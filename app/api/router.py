from fastapi import APIRouter

from app.api.robot import router as robot_router
from app.api.websocket import router as websocket_router

router = APIRouter()
router.include_router(robot_router, prefix="/api", tags=["robot"])
router.include_router(websocket_router, tags=["realtime"])
