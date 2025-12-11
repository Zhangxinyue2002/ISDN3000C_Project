#!/usr/bin/env python3
"""
Test script to verify camera captures are being saved and accessible via web interface

This test:
1. Initializes the camera service
2. Captures a few test images
3. Verifies they are saved to database
4. Shows how to access them via the web API

Usage:
    python3 test_camera_web.py
"""

import sys
import os
import time
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src.database import Database
from src.camera_service import CameraService

def main():
    print("="*70)
    print("           📸 Camera to Web Interface Test 📸")
    print("="*70)
    
    # Load configuration
    config_path = Path('config/config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize database
    print("\n📥 Initializing database...")
    db = Database(config['storage']['database_path'])
    
    # Get initial image count
    initial_count = db.get_next_image_number() - 1
    print(f"   Current images in database: {initial_count}")
    
    # Initialize camera service
    print("\n📷 Initializing camera service...")
    camera = CameraService(config, db)
    
    # Open camera
    if not camera.open_camera():
        print("\n❌ ERROR: Camera not available!")
        print("   Make sure a camera is connected to /dev/video0 or /dev/video8")
        return
    
    print("\n✅ Camera opened successfully!")
    
    # Capture test images
    num_captures = 3
    print(f"\n📸 Capturing {num_captures} test images...")
    
    captured_files = []
    for i in range(num_captures):
        print(f"   Capture {i+1}/{num_captures}...", end=" ")
        filepath = camera.capture_and_save()
        if filepath:
            captured_files.append(filepath)
            print(f"✓ Saved: {os.path.basename(filepath)}")
        else:
            print("✗ Failed")
        
        if i < num_captures - 1:
            time.sleep(1)  # Wait 1 second between captures
    
    # Close camera
    camera.stop_continuous_capture()
    
    # Verify images in database
    print(f"\n📊 Verifying database entries...")
    final_count = db.get_next_image_number() - 1
    new_images = final_count - initial_count
    print(f"   Images before test: {initial_count}")
    print(f"   Images after test:  {final_count}")
    print(f"   New images added:   {new_images}")
    
    if new_images == len(captured_files):
        print("\n✅ SUCCESS: All images saved to database!")
    else:
        print(f"\n⚠️  WARNING: Expected {len(captured_files)}, got {new_images} in database")
    
    # Show recent images
    print("\n📋 Recent images in database:")
    recent_images = db.get_images(limit=5, order='desc')
    for img in recent_images:
        # Database columns: id, filename, filepath, timestamp, category, fall_detected, 
        # breathing_detected, emergency_triggered, confidence, preserved
        img_id, filename, filepath, timestamp, category, fall_detected, breathing_detected, emergency_triggered, confidence, preserved = img
        print(f"   • {filename:15s} - {timestamp} - Category: {category}")
    
    # Show web interface instructions
    print("\n" + "="*70)
    print("🌐 WEB INTERFACE INSTRUCTIONS:")
    print("="*70)
    print("\n1. Start the web server:")
    print("   cd webapp")
    print("   python3 app.py")
    print("\n2. Or start the full system:")
    print("   ./scripts/run.sh")
    print("\n3. Open your browser:")
    print("   http://localhost:5000")
    print("\n4. The images you just captured should appear in the gallery!")
    print("\n" + "="*70)
    print("\n✨ Camera to web integration test complete!")
    print()

if __name__ == "__main__":
    main()
