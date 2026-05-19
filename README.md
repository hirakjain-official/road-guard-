# road guard

AI-powered speed enforcement system. uses webcam + computer vision to detect vehicles, calculate speeds, and trigger automated voice call alerts when speed limits are exceeded.

built as a proof-of-concept intelligent traffic monitoring system.

## what it does

- detects vehicles using YOLOv8 nano (works on CPU)
- tracks vehicles across two trigger lines to calculate speed
- fires AI voice calls via Vapi when overspeeding detected
- real-time dashboard with live feed, speed display, alert log
- configurable speed limits, cooldown timers, detection zones

## demo

*(add screenshots here)*

recommended images:
1. **main dashboard** - full UI showing video feed + speed display + alerts
2. **vehicle detection** - annotated frame with bounding boxes and trigger lines
3. **alert triggered** - dashboard during an overspeeding event
4. **config panel** - sidebar showing all the tunable parameters

## tech stack

**backend:**
- FastAPI (REST + WebSocket)
- OpenCV (video capture + annotation)
- YOLOv8 nano (vehicle detection)
- Vapi API (AI voice calls)

**frontend:**
- React + TypeScript
- Tailwind CSS
- WebSocket (real-time updates)
- MJPEG stream (live video)

**deployment:**
- runs locally on webcam
- demo mode available with generated video

## quick start

### prerequisites

- Python 3.8+ with pip
- Node.js 16+ with npm
- webcam (or use demo video)
- Vapi account for voice calls (optional for testing)

### setup

1. **clone repo**
```bash
git clone https://github.com/hirakjain-official/road-guard-.git
cd road-guard-
```

2. **install dependencies**

windows:
```bash
setup.bat
```

manual:
```bash
# backend
cd backend
pip install -r requirements.txt

# frontend
cd ../frontend
npm install
```

3. **configure Vapi (optional)**

copy `backend/.env.example` to `backend/.env`:
```bash
VAPI_API_KEY=your_vapi_api_key_here
VAPI_PHONE_NUMBER_ID=your_vapi_phone_number_id_here
ALERT_RECIPIENT_NUMBER=+1234567890
```

skip this if you just want to test detection without calls.

4. **run**

windows:
```bash
start.bat
```

manual:
```bash
# terminal 1 - backend
cd backend
python main.py

# terminal 2 - frontend
cd frontend
npm run dev
```

open http://localhost:5173

## how it works

1. **vehicle detection** - YOLOv8 runs inference on each frame, filters for vehicles (car, truck, bus, motorcycle)

2. **tracking** - assigns persistent IDs to detections across frames using IoU matching

3. **speed calculation** - when a vehicle crosses LINE 1 then LINE 2, speed = (pixel_distance / time_elapsed) × multiplier

4. **alert trigger** - if speed > limit AND cooldown expired, fires Vapi call with alert message

5. **cooldown** - prevents spam by enforcing minimum time between calls (default 30s)

## demo mode

includes a demo video generator for testing without a webcam:

```bash
cd backend
python gen_demo_video.py
```

this creates `demo_car.mp4` with a car moving through the frame. set `VIDEO_SOURCE=demo_car.mp4` in backend main.py or via the UI source switcher.

## configuration

tune these in the UI sidebar:

- **speed limit** - threshold for overspeeding (km/h)
- **speed multiplier** - calibration factor (tune until toy car reads ~80 km/h)
- **cooldown** - minimum seconds between calls
- **line positions** - trigger line Y coordinates (%)
- **YOLO confidence** - detection threshold (0.1-0.9)
- **call on any detection** - demo mode, triggers call whenever car crosses lines (ignores speed)

## architecture

```
┌─────────────┐      WebSocket      ┌──────────────┐
│   React     │◄────────────────────►│   FastAPI    │
│  Frontend   │                      │   Backend    │
└─────────────┘                      └──────────────┘
       │                                    │
       │ MJPEG stream                       │
       │◄───────────────────────────────────┤
                                            │
                                   ┌────────▼────────┐
                                   │  OpenCV Capture │
                                   │  YOLOv8 Detect  │
                                   │  Speed Calc     │
                                   └─────────────────┘
                                            │
                                   ┌────────▼────────┐
                                   │   Vapi Client   │
                                   │  (voice calls)  │
                                   └─────────────────┘
```

## api endpoints

**REST:**
- `GET /config` - get current config
- `PUT /config` - update config
- `GET /stream` - MJPEG video stream
- `POST /source` - switch video source (webcam/file)

**WebSocket:**
- `WS /ws` - real-time status + alerts + config updates

## known limitations

- speed calculation is simulated (pixel-based, not actual physics)
- works best with birds-eye view angle
- requires tuning multiplier per camera setup
- YOLOv8 nano is fast but less accurate than larger models
- no persistent storage (alerts reset on restart)

## future improvements

- add license plate recognition
- database for alert history
- multi-camera support
- actual speed calculation using camera calibration
- web deployment for remote monitoring
- SMS/email alerts in addition to calls

## contributing

this was built as a hackathon project / proof-of-concept. feel free to fork and extend it. PRs welcome for bug fixes or feature additions.

## credits

built by [Hirak Jain](https://github.com/hirakjain-official)

uses:
- [YOLOv8](https://github.com/ultralytics/ultralytics) for detection
- [Vapi](https://vapi.ai) for AI voice calls
- [FastAPI](https://fastapi.tiangolo.com/) for backend
- [React](https://react.dev/) + [Tailwind](https://tailwindcss.com/) for frontend

## license

MIT - use it however you want.
