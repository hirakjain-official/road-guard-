"""Road Guard — FastAPI backend
Routes:
  GET  /stream   — MJPEG video stream
  WS   /ws       — JSON updates (status + alerts)
  GET  /config   — current config
  PUT  /config   — update config
"""

import asyncio
import os
import threading
import time
import uuid
from contextlib import asynccontextmanager
from typing import Optional

import cv2
import numpy as np
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from detector import VehicleDetector
from vapi_client import VapiClient

load_dotenv()

# ── Video source ──────────────────────────────────────────────────────────────
# Set VIDEO_SOURCE in .env to a file path for demo video, leave blank for webcam
VIDEO_SOURCE_ENV = os.getenv('VIDEO_SOURCE', '')
VIDEO_SOURCE: int | str = VIDEO_SOURCE_ENV if VIDEO_SOURCE_ENV else 0

# ── Default config ────────────────────────────────────────────────────────────
DEFAULT_CONFIG = {
    'speed_limit': 60,
    'pixel_speed_mult': 0.5,   # tune this so demo car reads ~80 km/h
    'cooldown_seconds': 30,
    'line1_pct': 0.35,
    'line2_pct': 0.65,
    'confidence': 0.4,
    'call_on_any_detection': True,  # True = call whenever car crosses lines, ignoring speed
}

# ── Shared state ──────────────────────────────────────────────────────────────
state_lock = threading.Lock()
app_state: dict = {
    'frame': None,
    'speed': None,
    'overspeeding': False,
    'vehicles_count': 0,
    'alert_active': False,
    'alert_active_until': 0.0,
    'alerts': [],
    'config': dict(DEFAULT_CONFIG),
}

stop_event = threading.Event()
vapi = VapiClient()

# Hot-switchable video source — write to this to change source without restart
current_source: list = [VIDEO_SOURCE]  # list so it's mutable from outside the loop


# ── Capture loop ──────────────────────────────────────────────────────────────
def capture_loop():
    source = current_source[0]
    cap = cv2.VideoCapture(source)
    is_video_file = isinstance(source, str) and source != ''
    print(f'[Camera] Source: {"file: " + str(source) if is_video_file else "webcam"} | Opened: {cap.isOpened()}')

    with state_lock:
        cfg = dict(app_state['config'])
    detector = VehicleDetector(cfg)

    while not stop_event.is_set():
        # Hot-switch: if source changed, reopen capture
        if current_source[0] != source:
            cap.release()
            source = current_source[0]
            cap = cv2.VideoCapture(source)
            is_video_file = isinstance(source, str) and source != ''
            detector.tracked.clear()
            detector.last_speed = None
            with state_lock:
                app_state['speed'] = None
            print(f'[Camera] Switched to: {"file: " + str(source) if is_video_file else "webcam"} | Opened: {cap.isOpened()}')

        ret, frame = cap.read()

        # Loop video file when it ends
        if not ret and is_video_file:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            detector.tracked.clear()
            detector.last_speed = None
            with state_lock:
                app_state['speed'] = None
            ret, frame = cap.read()

        if not ret:
            time.sleep(0.05)
            continue

        with state_lock:
            cfg = dict(app_state['config'])

        detector.update_config(cfg)
        annotated, count, speed, overspeeding = detector.process(frame)
        now = time.time()

        with state_lock:
            app_state['frame'] = annotated
            app_state['vehicles_count'] = count

            call_on_any = cfg.get('call_on_any_detection', True)

            if speed is not None:
                app_state['speed'] = speed
                app_state['overspeeding'] = overspeeding

                # Trigger call: always (demo mode) OR only when overspeeding
                should_call = overspeeding if not call_on_any else True

                if should_call:
                    vapi.set_cooldown(cfg['cooldown_seconds'])
                    call_status = vapi.trigger_call(speed)

                    alert = {
                        'id': str(uuid.uuid4()),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'speed': round(speed, 1),
                        'callStatus': call_status,
                    }
                    app_state['alerts'] = ([alert] + app_state['alerts'])[:50]

                    if call_status == 'triggered':
                        app_state['alert_active'] = True
                        app_state['alert_active_until'] = now + 3.0

            if app_state['alert_active'] and now > app_state['alert_active_until']:
                app_state['alert_active'] = False

    cap.release()


