import asyncio

robot_state = {
    "battery": None,
    "distance": None,
    "temperature": None,
    "speed": 0,
    "direction": "stop",
    "status": "waiting",
    "updated_at": None,
}
state_lock = asyncio.Lock()
