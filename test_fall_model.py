#!/usr/bin/env python3
"""
Quick test script for the YOLOv8 Pose fall detector

This script lets you quickly test the fall detection model with your webcam
before integrating it into the main system.

Usage:
    python3 test_fall_model.py
    python3 test_fall_model.py --headless  (for systems without display)
    python3 test_fall_model.py --image path/to/image.jpg  (test with image)
"""

import cv2
import sys
import os
import argparse

# Force headless mode for OpenCV to avoid Qt/X11 issues
os.environ['QT_QPA_PLATFORM'] = 'offscreen'

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.fall_detector_pose import FallDetectorPose
import time


def test_with_image(detector, image_path):
    """Test detector with a single image"""
    print(f"📷 Testing with image: {image_path}")
    
    frame = cv2.imread(image_path)
    if frame is None:
        print(f"❌ Cannot read image: {image_path}")
        return
    
    print("✅ Image loaded successfully!")
    print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
    print()
    
    # Detect
    print("🔍 Running detection...")
    result = detector.detect_fall(frame)
    
    # Display results
    print("="*70)
    print("📊 Detection Results:")
    print("="*70)
    print(f"   Person detected: {result['person_detected']}")
    if result['person_detected']:
        print(f"   Fall detected: {'⚠️  YES' if result['fall_detected'] else '✓ NO'}")
        print(f"   Class: {result['class_label']}")
        print(f"   Confidence: {result['confidence']:.3f}")
        print(f"   Bounding box: {result['bounding_box']}")
        print(f"   Chest region: {result['chest_bbox']}")
        print(f"   Inference time: {result['inference_time']:.1f}ms")
    print("="*70)
    print()
    
    # Save visualization
    if result['person_detected']:
        x1, y1, x2, y2 = result['bounding_box']
        color = (0, 0, 255) if result['fall_detected'] else (0, 255, 0)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
        
        if result['chest_bbox']:
            cx1, cy1, cx2, cy2 = result['chest_bbox']
            cv2.rectangle(frame, (cx1, cy1), (cx2, cy2), (255, 255, 0), 2)
        
        text = f"{result['class_label']} ({result['confidence']:.2f})"
        cv2.putText(frame, text, (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
        
        output_path = 'test_fall_detection_result.jpg'
        cv2.imwrite(output_path, frame)
        print(f"💾 Visualization saved to: {output_path}")
    
    print("✨ Test complete!")


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Test YOLOv8 Pose Fall Detector')
    parser.add_argument('--headless', action='store_true',
                       help='Run without display (capture only, no window)')
    parser.add_argument('--image', type=str,
                       help='Test with a single image instead of webcam')
    parser.add_argument('--frames', type=int, default=100,
                       help='Number of frames to capture in headless mode (default: 100)')
    args = parser.parse_args()
    
    print("="*70)
    print(" "*15 + "🤖 Fall Detection Model Test 🤖")
    print("="*70)
    print()
    
    # Initialize detector
    print("📥 Initializing YOLOv8 Pose detector...")
    print("   (First run will download model ~6MB - please wait)")
    print()
    
    try:
        detector = FallDetectorPose()
    except Exception as e:
        print(f"❌ Error initializing detector: {e}")
        print()
        print("💡 Try installing ultralytics:")
        print("   pip install ultralytics")
        return
    
    if not detector.model_loaded:
        print("❌ Model failed to load")
        return
    
    print("✅ Detector initialized successfully!")
    print()
    
    # Show model info
    print("📊 Model Information:")
    info = detector.get_model_info()
    for key, value in info.items():
        print(f"   • {key}: {value}")
    print()
    
    # If testing with image, use different function
    if args.image:
        test_with_image(detector, args.image)
        return
    
    # Open webcam
    print("📹 Opening webcam...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open webcam")
        print("💡 Make sure your camera is connected and not in use")
        return
    
    print("✅ Webcam opened successfully!")
    print()
    
    if args.headless:
        print("="*70)
        print("🎯 Headless Mode (No Display):")
        print("="*70)
        print(f"   Will capture {args.frames} frames and save detections")
        print("   Press Ctrl+C to stop early")
        print("="*70)
        print()
    else:
        print("="*70)
        print("🎯 Test Instructions:")
        print("="*70)
        print("1. Stand normally → Should detect 'standing'")
        print("2. Sit down → Should detect 'sitting'")
        print("3. Lie down flat → Should detect 'FALL'")
        print("4. Press 'q' to quit")
        print("="*70)
        print()
    
    # Stats
    frame_count = 0
    fall_count = 0
    person_count = 0
    fps_start = time.time()
    fps_counter = 0
    fps_display = 0
    max_frames = args.frames if args.headless else float('inf')
    
    # Save detections in headless mode
    detections = []
    
    try:
        while frame_count < max_frames:
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
                detections.append({
                    'frame': frame_count,
                    'time': time.time(),
                    'confidence': result['confidence'],
                    'bbox': result['bounding_box']
                })
            
            # Print progress in headless mode
            if args.headless:
                if frame_count % 10 == 0:
                    print(f"📊 Frame {frame_count}/{max_frames} | "
                          f"Falls: {fall_count} | People: {person_count}", end='\r')
            
            # Calculate FPS
            fps_counter += 1
            if time.time() - fps_start > 1:
                fps_display = fps_counter
                fps_counter = 0
                fps_start = time.time()
            
            # Skip visualization in headless mode
            if args.headless:
                continue
            
            # Draw visualization
            display_frame = frame.copy()
            
            if result['person_detected']:
                x1, y1, x2, y2 = result['bounding_box']
                
                # Choose color
                if result['fall_detected']:
                    color = (0, 0, 255)  # Red
                    status_text = "⚠️  FALL DETECTED!"
                elif result['class_label'] == 'standing':
                    color = (0, 255, 0)  # Green
                    status_text = "✓ Standing"
                elif result['class_label'] == 'sitting':
                    color = (0, 255, 255)  # Yellow
                    status_text = "✓ Sitting"
                else:
                    color = (128, 128, 128)  # Gray
                    status_text = result['class_label']
                
                # Draw person box
                cv2.rectangle(display_frame, (x1, y1), (x2, y2), color, 3)
                
                # Draw chest region (for breathing detection)
                if result['chest_bbox']:
                    cx1, cy1, cx2, cy2 = result['chest_bbox']
                    cv2.rectangle(display_frame, (cx1, cy1), (cx2, cy2), (255, 255, 0), 2)
                    cv2.putText(display_frame, "Chest ROI", (cx1, cy1 - 10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
                
                # Draw confidence
                conf_text = f"Confidence: {result['confidence']:.2f}"
                cv2.putText(display_frame, conf_text, (x1, y1 - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                
                # Large status text
                if result['fall_detected']:
                    cv2.putText(display_frame, "FALL DETECTED!", (50, 80),
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
                    # Flash effect
                    if frame_count % 10 < 5:
                        overlay = display_frame.copy()
                        cv2.rectangle(overlay, (0, 0), (display_frame.shape[1], display_frame.shape[0]),
                                    (0, 0, 255), 20)
                        display_frame = cv2.addWeighted(overlay, 0.3, display_frame, 0.7, 0)
            else:
                status_text = "No person detected"
                cv2.putText(display_frame, status_text, (50, 80),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (128, 128, 128), 2)
            
            # Info overlay
            info_bg = display_frame.copy()
            cv2.rectangle(info_bg, (0, 0), (400, 120), (0, 0, 0), -1)
            display_frame = cv2.addWeighted(info_bg, 0.6, display_frame, 0.4, 0)
            
            # Display stats
            cv2.putText(display_frame, f"FPS: {fps_display}", (10, 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Inference: {result['inference_time']:.1f}ms", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Frames: {frame_count}", (10, 75),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            cv2.putText(display_frame, f"Falls detected: {fall_count}", (10, 100),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show frame
            cv2.imshow('Fall Detection Test - Press Q to Quit', display_frame)
            
            # Handle keyboard
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q') or key == 27:  # q, Q, or ESC
                break
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    
    finally:
        cap.release()
        cv2.destroyAllWindows()
    
    # Final stats
    print()
    print()
    print("="*70)
    print("📊 Test Summary:")
    print("="*70)
    print(f"   Total frames processed: {frame_count}")
    print(f"   People detected: {person_count}")
    print(f"   Falls detected: {fall_count}")
    if frame_count > 0:
        print(f"   Person detection rate: {(person_count/frame_count*100):.1f}%")
        print(f"   Fall detection rate: {(fall_count/frame_count*100):.1f}%")
    print("="*70)
    
    # Show detection details
    if detections:
        print()
        print("📋 Fall Detection Events:")
        print("-"*70)
        for i, det in enumerate(detections[:10], 1):  # Show first 10
            print(f"   {i}. Frame {det['frame']} - "
                  f"Confidence: {det['confidence']:.3f} - "
                  f"BBox: {det['bbox']}")
        if len(detections) > 10:
            print(f"   ... and {len(detections) - 10} more")
        print("-"*70)
    
    print()
    
    if fall_count > 0:
        print("✅ Fall detection is working!")
        print("   The model successfully detected falls.")
    else:
        print("ℹ️  No falls detected in this session.")
        print("   Try lying down flat in front of the camera to trigger fall detection.")
    
    print()
    print("🎯 Next Steps:")
    print("   1. If fall detection works well, integrate into main system")
    print("   2. Update src/main.py to use FallDetectorPose")
    print("   3. Run: ./scripts/run.sh")
    print()
    print("✨ Test complete!")


if __name__ == '__main__':
    main()
