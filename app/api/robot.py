from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.websocket import manager
from app.config import get_settings
from app.mqtt_service import mqtt_service
from app.state import robot_state, state_lock

router = APIRouter()
settings = get_settings()


class Command(BaseModel):
    command: Literal["forward", "backward", "left", "right", "stop", "horn"]
    speed: int = Field(default=180, ge=0, le=255)


@router.get("/config")
async def config():
    return {"camera_stream_url": settings.camera_stream_url}


@router.get("/telemetry")
async def get_telemetry():
    # Pastikan 'camera_url' dikirim ke frontend mengambil dari settings env
    return {
        "status": "online",
        "camera_url": settings.camera_stream_url, 
        # ... data telemetri robot lainnya seperti speed, direction, dll.
    }

@router.post("/command")
async def command(data: Command):
    if data.command == "left":
        data.command = "right"
    elif data.command == "right":
        data.command = "left"
    if not await mqtt_service.publish_command(data.command, data.speed):
        raise HTTPException(status_code=503, detail="Broker MQTT tidak terhubung")
    async with state_lock:
        robot_state["direction"] = data.command
        robot_state["speed"] = 0 if data.command == "stop" else data.speed
        snapshot = robot_state.copy()
    await manager.broadcast({"type": "telemetry", "data": snapshot})
    return {"ok": True, "command": data.model_dump()}
