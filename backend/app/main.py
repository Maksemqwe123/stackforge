from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, generate_latest
from starlette.responses import Response

from app.api import auth, deployments, stacks, ws
from app.database import Base, engine
from app.models import models as _models  # noqa: F401 — register ORM metadata

REQUESTS = Counter("stackforge_http_requests_total", "HTTP requests", ["path"])


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="StackForge", version="0.4.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(stacks.router, prefix="/api/v1")
app.include_router(deployments.router, prefix="/api/v1")
app.include_router(ws.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "stackforge-api"}


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain; version=0.0.4")
