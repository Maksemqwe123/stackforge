import subprocess
from datetime import datetime, timezone

from redis import Redis
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.config import settings
from app.models import DeployStatus, Deployment, Stack
from app.workers.celery_app import celery_app

engine = create_engine(settings.database_url_sync)


def _publish(deployment_id: int, line: str) -> None:
    Redis.from_url(settings.redis_url).publish(f"deploy:{deployment_id}", line)


@celery_app.task(name="run_deployment")
def run_deployment(deployment_id: int) -> None:
    with Session(engine) as db:
        deployment = db.get(Deployment, deployment_id)
        if not deployment:
            return
        stack = db.get(Stack, deployment.stack_id)
        deployment.status = DeployStatus.running
        db.commit()
        _publish(deployment_id, "starting docker compose up\n")

        try:
            proc = subprocess.run(
                ["docker", "compose", "-f", stack.compose_path, "up", "-d"],
                capture_output=True,
                text=True,
                timeout=120,
            )
            output = (proc.stdout or "") + (proc.stderr or "")
            deployment.logs += output
            deployment.status = DeployStatus.success if proc.returncode == 0 else DeployStatus.failed
            _publish(deployment_id, output or f"exit code {proc.returncode}\n")
        except Exception as exc:  # noqa: BLE001
            deployment.logs += str(exc) + "\n"
            deployment.status = DeployStatus.failed
            _publish(deployment_id, f"error: {exc}\n")
        finally:
            deployment.finished_at = datetime.now(timezone.utc)
            db.commit()
            _publish(deployment_id, f"[done] status={deployment.status.value}\n")
