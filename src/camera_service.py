"""
Camera Service for Elderly Fall Detection System
Handles continuous photo capture and storage management
"""
import cv2
import time
import threading
import os
from datetime import datetime
from pathlib import Path


class CameraService:
    def __init__(self, config, database):
        """Initialize camera with configuration."""
        self.config = config
        self.db = database
        self.camera_config = config['camera']
        self.storage_config = config['storage']
        
        # Initialize camera
        self.cap = None
        self.running = False
        self.capture_thread = None
        self.current_frame = None
        self.frame_lock = threading.Lock()
        
        # Storage
        self.images_dir = Path(self.storage_config['images_directory'])
        self.images_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"Camera service initialized")
        print(f"  Resolution: {self.camera_config['resolution']}")
        print(f"  Capture interval: {self.camera_config['capture_interval']}s")
        print(f"  Images directory: {self.images_dir}")
    
    def open_camera(self):
        """Open camera device."""
        if self.cap is not None and self.cap.isOpened():
            return True
        
        # Try multiple camera indices
        camera_indices = [0, 1, 8, 10]
        
        for idx in camera_indices:
            print(f"Trying /dev/video{idx}...")
            self.cap = cv2.VideoCapture(idx)
            
            if self.cap.isOpened():
                # Set camera properties
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.camera_config['resolution'][0])
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.camera_config['resolution'][1])
                self.cap.set(cv2.CAP_PROP_FPS, self.camera_config['framerate'])
                
                print(f"✓ Camera opened successfully on /dev/video{idx}")
                print(f"  Actual resolution: {int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}")
                print(f"  Actual FPS: {int(self.cap.get(cv2.CAP_PROP_FPS))}")
                return True
            else:
                self.cap.release()
                self.cap = None
        
        print("ERROR: Failed to open camera on any device!")
        return False
    
    def start_continuous_capture(self):
        """Start continuous photo capture mode."""
        if self.running:
            print("Camera already running")
            return
        
        if not self.open_camera():
            print("Cannot start capture - camera not available")
            return
        
        self.running = True
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.start()
        print("Continuous capture started")
    
    def stop_continuous_capture(self):
        """Stop continuous capture."""
        self.running = False
        if self.capture_thread:
            self.capture_thread.join()
        if self.cap:
            self.cap.release()
        print("Continuous capture stopped")
    
    def _capture_loop(self):
        """Internal continuous capture loop."""
        interval = self.camera_config['capture_interval']
        
        while self.running:
            try:
                # Capture frame
                ret, frame = self.cap.read()
                
                if ret:
                    # Update current frame
                    with self.frame_lock:
                        self.current_frame = frame.copy()
                    
                    # Save frame
                    self.capture_and_save(frame)
                    
                    # Check storage and cleanup if needed
                    self._check_storage()
                else:
                    print("Failed to read frame from camera")
                    time.sleep(1)
                    continue
                
                # Wait for next interval
                time.sleep(interval)
                
            except Exception as e:
                print(f"Error in capture loop: {e}")
                time.sleep(1)
    
    def get_current_frame(self):
        """Get current frame as numpy array."""
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def capture_and_save(self, frame=None):
        """Capture one photo and save with sequential number."""
        if frame is None:
            if not self.cap or not self.cap.isOpened():
                if not self.open_camera():
                    return None
            
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame")
                return None
        
        # Get next image number
        img_number = self.db.get_next_image_number()
        
        # Create filename
        filename = f"{img_number}.{self.storage_config['image_format']}"
        filepath = self.images_dir / filename
        
        # Save image
        quality = self.storage_config['image_quality']
        cv2.imwrite(str(filepath), frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        
        # Add to database
        self.db.add_image(
            filename=filename,
            filepath=str(filepath),
            category='normal'
        )
        
        return filepath
    
    def save_image(self, image, category='normal', metadata=None):
        """Save image with specific category and metadata."""
        # Get next image number
        img_number = self.db.get_next_image_number()
        
        # Create filename
        filename = f"{img_number}.{self.storage_config['image_format']}"
        filepath = self.images_dir / filename
        
        # Save image
        quality = self.storage_config['image_quality']
        cv2.imwrite(str(filepath), image, [cv2.IMWRITE_JPEG_QUALITY, quality])
        
        # Add to database
        fall_detected = category == 'fall_detected'
        emergency = category == 'emergency'
        confidence = metadata.get('confidence', None) if metadata else None
        
        image_id = self.db.add_image(
            filename=filename,
            filepath=str(filepath),
            category=category,
            fall_detected=fall_detected,
            emergency_triggered=emergency,
            confidence=confidence
        )
        
        return image_id
    
    def _check_storage(self):
        """Check storage and trigger cleanup if needed."""
        total_images = self.db.get_image_count()
        max_images = self.storage_config['max_images']
        threshold = self.storage_config['cleanup_threshold']
        
        if total_images > (max_images * threshold):
            print(f"Storage threshold reached ({total_images} images). Starting cleanup...")
            deleted = self.db.cleanup_old_images(
                max_images=max_images,
                cleanup_threshold=threshold,
                keep_preserved=self.storage_config.get('keep_fall_images', True),
                cleanup_days=self.storage_config['cleanup_days']
            )
            print(f"Cleanup complete. Deleted {deleted} images.")
    
    def get_storage_info(self):
        """Get current storage usage statistics."""
        return self.db.get_storage_stats()
    
    def test_camera(self):
        """Test camera capture."""
        print("\nTesting camera...")
        
        if not self.open_camera():
            print("Camera test failed!")
            return False
        
        print("Capturing test image...")
        ret, frame = self.cap.read()
        
        if ret:
            test_file = self.images_dir / "test_capture.jpg"
            cv2.imwrite(str(test_file), frame)
            print(f"Test image saved: {test_file}")
            print(f"  Size: {frame.shape}")
            return True
        else:
            print("Failed to capture test image")
            return False


if __name__ == '__main__':
    """Test camera independently."""
    import yaml
    import sys
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from database import Database
    
    # Load config
    with open('../config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize database
    db = Database(config['storage']['database_path'])
    
    # Initialize camera
    camera = CameraService(config, db)
    
    # Test camera
    if camera.test_camera():
        print("\nCamera test successful!")
        
        # Test continuous capture
        print("\nStarting continuous capture for 10 seconds...")
        camera.start_continuous_capture()
        time.sleep(10)
        camera.stop_continuous_capture()
        
        # Show storage stats
        stats = camera.get_storage_info()
        print(f"\nStorage Statistics:")
        print(f"  Total images: {stats['total_images']}")
        print(f"  Storage used: {stats['total_size_mb']:.2f} MB")
    else:
        print("\nCamera test failed!")
    
    db.close()
