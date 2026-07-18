# Robot Control Center (MQTT)

Kontrol robot dan telemetry memakai MQTT. ESP32-CAM tetap memberi stream MJPEG langsung pada `CAMERA_STREAM_URL`.

## Konfigurasi

1. Jalankan broker MQTT (Mosquitto/EMQX) pada alamat yang dapat dijangkau PC dan ESP32.
2. Salin `.env.example` menjadi `.env`, lalu isi alamat broker dan stream kamera.
3. Samakan `MQTT_HOST`, kredensial, serta nama topic di backend dan firmware ESP32 utama.

## Topic

| Topic | Arah | Payload |
| --- | --- | --- |
| `robot/control` | Backend → ESP32 | `{"command":"forward","speed":180}` |
| `robot/telemetry` | ESP32 → Backend | `{"speed":180,"direction":"forward","status":"online"}` |

## Menjalankan backend

```powershell
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
