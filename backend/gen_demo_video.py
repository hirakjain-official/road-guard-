"""
Generates demo_car.mp4 — a simple looping video of a car rectangle
moving top-to-bottom across the frame, triggering Line 1 then Line 2.
Run once: python gen_demo_video.py
"""

import cv2
import numpy as np

W, H = 640, 480
FPS = 30
DURATION_SEC = 6
OUT_PATH = 'demo_car.mp4'

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
writer = cv2.VideoWriter(OUT_PATH, fourcc, FPS, (W, H))

TOTAL_FRAMES = FPS * DURATION_SEC

# Car dimensions
CAR_W, CAR_H = 120, 70

for i in range(TOTAL_FRAMES):
    frame = np.full((H, W, 3), (20, 20, 30), dtype=np.uint8)

    # Road markings
    for y in range(0, H, 40):
        cv2.line(frame, (W // 2, y), (W // 2, min(y + 20, H)), (60, 60, 60), 2)

    # Trigger lines
    l1 = int(H * 0.35)
    l2 = int(H * 0.65)
    cv2.line(frame, (0, l1), (W, l1), (34, 197, 94), 2)
    cv2.putText(frame, 'LINE 1', (8, l1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (34, 197, 94), 1)
    cv2.line(frame, (0, l2), (W, l2), (239, 68, 68), 2)
    cv2.putText(frame, 'LINE 2', (8, l2 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (239, 68, 68), 1)

    # Car position — enters from top, exits at bottom
    t = i / TOTAL_FRAMES
    car_y = int(-CAR_H + (H + CAR_H) * t)
    car_x = W // 2 - CAR_W // 2

    # Car body
    cv2.rectangle(frame, (car_x, car_y), (car_x + CAR_W, car_y + CAR_H), (50, 120, 220), -1)
    cv2.rectangle(frame, (car_x, car_y), (car_x + CAR_W, car_y + CAR_H), (100, 160, 255), 2)
    # Windshield
    cv2.rectangle(frame, (car_x + 15, car_y + 8), (car_x + CAR_W - 15, car_y + 35), (150, 200, 255), -1)
    # Wheels
    for wx, wy in [(car_x + 10, car_y + CAR_H), (car_x + CAR_W - 10, car_y + CAR_H)]:
        cv2.circle(frame, (wx, wy), 12, (40, 40, 40), -1)
        cv2.circle(frame, (wx, wy), 12, (80, 80, 80), 2)

    # Label
    cv2.putText(frame, 'DEMO CAR', (car_x, car_y - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

    writer.write(frame)

writer.release()
print(f'Demo video written to {OUT_PATH}  ({TOTAL_FRAMES} frames @ {FPS}fps)')
