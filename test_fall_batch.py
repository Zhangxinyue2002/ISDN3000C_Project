#!/usr/bin/env python3
"""
Batch test script for fall detection on multiple images

Usage:
    python3 test_fall_batch.py                    # Test all images in PHOTO/
    python3 test_fall_batch.py image1.jpg image2.jpg  # Test specific images
    python3 test_fall_batch.py --dir path/to/images/  # Test all images in directory
"""

import cv2
import sys
import os
import glob
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.fall_detector_pose import FallDetectorPose


def test_batch_images(image_paths, detector):
    """Test multiple images and generate report"""
    
    results = []
    total = len(image_paths)
    
    print(f"\n{'='*70}")
    print(f"Testing {total} images...")
    print(f"{'='*70}\n")
    
    for i, image_path in enumerate(image_paths, 1):
        print(f"[{i}/{total}] Processing: {os.path.basename(image_path)}", end=" ... ")
        
        # Read image
        frame = cv2.imread(image_path)
        if frame is None:
            print("❌ Cannot read image")
            results.append({
                'path': image_path,
                'filename': os.path.basename(image_path),
                'error': 'Cannot read image',
                'person_detected': False,
                'fall_detected': False
            })
            continue
        
        # Detect
        result = detector.detect_fall(frame)
        result['path'] = image_path
        result['filename'] = os.path.basename(image_path)
        results.append(result)
        
        # Print quick result
        if result['person_detected']:
            if result['fall_detected']:
                print(f"⚠️  FALL ({result['confidence']:.2f})")
            else:
                print(f"✓ {result['class_label']} ({result['confidence']:.2f})")
        else:
            print("○ No person")
    
    return results


def print_summary(results):
    """Print detailed summary report"""
    
    print(f"\n{'='*70}")
    print("📊 BATCH TEST SUMMARY")
    print(f"{'='*70}\n")
    
    total = len(results)
    person_detected = sum(1 for r in results if r.get('person_detected', False))
    falls_detected = sum(1 for r in results if r.get('fall_detected', False))
    standing = sum(1 for r in results if r.get('class_label') == 'standing')
    sitting = sum(1 for r in results if r.get('class_label') == 'sitting')
    errors = sum(1 for r in results if 'error' in r)
    
    print(f"Total Images:        {total}")
    print(f"Person Detected:     {person_detected} ({person_detected/total*100:.1f}%)")
    print(f"Falls Detected:      {falls_detected} ({falls_detected/total*100:.1f}%)")
    print(f"Standing:            {standing}")
    print(f"Sitting:             {sitting}")
    print(f"Errors:              {errors}")
    
    # Show all falls
    if falls_detected > 0:
        print(f"\n{'─'*70}")
        print("⚠️  FALL DETECTIONS:")
        print(f"{'─'*70}")
        for r in results:
            if r.get('fall_detected', False):
                print(f"  • {r['filename']:30s} - Confidence: {r['confidence']:.3f}")
    
    # Show errors
    if errors > 0:
        print(f"\n{'─'*70}")
        print("❌ ERRORS:")
        print(f"{'─'*70}")
        for r in results:
            if 'error' in r:
                print(f"  • {r['filename']:30s} - {r['error']}")
    
    print(f"\n{'='*70}\n")


def save_results_csv(results, output_file='test_results.csv'):
    """Save results to CSV file"""
    
    import csv
    
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Filename', 'Person Detected', 'Fall Detected', 'Class', 'Confidence', 'Inference Time (ms)'])
        
        for r in results:
            writer.writerow([
                r.get('filename', ''),
                r.get('person_detected', False),
                r.get('fall_detected', False),
                r.get('class_label', 'N/A'),
                f"{r.get('confidence', 0):.3f}",
                f"{r.get('inference_time', 0):.1f}"
            ])
    
    print(f"💾 Results saved to: {output_file}")


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Batch test fall detection on multiple images')
    parser.add_argument('images', nargs='*', help='Image files to test')
    parser.add_argument('--dir', type=str, default='PHOTO', help='Directory containing images (default: PHOTO)')
    parser.add_argument('--pattern', type=str, default='*.jpg', help='File pattern to match (default: *.jpg)')
    parser.add_argument('--save-csv', action='store_true', help='Save results to CSV file')
    parser.add_argument('--output', type=str, default='test_results.csv', help='Output CSV filename')
    args = parser.parse_args()
    
    print("="*70)
    print(" "*15 + "🤖 Fall Detection Batch Test 🤖")
    print("="*70)
    print()
    
    # Initialize detector
    print("📥 Initializing YOLOv8 Pose detector...")
    try:
        detector = FallDetectorPose()
    except Exception as e:
        print(f"❌ Error initializing detector: {e}")
        print("\n💡 Try installing ultralytics:")
        print("   pip install ultralytics")
        return
    
    if not detector.model_loaded:
        print("❌ Model failed to load")
        return
    
    print("✅ Detector initialized successfully!")
    
    # Get list of images
    image_paths = []
    
    if args.images:
        # Use specified images
        for img in args.images:
            if os.path.exists(img):
                image_paths.append(img)
            else:
                print(f"⚠️  Warning: Image not found: {img}")
    else:
        # Scan directory
        search_dir = args.dir
        if not os.path.exists(search_dir):
            print(f"❌ Directory not found: {search_dir}")
            return
        
        # Support multiple extensions
        patterns = ['*.jpg', '*.jpeg', '*.png', '*.JPG', '*.JPEG', '*.PNG']
        for pattern in patterns:
            image_paths.extend(glob.glob(os.path.join(search_dir, pattern)))
            image_paths.extend(glob.glob(os.path.join(search_dir, '**', pattern), recursive=True))
        
        # Remove duplicates
        image_paths = list(set(image_paths))
    
    if not image_paths:
        print(f"❌ No images found!")
        print(f"\n💡 Usage:")
        print(f"   python3 test_fall_batch.py                    # Test all in PHOTO/")
        print(f"   python3 test_fall_batch.py img1.jpg img2.jpg  # Test specific images")
        print(f"   python3 test_fall_batch.py --dir path/to/dir  # Test all in directory")
        return
    
    # Sort for consistent ordering
    image_paths.sort()
    
    # Run batch test
    results = test_batch_images(image_paths, detector)
    
    # Print summary
    print_summary(results)
    
    # Save to CSV if requested
    if args.save_csv:
        save_results_csv(results, args.output)
    
    print("✨ Batch test complete!")


if __name__ == '__main__':
    main()
