#!/usr/bin/env python3
"""
Elderly Fall Detection System - Main Application

Integrates all components:
- Camera service (continuous capture)
- Fall detection (YOLO)
- Breathing detection (SIFT)
- Emergency controller (state machine)
- GPIO controls (buttons & LEDs)
- Database logging

Author: ISDN3000C Project Team
Date: 2025-12-10
"""

import sys
import os
import time
import signal
import threading
import logging
from pathlib import Path
import yaml

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database import Database
from src.gpio_handler import GPIOHandler
from src.camera_service import CameraService
from src.fall_detector_enhanced import FallDetectorEnhanced
from src.breathing_detector import BreathingDetector
from src.emergency_controller import EmergencyController, EmergencyState

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ElderlyFallDetectionSystem:
    """
    Main system coordinator.
    
    Orchestrates all components and manages the detection pipeline.
    """
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """
        Initialize the complete system.
        
        Args:
            config_path: Path to configuration file
        """
        logger.info("="*60)
        logger.info("Elderly Fall Detection System")
        logger.info("="*60)
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # System state
        self.running = False
        self.monitoring_thread = None
        self.fall_check_interval = self.config['fall_detection'].get('check_interval', 0.5)
        self.last_processed_image_id = 0  # Track last processed image for fall detection
        
        # Emergency mode tracking
        self.emergency_mode_active = False
        self.emergency_mode_start = None
        self.emergency_mode_duration = 10  # 10 seconds
        
        # Breathing detection tracking (one-time check per fall)
        self.breathing_check_done = False  # Flag to ensure breathing is checked only once per fall
        
        # Initialize components
        logger.info("\n1. Initializing database...")
        self.db = Database(self.config['storage']['database_path'])
        logger.info("   ✓ Database ready")
        
        logger.info("\n2. Initializing GPIO...")
        self.gpio = GPIOHandler(self.config['gpio'])
        logger.info("   ✓ GPIO ready")
        
        logger.info("\n3. Initializing camera...")
        self.camera = CameraService(self.config, self.db)
        logger.info("   ✓ Camera ready")
        
        logger.info("\n4. Initializing enhanced fall detector...")
        self.fall_detector = FallDetectorEnhanced(debug_mode=True)
        logger.info("   ✓ Enhanced fall detector ready")
        
        logger.info("\n5. Initializing breathing detector...")
        self.breathing_detector = BreathingDetector(config_path)
        logger.info("   ✓ Breathing detector ready")
        
        logger.info("\n6. Initializing emergency controller...")
        self.emergency = EmergencyController(config_path, self.gpio, self.db)
        logger.info("   ✓ Emergency controller ready")
        
        # Setup callbacks
        self._setup_callbacks()
        
        logger.info("\n✓ System initialization complete!")
        logger.info("="*60)
    
    def _setup_callbacks(self):
        """Setup button callbacks and emergency notifications."""
        # Button 1: Manual emergency call
        self.gpio.setup_buttons(
            call_999_callback=self._on_manual_emergency,
            stop_call_callback=self._on_cancel_emergency
        )
        
        # Emergency controller callback
        self.emergency.set_state_change_callback(self._on_emergency_state_change)
        
        logger.info("Callbacks configured:")
        logger.info("  - Button 1: Manual emergency trigger")
        logger.info("  - Button 2: Cancel/stop emergency")
    
    def _on_manual_emergency(self):
        """Handle manual emergency button press."""
        logger.warning("🔴 MANUAL EMERGENCY BUTTON PRESSED!")
        logger.warning("⚠️  EMERGENCY MODE ACTIVATED - All photos will be marked as EMERGENCY until Button 2 is pressed")
        
        # Activate emergency mode (no time limit, controlled by emergency state)
        self.emergency_mode_active = True
        self.emergency_mode_start = time.time()
        
        # Log emergency event
        self.db.add_event('emergency_triggered', details='Manual emergency button (Button 1) pressed')
        
        self.emergency.trigger_emergency(manual=True)
    
    def _on_cancel_emergency(self):
        """Handle cancel button press - highest priority, resets everything."""
        logger.warning("🟢 BUTTON 2 PRESSED - SYSTEM RESET")
        
        # Reset breathing check flag - allow breathing check for next fall
        self.breathing_check_done = False
        logger.info("✓ Breathing check flag reset - ready for next fall detection")
        
        # Button 2 has highest priority - always reset to IDLE
        # Turns off LED1 and LED2, stops all monitoring
        self.emergency.reset_to_idle("User pressed Button 2 (reset)")
        logger.info("All LEDs OFF - System back to fall detection mode")
    
    def _on_emergency_state_change(self, new_state: EmergencyState, old_state: EmergencyState):
        """
        Handle emergency state changes.
        
        Args:
            new_state: New emergency state
            old_state: Previous emergency state
        """
        logger.info(f"Emergency state: {old_state.value} → {new_state.value}")
        
        # When entering EMERGENCY_ACTIVE state (LED1+LED2 solid, calling 999)
        # Activate emergency mode to mark all subsequent photos as EMERGENCY
        if new_state == EmergencyState.EMERGENCY_ACTIVE:
            logger.warning("🚨 EMERGENCY_ACTIVE STATE - Calling 999! All photos will be marked as EMERGENCY")
            self.emergency_mode_active = True
            self.emergency_mode_start = time.time()
        
        # When emergency is resolved or cancelled, deactivate emergency mode
        elif new_state in [EmergencyState.IDLE, EmergencyState.EMERGENCY_RESOLVED, 
                          EmergencyState.COUNTDOWN_CANCELLED]:
            if self.emergency_mode_active:
                logger.info("Emergency mode deactivated")
                self.emergency_mode_active = False
    
    def _monitoring_loop(self):
        """
        Main monitoring loop.
        
        Continuously checks saved images for fall detection.
        """
        logger.info("Starting fall detection monitoring loop...")
        
        import cv2
        frames_checked = 0
        falls_detected = 0
        
        while self.running:
            try:
                # Get the most recently saved image from database
                recent_images = self.db.get_images(limit=1, order='desc')
                
                if recent_images and len(recent_images) > 0:
                    latest_image = recent_images[0]
                    image_id = latest_image[0]
                    filepath = latest_image[2]  # filepath is at index 2
                    
                    # Only process if we haven't processed this image yet
                    if image_id > self.last_processed_image_id:
                        self.last_processed_image_id = image_id
                        
                        # Load the actual saved image from disk
                        frame = cv2.imread(filepath)
                        
                        if frame is not None:
                            # If in emergency mode (LED1+LED2 on), mark all photos as emergency
                            if self.emergency_mode_active:
                                elapsed = time.time() - self.emergency_mode_start
                                logger.warning(f"⚠️  EMERGENCY MODE: Image {image_id} marked as EMERGENCY (elapsed: {elapsed:.1f}s, press Button 2 to stop)")
                                
                                # Update database with emergency category
                                cursor = self.db.conn.cursor()
                                cursor.execute('''
                                    UPDATE images 
                                    SET category = 'emergency', emergency_triggered = 1, preserved = 1
                                    WHERE id = ?
                                ''', (image_id,))
                                self.db.conn.commit()
                                
                                frames_checked += 1
                            else:
                                # Normal fall detection mode
                                # Run fall detection on the saved image
                                result = self.fall_detector.detect_fall(frame)
                                frames_checked += 1
                                
                                # Update the image with fall detection results
                                if result['fall_detected']:
                                    category = 'fall'
                                    falls_detected += 1
                                    logger.warning(f"🚨 FALL DETECTED! Image ID: {image_id}, Confidence: {result['confidence']:.2f} - Pose: {result.get('pose_label', 'unknown')}")
                                    
                                    # Update database
                                    self.db.update_image_category(image_id, category, 
                                                                 fall_detected=True,
                                                                 confidence=result['confidence'])
                                    
                                    # Log fall detected event
                                    self.db.add_event('fall_detected', image_id=image_id, 
                                                     details=f"Confidence: {result['confidence']:.2f}, Pose: {result.get('pose_label', 'unknown')}")
                                    
                                    # Handle based on current emergency state
                                    if self.emergency.state == EmergencyState.IDLE:
                                        # New fall detected
                                        self.emergency.handle_fall_detected(result['confidence'])
                                        
                                        # Check breathing ONLY ONCE per fall (not continuously)
                                        if not self.breathing_check_done:
                                            logger.warning("🫁 BREATHING DETECTION MODE ACTIVATED 🫁")
                                            logger.info("💨 Checking breathing immediately (ONE-TIME check)...")
                                            self._check_breathing(result)
                                            self.breathing_check_done = True
                                        else:
                                            logger.info("ℹ️  Breathing already checked for this fall - skipping (press Button 2 to reset)")
                                    else:
                                        logger.debug(f"Fall continues (state: {self.emergency.state.value})")
                                else:
                                    # Update with normal category and pose label
                                    logger.debug(f"Normal pose detected. Image ID: {image_id}, Confidence: {result['confidence']:.2f}")
                                    self.db.update_image_category(image_id, 'normal',
                                                                 fall_detected=False,
                                                                 confidence=result['confidence'])
                        else:
                            logger.warning(f"Failed to load image: {filepath}")
                
                # Log periodically
                if frames_checked % 100 == 0:
                    logger.info(f"Frames checked: {frames_checked}, Falls detected: {falls_detected}")
                
                # Sleep between checks
                time.sleep(self.fall_check_interval)
            
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                time.sleep(1)
        
        logger.info("Monitoring loop stopped")
    
    def _check_breathing(self, fall_result: dict):
        """
        Check breathing after fall detection.
        
        Args:
            fall_result: Result from fall detector
        """
        logger.warning("="*60)
        logger.warning("🫁 BREATHING DETECTION SEQUENCE STARTED 🫁")
        logger.warning("="*60)
        
        self.emergency.set_state(EmergencyState.CHECKING_BREATHING, "Analyzing breathing")
        
        # Capture video for breathing analysis (optimized: 8s duration, 100 keypoints max)
        duration = self.breathing_detector.capture_duration
        fps = self.breathing_detector.fps
        
        logger.info(f"📹 Capturing {duration}s of video at {fps} FPS (optimized for speed)...")
        
        frames = []
        start_time = time.time()
        
        while time.time() - start_time < duration:
            frame = self.camera.get_current_frame()
            if frame is not None:
                frames.append(frame)
            time.sleep(1.0 / fps)
        
        logger.info(f"✅ Captured {len(frames)} frames for breathing analysis")
        
        # Analyze breathing
        chest_bbox = fall_result.get('chest_bbox')
        if chest_bbox is None:
            logger.warning("⚠️  No chest region detected, using default")
            # Use default region if not available
            h, w = frames[0].shape[:2]
            chest_bbox = (w // 4, h // 4, 3 * w // 4, 3 * h // 4)
        
        logger.warning("🔬 ANALYZING CHEST MOVEMENT (every 3rd frame for speed)...")
        breathing_result = self.breathing_detector.analyze_breathing(frames, chest_bbox)
        
        logger.warning("="*60)
        logger.warning("💨 BREATHING ANALYSIS COMPLETE (optimized) 💨")
        logger.warning("="*60)
        logger.info(f"  🫁 Breathing detected: {breathing_result['breathing_detected']}")
        logger.info(f"  📊 Confidence: {breathing_result['confidence']:.2f}")
        logger.info(f"  💓 Breathing rate: {breathing_result['breathing_rate']:.1f} BPM")
        
        # Notify emergency controller
        self.emergency.handle_breathing_result(
            breathing_detected=breathing_result['breathing_detected'],
            confidence=breathing_result['confidence']
        )
    
    def start(self):
        """Start the system."""
        if self.running:
            logger.warning("System already running")
            return
        
        logger.info("\n" + "="*60)
        logger.info("STARTING SYSTEM")
        logger.info("="*60)
        
        self.running = True
        
        # Start camera continuous capture
        logger.info("\n1. Starting continuous camera capture...")
        self.camera.start_continuous_capture()
        logger.info("   ✓ Camera capturing every {} seconds".format(
            self.config['camera']['capture_interval']
        ))
        
        # Start monitoring thread
        logger.info("\n2. Starting fall detection monitoring...")
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        logger.info("   ✓ Monitoring active")
        
        logger.info("\n✓ SYSTEM RUNNING")
        logger.info("="*60)
        logger.info("\nControls:")
        logger.info("  - Button 1: Manual emergency call")
        logger.info("  - Button 2: Cancel/stop emergency")
        logger.info("  - Press Ctrl+C to stop system")
        logger.info("")
        
        # Log initial status
        self._log_status()
    
    def stop(self):
        """Stop the system."""
        if not self.running:
            return
        
        logger.info("\n" + "="*60)
        logger.info("STOPPING SYSTEM")
        logger.info("="*60)
        
        self.running = False
        
        # Stop monitoring thread
        if self.monitoring_thread:
            logger.info("Stopping monitoring thread...")
            self.monitoring_thread.join(timeout=5)
        
        # Stop camera
        logger.info("Stopping camera...")
        self.camera.stop_continuous_capture()
        
        # Cleanup emergency controller
        logger.info("Cleaning up emergency controller...")
        self.emergency.cleanup()
        
        logger.info("\n✓ SYSTEM STOPPED")
        logger.info("="*60)
    
    def _log_status(self):
        """Log system status."""
        status = {
            'camera': {
                'running': self.camera.running,
                'images_captured': self.db.get_image_count()
            },
            'fall_detector': self.fall_detector.get_model_info(),
            'emergency': self.emergency.get_status(),
            'storage': self.camera.get_storage_info()
        }
        
        logger.info("\nSystem Status:")
        logger.info(f"  Camera running: {status['camera']['running']}")
        logger.info(f"  Images captured: {status['camera']['images_captured']}")
        logger.info(f"  Fall detector: {'ACTIVE' if status['fall_detector']['model_loaded'] else 'MOCK MODE'}")
        logger.info(f"  Emergency state: {status['emergency']['state']}")
        logger.info(f"  Storage used: {status['storage']['total_size_mb']:.1f} MB")
    
    def run(self):
        """
        Run the system (blocking).
        
        Starts all components and runs until interrupted.
        """
        try:
            self.start()
            
            # Keep running until interrupted
            while self.running:
                time.sleep(1)
                
                # Periodic status updates (every 5 minutes)
                if int(time.time()) % 300 == 0:
                    self._log_status()
        
        except KeyboardInterrupt:
            logger.info("\n\nReceived interrupt signal...")
        
        finally:
            self.stop()
            self.cleanup()
    
    def cleanup(self):
        """Cleanup all resources."""
        logger.info("\nCleaning up resources...")
        
        if hasattr(self, 'camera'):
            self.camera.stop_continuous_capture()
        
        if hasattr(self, 'gpio'):
            self.gpio.cleanup()
        
        if hasattr(self, 'db'):
            self.db.close()
        
        logger.info("✓ Cleanup complete!")


def signal_handler(sig, frame):
    """Handle interrupt signals gracefully."""
    logger.info("\n\nReceived interrupt signal...")
    sys.exit(0)


def main():
    """Main entry point."""
    # Setup signal handler
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run system
    system = ElderlyFallDetectionSystem()
    system.run()


if __name__ == '__main__':
    main()
