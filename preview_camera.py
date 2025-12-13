#!/usr/bin/env python3
"""
Camera Preview Tool
Shows what the camera sees and saves test frames.
Helps you position the camera and person correctly.

Usage:
    python3 preview_camera.py [--save]
    
Options:
    --save    Save frame to test_preview.jpg
"""
import cv2
import sys

def main():
    save_mode = '--save' in sys.argv
    
    print("="*60)
    print("CAMERA PREVIEW TOOL")
    print("="*60)
    
    print("\nOpening camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Failed to open camera")
        return 1
    
    print("✓ Camera opened")
    
    # Capture multiple frames
    print("\nCapturing frames...")
    frames_captured = 0
    
    for i in range(10):
        ret, frame = cap.read()
        if ret:
            frames_captured += 1
            if i == 0:
                # Save first frame
                filename = "test_preview.jpg"
                cv2.imwrite(filename, frame)
                print(f"✓ Frame saved: {filename}")
                print(f"  Resolution: {frame.shape[1]}x{frame.shape[0]}")
                
                # Show brightness stats
                import numpy as np
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray)
                print(f"  Average brightness: {brightness:.1f}/255")
                
                if brightness < 30:
                    print("  ⚠️  Very dark - need more lighting")
                elif brightness < 80:
                    print("  ⚠️  Dim - could use better lighting")
                else:
                    print("  ✓ Good lighting")
    
    cap.release()
    
    print(f"\n✓ Captured {frames_captured}/10 frames successfully")
    
    if frames_captured > 0:
        print("\n📋 Next steps:")
        print("1. Download the test image:")
        print("   scp user@rdk-ip:~/ISDN3000C_Project/test_preview.jpg .")
        print("\n2. Check if person is visible in the image")
        print("\n3. If person is visible:")
        print("   - Run breathing test: python3 test_breathing_rdk.py")
        print("\n4. If no person visible:")
        print("   - Adjust camera position")
        print("   - Make sure person is in frame")
        print("   - Re-run this preview tool")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
