import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
    """Konfigurasi aplikasi yang dibaca sekali saat server mulai."""

    app_name: str = "Robot 4-Wheel Control Center"
    camera_stream_url: str = os.getenv("CAMERA_STREAM_URL", "http://192.168.100.24:81/stream")
    mqtt_host: str = os.getenv("MQTT_HOST", "103.197.188.199")
    mqtt_port: int = int(os.getenv("MQTT_PORT", "1883"))
    mqtt_username: str = os.getenv("MQTT_USERNAME", "nexaryn")
    mqtt_password: str = os.getenv("MQTT_PASSWORD", "31750321")
    mqtt_control_topic: str = os.getenv("MQTT_CONTROL_TOPIC", "robot/control")
    mqtt_telemetry_topic: str = os.getenv("MQTT_TELEMETRY_TOPIC", "robot/telemetry")


@lru_cache
def get_settings() -> Settings:
    return Settings()
