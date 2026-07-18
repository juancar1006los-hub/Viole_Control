from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import router
from app.config import BASE_DIR, get_settings
from app.mqtt_service import mqtt_service

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    await mqtt_service.start()
    yield
    await mqtt_service.stop()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(router)
app.mount("/static", StaticFiles(directory=BASE_DIR / "app" / "static"), name="static")


@app.get("/", include_in_schema=False)
async def dashboard():
    return FileResponse(BASE_DIR / "app" / "templates" / "index.html")
