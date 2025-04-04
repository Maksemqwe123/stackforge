from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models import DeployStatus, Deployment, Stack, User
from app.schemas import DeploymentOut
from app.workers.tasks import run_deployment

router = APIRouter(prefix="/deployments", tags=["deployments"])


@router.post("/stack/{stack_id}", response_model=DeploymentOut, status_code=202)
async def trigger_deploy(
    stack_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Stack).where(Stack.id == stack_id, Stack.owner_id == user.id))
    stack = result.scalar_one_or_none()
    if not stack:
        raise HTTPException(status_code=404, detail="stack not found")

    deployment = Deployment(stack_id=stack.id, status=DeployStatus.pending, logs="queued\n")
    db.add(deployment)
    await db.commit()
    await db.refresh(deployment)
    run_deployment.delay(deployment.id)
    return deployment


@router.get("/stack/{stack_id}", response_model=list[DeploymentOut])
async def list_deployments(
    stack_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Deployment)
        .join(Stack)
        .where(Stack.id == stack_id, Stack.owner_id == user.id)
        .order_by(Deployment.created_at.desc())
    )
    return result.scalars().all()
