#!/usr/bin/env python3
"""
Capture a test frame to determine chest bounding box coordinates.
Usage: python3 capture_test_frame.py
Then download test_frame.jpg and identify the chest region coordinates.
"""
import cv2

print("Opening camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Failed to open camera")
    exit(1)

print("Capturing frame...")
ret, frame = cap.read()

if ret:
    filename = "test_frame.jpg"
    cv2.imwrite(filename, frame)
    print(f"✓ Frame saved: {filename}")
    print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
    print(f"\nDownload this image and identify chest coordinates:")
    print(f"  scp user@rdk-ip:~/ISDN3000C_Project/{filename} .")
    print(f"\nThen use: python3 test_breathing_rdk.py --bbox X1,Y1,X2,Y2")
else:
    print("Failed to capture frame")

cap.release()
