#!/usr/bin/env python3
"""
Test script for GPIO and Camera components
Run this on the RDK X5 to verify hardware is working correctly
"""
import sys
import os
import time
import signal
import yaml

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import Database
from gpio_handler import GPIOHandler
from camera_service import CameraService


class ComponentTester:
    def __init__(self):
        """Initialize components for testing."""
        print("="*60)
        print("Component Test Script - Elderly Fall Detection System")
        print("="*60)
        
        # Load config
        with open('config/config.yaml', 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        print("\n1. Initializing database...")
        self.db = Database(self.config['storage']['database_path'])
        print("   ✓ Database ready")
        
        print("\n2. Initializing GPIO...")
        self.gpio = GPIOHandler(self.config['gpio'])
        print("   ✓ GPIO ready")
        
        print("\n3. Initializing camera...")
        self.camera = CameraService(self.config, self.db)
        print("   ✓ Camera ready")
        
        # Setup button callbacks
        self.gpio.setup_buttons(
            call_999_callback=self.on_button1_press,
            stop_call_callback=self.on_button2_press
        )
        
        self.running = True
    
    def on_button1_press(self):
        """Handle Button 1 press (Call 999)."""
        print("\n>>> BUTTON 1 PRESSED (Call 999)")
        self.gpio.led_emergency_flash()
        time.sleep(2)
        self.gpio.led_emergency_off()
    
    def on_button2_press(self):
        """Handle Button 2 press (Stop Call)."""
        print("\n>>> BUTTON 2 PRESSED (Stop Call)")
        self.gpio.led_emergency_off()
    
    def test_leds(self):
        """Test LED functionality."""
        print("\n" + "="*60)
        print("TEST 1: LED Functionality")
        print("="*60)
        
        print("\nTesting LED 1 (Fall indicator)...")
        print("  - Turning on...")
        self.gpio.led_fall_on()
        time.sleep(2)
        print("  - Turning off...")
        self.gpio.led_fall_off()
        time.sleep(1)
        
        print("\nTesting LED 2 (Emergency - Solid)...")
        print("  - Turning on...")
        self.gpio.led_emergency_solid()
        time.sleep(2)
        print("  - Turning off...")
        self.gpio.led_emergency_off()
        time.sleep(1)
        
        print("\nTesting LED 2 (Emergency - Flashing)...")
        print("  - Starting flash for 5 seconds...")
        self.gpio.led_emergency_flash()
        time.sleep(5)
        self.gpio.led_emergency_off()
        
        print("\n✓ LED test complete!")
    
    def test_camera(self):
        """Test camera functionality."""
        print("\n" + "="*60)
        print("TEST 2: Camera Functionality")
        print("="*60)
        
        if not self.camera.test_camera():
            print("\n✗ Camera test FAILED!")
            return False
        
        print("\nTesting manual capture...")
        self.gpio.led_fall_on()
        filepath = self.camera.capture_and_save()
        self.gpio.led_fall_off()
        
        if filepath:
            print(f"✓ Image saved: {filepath}")
        else:
            print("✗ Failed to capture image")
            return False
        
        print("\n✓ Camera test complete!")
        return True
    
    def test_continuous_capture(self):
        """Test continuous capture mode."""
        print("\n" + "="*60)
        print("TEST 3: Continuous Capture")
        print("="*60)
        
        print("\nStarting continuous capture for 15 seconds...")
        print("Images will be captured every {} seconds".format(
            self.config['camera']['capture_interval']
        ))
        
        initial_count = self.db.get_image_count()
        print(f"Initial image count: {initial_count}")
        
        self.camera.start_continuous_capture()
        
        # Monitor for 15 seconds
        for i in range(15):
            time.sleep(1)
            if i % 5 == 0:
                count = self.db.get_image_count()
                print(f"  {i}s - Total images: {count}")
        
        self.camera.stop_continuous_capture()
        
        final_count = self.db.get_image_count()
        captured = final_count - initial_count
        
        print(f"\nFinal image count: {final_count}")
        print(f"New images captured: {captured}")
        print("\n✓ Continuous capture test complete!")
    
    def test_storage_stats(self):
        """Test storage statistics."""
        print("\n" + "="*60)
        print("TEST 4: Storage Statistics")
        print("="*60)
        
        stats = self.camera.get_storage_info()
        
        print(f"\nTotal images: {stats['total_images']}")
        print(f"Storage used: {stats['total_size_mb']:.2f} MB")
        print(f"Category breakdown:")
        for category, count in stats['category_counts'].items():
            print(f"  - {category}: {count}")
        
        print("\n✓ Storage stats test complete!")
    
    def test_buttons(self):
        """Test button inputs."""
        print("\n" + "="*60)
        print("TEST 5: Button Inputs")
        print("="*60)
        
        print("\nButton test ready!")
        print("Instructions:")
        print("  - Press Button 1 to trigger 'Call 999' (LED 2 will flash)")
        print("  - Press Button 2 to trigger 'Stop Call' (LED 2 will stop)")
        print("  - Press Ctrl+C to exit")
        print("\nWaiting for button presses...")
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        
        print("\n✓ Button test complete!")
    
    def run_all_tests(self):
        """Run all component tests."""
        try:
            # Test 1: LEDs
            self.test_leds()
            input("\nPress Enter to continue to camera test...")
            
            # Test 2: Camera
            if not self.test_camera():
                print("\nCamera test failed. Stopping tests.")
                return
            input("\nPress Enter to continue to continuous capture test...")
            
            # Test 3: Continuous capture
            self.test_continuous_capture()
            input("\nPress Enter to continue to storage stats test...")
            
            # Test 4: Storage stats
            self.test_storage_stats()
            input("\nPress Enter to continue to button test...")
            
            # Test 5: Buttons
            self.test_buttons()
            
        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources."""
        print("\n" + "="*60)
        print("Cleaning up...")
        print("="*60)
        
        if hasattr(self, 'camera'):
            self.camera.stop_continuous_capture()
        
        if hasattr(self, 'gpio'):
            self.gpio.cleanup()
        
        if hasattr(self, 'db'):
            self.db.close()
        
        print("✓ Cleanup complete!")


def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully."""
    print("\n\nReceived interrupt signal...")
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    
    tester = ComponentTester()
    tester.run_all_tests()
    
    print("\n" + "="*60)
    print("All tests complete!")
    print("="*60)
