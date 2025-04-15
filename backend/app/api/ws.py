import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from app.config import settings

router = APIRouter()


@router.websocket("/deployments/{deployment_id}")
async def deployment_logs(ws: WebSocket, deployment_id: int):
    await ws.accept()
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    channel = f"deploy:{deployment_id}"
    pubsub = redis.pubsub()
    await pubsub.subscribe(channel)
    try:
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
            if message and message.get("data"):
                await ws.send_text(str(message["data"]))
            await asyncio.sleep(0.05)
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await redis.close()
