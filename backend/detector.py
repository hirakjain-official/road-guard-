"""
Vehicle detector — YOLOv8 primary, motion-based fallback for demo video.
Speed is calculated when any tracked vehicle crosses Line1 then Line2.
"""

import math
import time
from dataclasses import dataclass, field
from typing import Optional

import cv2
import numpy as np


@dataclass
class TrackedVehicle:
    vid: int
    cx: float
    cy: float
    line1_time: Optional[float] = None
    line2_crossed: bool = False
    last_seen: float = field(default_factory=time.time)


class VehicleDetector:
    def __init__(self, config: dict):
        self.config = config
        self.model = None
        self._load_model()
        self.tracked: dict[int, TrackedVehicle] = {}
        self._next_id = 0
        self.last_speed: Optional[float] = None
        self._bg_sub = cv2.createBackgroundSubtractorMOG2(history=30, varThreshold=40)

    def _load_model(self):
        try:
            from ultralytics import YOLO
            self.model = YOLO('yolov8n.pt')
            print('[Detector] YOLOv8n loaded')
        except Exception as e:
            print(f'[Detector] YOLO unavailable ({e}) — using motion detection fallback')
            self.model = None

    def update_config(self, config: dict):
        self.config = config

    def _line_ys(self, h: int) -> tuple[int, int]:
        return int(h * self.config['line1_pct']), int(h * self.config['line2_pct'])

    def process(self, frame: np.ndarray) -> tuple[np.ndarray, int, Optional[float], bool]:
        """Returns (annotated_frame, vehicle_count, speed_if_new, overspeeding)."""
        h, w = frame.shape[:2]
        l1, l2 = self._line_ys(h)
        out = frame.copy()

        # Draw trigger lines
        cv2.line(out, (0, l1), (w, l1), (34, 197, 94), 2)
        cv2.putText(out, 'LINE 1', (8, l1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (34, 197, 94), 1)
        cv2.line(out, (0, l2), (w, l2), (239, 68, 68), 2)
        cv2.putText(out, 'LINE 2', (8, l2 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (239, 68, 68), 1)

        detections = self._detect(frame)
        speed_this_frame: Optional[float] = None
        overspeeding = False

        now = time.time()
        for (x1, y1, x2, y2) in detections:
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            vid = self._match(cx, cy)
            v = self.tracked[vid]
            v.cx, v.cy, v.last_seen = cx, cy, now

            # Line 1 crossing band ±25px
            if v.line1_time is None and abs(cy - l1) < 25:
                v.line1_time = now

            # Line 2 crossing — calculate speed
            if v.line1_time and not v.line2_crossed and abs(cy - l2) < 25:
                elapsed = now - v.line1_time
                if elapsed > 0.05:
                    px_dist = abs(l2 - l1)
                    speed = (px_dist / elapsed) * self.config['pixel_speed_mult']
                    speed_this_frame = speed
                    self.last_speed = speed
                    overspeeding = speed > self.config['speed_limit']
                    v.line2_crossed = True

            spd = self.last_speed if v.line2_crossed else None
            color = (239, 68, 68) if (v.line2_crossed and overspeeding) else (34, 197, 94)
            cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
            label = f'{spd:.0f} km/h' if spd else 'Vehicle'
            cv2.putText(out, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Prune stale tracks
        for vid in [k for k, v in self.tracked.items() if now - v.last_seen > 3.0]:
            del self.tracked[vid]

        return out, len(detections), speed_this_frame, overspeeding

    def _detect(self, frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        """Return list of (x1,y1,x2,y2) bboxes — YOLO if available, else motion."""
        if self.model is not None:
            return self._yolo_detect(frame)
        return self._motion_detect(frame)

    def _yolo_detect(self, frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        results = self.model(
            frame,
            classes=[2, 3, 5, 7],
            conf=self.config.get('confidence', 0.4),
            verbose=False,
        )
        boxes = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes.append((x1, y1, x2, y2))
        return boxes

    def _motion_detect(self, frame: np.ndarray) -> list[tuple[int, int, int, int]]:
        """Background-subtraction fallback — works great with demo video."""
        mask = self._bg_sub.apply(frame)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
        mask = cv2.dilate(mask, np.ones((15, 15), np.uint8))
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        boxes = []
        for c in contours:
            if cv2.contourArea(c) < 800:
                continue
            x, y, bw, bh = cv2.boundingRect(c)
            boxes.append((x, y, x + bw, y + bh))
        return boxes

    def _match(self, cx: float, cy: float) -> int:
        best_id, best_dist = None, 150.0
        for vid, v in self.tracked.items():
            d = math.hypot(cx - v.cx, cy - v.cy)
            if d < best_dist:
                best_dist, best_id = d, vid
        if best_id is None:
            best_id = self._next_id
            self._next_id += 1
            self.tracked[best_id] = TrackedVehicle(vid=best_id, cx=cx, cy=cy)
        return best_id
