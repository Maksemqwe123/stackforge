from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.database import get_db
from app.models import Stack, User
from app.schemas import StackCreate, StackOut

router = APIRouter(prefix="/stacks", tags=["stacks"])


@router.get("", response_model=list[StackOut])
async def list_stacks(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Stack).where(Stack.owner_id == user.id))
    return result.scalars().all()


@router.post("", response_model=StackOut, status_code=201)
async def create_stack(
    body: StackCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    stack = Stack(name=body.name, compose_path=body.compose_path, owner_id=user.id)
    db.add(stack)
    await db.commit()
    await db.refresh(stack)
    return stack


@router.get("/{stack_id}", response_model=StackOut)
async def get_stack(stack_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Stack).where(Stack.id == stack_id, Stack.owner_id == user.id))
    stack = result.scalar_one_or_none()
    if not stack:
        raise HTTPException(status_code=404, detail="not found")
    return stack