# ── Lifespan ──────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(_: FastAPI):
    t = threading.Thread(target=capture_loop, daemon=True)
    t.start()
    yield
    stop_event.set()
    t.join(timeout=3)


app = FastAPI(lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])


# ── Config ────────────────────────────────────────────────────────────────────
class ConfigUpdate(BaseModel):
    speed_limit: Optional[float] = None
    pixel_speed_mult: Optional[float] = None
    cooldown_seconds: Optional[int] = None
    line1_pct: Optional[float] = None
    line2_pct: Optional[float] = None
    confidence: Optional[float] = None
    call_on_any_detection: Optional[bool] = None


class SourceUpdate(BaseModel):
    source: str  # "0" for webcam, or a file path


@app.post('/source')
def set_source(body: SourceUpdate):
    new = int(body.source) if body.source.isdigit() else body.source
    current_source[0] = new
    return {'source': str(new)}


@app.get('/source')
def get_source():
    return {'source': str(current_source[0])}


@app.get('/config')
def get_config():
    with state_lock:
        return dict(app_state['config'])


@app.put('/config')
def put_config(u: ConfigUpdate):
    with state_lock:
        cfg = app_state['config']
        if u.speed_limit is not None: cfg['speed_limit'] = u.speed_limit
        if u.pixel_speed_mult is not None: cfg['pixel_speed_mult'] = u.pixel_speed_mult
        if u.cooldown_seconds is not None: cfg['cooldown_seconds'] = u.cooldown_seconds
        if u.line1_pct is not None: cfg['line1_pct'] = u.line1_pct
        if u.line2_pct is not None: cfg['line2_pct'] = u.line2_pct
        if u.confidence is not None: cfg['confidence'] = u.confidence
        if u.call_on_any_detection is not None: cfg['call_on_any_detection'] = u.call_on_any_detection
        return dict(cfg)


# ── MJPEG stream ──────────────────────────────────────────────────────────────
def _blank_frame(w: int = 640, h: int = 480) -> np.ndarray:
    f = np.zeros((h, w, 3), dtype=np.uint8)
    cv2.putText(f, 'Road Guard — starting...', (60, h // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (80, 80, 80), 2)
    return f


@app.get('/stream')
async def stream():
    async def generate():
        while True:
            with state_lock:
                frame = app_state.get('frame')
            out = frame if frame is not None else _blank_frame()
            _, buf = cv2.imencode('.jpg', out, [cv2.IMWRITE_JPEG_QUALITY, 82])
            yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'
                   + buf.tobytes() + b'\r\n')
            await asyncio.sleep(1 / 30)

    return StreamingResponse(generate(), media_type='multipart/x-mixed-replace; boundary=frame')


# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket('/ws')
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(0.1)
            with state_lock:
                cfg = app_state['config']
                payload = {
                    'status': {
                        'speed': app_state['speed'],
                        'overspeeding': app_state['overspeeding'],
                        'vehiclesDetected': app_state['vehicles_count'],
                        'cooldownRemaining': vapi.cooldown_remaining(),
                        'alertActive': app_state['alert_active'],
                    },
                    'alerts': list(app_state['alerts']),
                    'config': {
                        'speedLimit': cfg['speed_limit'],
                        'pixelSpeedMult': cfg['pixel_speed_mult'],
                        'cooldownSeconds': cfg['cooldown_seconds'],
                        'line1Pct': cfg['line1_pct'],
                        'line2Pct': cfg['line2_pct'],
                        'confidence': cfg['confidence'],
                        'callOnAnyDetection': cfg.get('call_on_any_detection', True),
                    },
                }
            await websocket.send_json(payload)
    except WebSocketDisconnect:
        pass


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000, log_level='info')
