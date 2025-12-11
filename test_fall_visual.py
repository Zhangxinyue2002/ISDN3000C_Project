#!/usr/bin/env python3
"""
Visual test for fall detection with webcam display
Works with VNC viewer / X11 display

Usage:
    python3 test_fall_visual.py
"""

import cv2
import sys
import os
import time

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.fall_detector_pose import FallDetectorPose


def main():
    print("="*70)
    print(" "*15 + "🤖 Fall Detection Visual Test 🤖")
    print("="*70)
    print()
    
    # Initialize detector
    print("📥 Initializing YOLOv8 Pose detector...")
    try:
        detector = FallDetectorPose()
    except Exception as e:
        print(f"❌ Error initializing detector: {e}")
        return
    
    if not detector.model_loaded:
        print("❌ Model failed to load")
        return
    
    print("✅ Detector initialized successfully!")
    print()
    
    # Open webcam
    print("📹 Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open webcam")
        return
    
    # Set resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    print("✅ Webcam opened successfully!")
    print()
    print("="*70)
    print("🎯 Instructions:")
    print("="*70)
    print("   • Stand normally → Shows 'Standing' (Green)")
    print("   • Sit down → Shows 'Sitting' (Yellow)")
    print("   • Lie down flat → Shows 'FALL DETECTED!' (Red)")
    print("   • Press 'q' or 'ESC' to quit")
    print("="*70)
    print()
    
    # Stats
    frame_count = 0
    fall_count = 0
    person_count = 0
    fps_start = time.time()
    fps_counter = 0
    fps_display = 0
    
    window_name = 'Fall Detection Test - Press Q to Quit'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            frame_count += 1
            
            # Detect fall
            result = detector.detect_fall(frame)
            
            # Update stats
            if result['person_detected']:
                person_count += 1
            if result['fall_detected']:
                fall_count += 1
            
            # Calculate FPS
            fps_counter += 1
            if time.time() - fps_start > 1:
                fps_display = fps_counter
                fps_counter = 0
                fps_start = time.time()
            
            # Create display frame
            display_frame = frame.copy()
            h, w = display_frame.shape[:2]
            
            # Draw detection results
            if result['person_detected']:
                x1, y1, x2, y2 = result['bounding_box']
                
                # Choose color based on status
                if result['fall_detected']:
                    color = (0, 0, 255)  # Red for fall
                    status_text = "⚠️ FALL DETECTED!"
                    status_color = (0, 0, 255)
                elif result['class_label'] == 'standing':
                    color = (0, 255, 0)  # Green for standing
                    status_text = "✓ Standing"
                    status_color = (0, 255, 0)
                elif result['class_label'] == 'sitting':
                    color = (0, 255, 255)  # Yellow for sitting
                    status_text = "✓ Sitting"
                    status_color = (0, 200, 200)
                else:
                    color = (128, 128, 128)  # Gray
                    status_text = result['class_label']
                    status_color = (128, 128, 128)
                
                # Draw person bounding box
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 3)
                
                # Draw chest region (for breathing detection)
                if result['chest_bbox']:
                    cx1, cy1, cx2, cy2 = result['chest_bbox']
                    cv2.rectangle(display_frame, (cx1, cy1), (cx2, cy2), (255, 255, 0), 2)
                    cv2.putText(display_frame, "Chest ROI", (cx1, cy1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)
                
                # Draw confidence
                conf_text = f"Confidence: {result['confidence']:.2f}"
                cv2.putText(display_frame, conf_text, (x1, y1 - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Large status display at top
                status_y = 60
                cv2.putText(display_frame, status_text, (20, status_y),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, status_color, 3)
                
                # Flash effect for fall
                if result['fall_detected'] and frame_count % 10 < 5:
                    overlay = display_frame.copy()
                    cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 255), 30)
                    display_frame = cv2.addWeighted(overlay, 0.2, display_frame, 0.8, 0)
            
            else:
                # No person detected
                cv2.putText(display_frame, "No person detected", (20, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (128, 128, 128), 3)
            
            # Info panel background
            info_bg = display_frame.copy()
            cv2.rectangle(info_bg, (0, 0), (w, 150), (0, 0, 0), -1)
            display_frame = cv2.addWeighted(info_bg, 0.5, display_frame, 0.5, 0)
            
            # Display stats
            y_offset = 100
            cv2.putText(display_frame, f"FPS: {fps_display}", (20, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Inference: {result['inference_time']:.1f}ms", 
                       (20, y_offset + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            cv2.putText(display_frame, f"Frames: {frame_count}", (w - 200, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Falls: {fall_count}", (w - 200, y_offset + 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow(window_name, display_frame)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q') or key == 27:  # q, Q, or ESC
                break
            elif key == ord('s') or key == ord('S'):  # Save screenshot
                filename = f'fall_detection_screenshot_{frame_count}.jpg'
                cv2.imwrite(filename, display_frame)
                print(f"📸 Screenshot saved: {filename}")
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    # Final summary
    print()
    print("="*70)
    print("📊 Test Summary:")
    print("="*70)
    print(f"   Total frames: {frame_count}")
    print(f"   People detected: {person_count}")
    print(f"   Falls detected: {fall_count}")
    if frame_count > 0:
        print(f"   Person rate: {(person_count/frame_count*100):.1f}%")
        print(f"   Fall rate: {(fall_count/frame_count*100):.1f}%")
    print("="*70)
    print()
    print("✨ Test complete!")


if __name__ == '__main__':
    main()
