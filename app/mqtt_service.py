import asyncio
import json
import time
import uuid

from gmqtt import Client as MQTTClient

from app.api.websocket import manager
from app.config import get_settings
from app.state import robot_state, state_lock


class MQTTService:
    def __init__(self):
        self.settings = get_settings()
        self.client = MQTTClient(f"robot-backend-{uuid.uuid4().hex[:8]}")
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.connected = False

    async def start(self):
        if self.settings.mqtt_username:
            self.client.set_auth_credentials(self.settings.mqtt_username, self.settings.mqtt_password)
        try:
            await self.client.connect(self.settings.mqtt_host, self.settings.mqtt_port)
        except Exception:
            self.connected = False

    async def stop(self):
        if self.connected:
            await self.client.disconnect()

    def _on_connect(self, client, flags, rc, properties):
        self.connected = True
        client.subscribe(self.settings.mqtt_telemetry_topic, qos=1)

    def _on_disconnect(self, client, packet, exc=None):
        self.connected = False

    def _on_message(self, client, topic, payload, qos, properties):
        if topic != self.settings.mqtt_telemetry_topic:
            return
        try:
            data = json.loads(payload.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return
        asyncio.create_task(self._apply_telemetry(data))

    async def _apply_telemetry(self, data):
        allowed = {"battery", "distance", "temperature", "speed", "direction", "status"}
        async with state_lock:
            robot_state.update({key: value for key, value in data.items() if key in allowed})
            robot_state["status"] = data.get("status", "online")
            robot_state["updated_at"] = int(time.time())
            snapshot = robot_state.copy()
        await manager.broadcast({"type": "telemetry", "data": snapshot})

    def publish_command(self, command, speed):
        if not self.connected:
            return False
        self.client.publish(self.settings.mqtt_control_topic, json.dumps({"command": command, "speed": speed}), qos=1)
        return True


mqtt_service = MQTTService()
