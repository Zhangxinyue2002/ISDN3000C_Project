"""
GPIO Handler for Elderly Fall Detection System
Manages buttons and LEDs
"""
from gpiozero import LED, Button
import threading
import time


class GPIOHandler:
    def __init__(self, config):
        """Initialize GPIO pins from configuration."""
        self.config = config
        
        # Initialize buttons
        self.button_call_999 = Button(config['button_call_999'], bounce_time=config['bounce_time']/1000)
        self.button_stop_call = Button(config['button_stop_call'], bounce_time=config['bounce_time']/1000)
        
        # Initialize LEDs
        self.led_fall = LED(config['led_fall'])
        self.led_emergency = LED(config['led_emergency'])
        
        # Flash control
        self.flash_thread = None
        self.flashing = False
        
        print(f"GPIO initialized:")
        print(f"  Button 1 (Call 999): GPIO {config['button_call_999']}")
        print(f"  Button 2 (Stop Call): GPIO {config['button_stop_call']}")
        print(f"  LED 1 (Fall): GPIO {config['led_fall']}")
        print(f"  LED 2 (Emergency): GPIO {config['led_emergency']}")
    
    def setup_buttons(self, call_999_callback, stop_call_callback):
        """Setup button event handlers."""
        self.button_call_999.when_pressed = call_999_callback
        self.button_stop_call.when_pressed = stop_call_callback
        print("Button callbacks registered")
    
    def led_fall_on(self):
        """Turn on fall detection LED."""
        self.led_fall.on()
    
    def led_fall_off(self):
        """Turn off fall detection LED."""
        self.led_fall.off()
    
    def led_fall_blink(self, duration=0.5):
        """Blink fall LED briefly."""
        self.led_fall.on()
        time.sleep(duration)
        self.led_fall.off()
    
    def led_emergency_flash(self):
        """Flash emergency LED (non-blocking)."""
        self.led_emergency_off()  # Stop any existing flash
        self.flashing = True
        self.flash_thread = threading.Thread(target=self._flash_loop)
        self.flash_thread.start()
    
    def _flash_loop(self):
        """Internal flash loop."""
        while self.flashing:
            self.led_emergency.on()
            time.sleep(0.5)
            self.led_emergency.off()
            time.sleep(0.5)
    
    def led_emergency_solid(self):
        """Turn emergency LED solid on."""
        self.flashing = False
        if self.flash_thread:
            self.flash_thread.join()
        self.led_emergency.on()
    
    def led_emergency_off(self):
        """Turn off emergency LED."""
        self.flashing = False
        if self.flash_thread:
            self.flash_thread.join()
        self.led_emergency.off()
    
    def test_all(self):
        """Test all GPIO components."""
        print("\nTesting GPIO components...")
        
        print("Testing LED 1 (Fall)...")
        self.led_fall_on()
        time.sleep(1)
        self.led_fall_off()
        
        print("Testing LED 2 (Emergency) - Solid...")
        self.led_emergency_solid()
        time.sleep(1)
        self.led_emergency_off()
        
        print("Testing LED 2 (Emergency) - Flash...")
        self.led_emergency_flash()
        time.sleep(3)
        self.led_emergency_off()
        
        print("\nGPIO test complete!")
        print("Now test buttons:")
        print("  - Press Button 1 to test Call 999")
        print("  - Press Button 2 to test Stop Call")
        print("  - Press Ctrl+C to exit")
    
    def cleanup(self):
        """Cleanup GPIO resources."""
        self.flashing = False
        if self.flash_thread:
            self.flash_thread.join()
        self.led_fall.close()
        self.led_emergency.close()
        self.button_call_999.close()
        self.button_stop_call.close()
        print("GPIO cleanup complete")


if __name__ == '__main__':
    """Test GPIO independently."""
    import yaml
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print("\nExiting...")
        gpio.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Load config
    with open('../config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    gpio = GPIOHandler(config['gpio'])
    
    # Setup test callbacks
    def on_button1():
        print(">>> Button 1 pressed! (Call 999)")
        gpio.led_fall_blink()
    
    def on_button2():
        print(">>> Button 2 pressed! (Stop Call)")
        gpio.led_fall_blink()
    
    gpio.setup_buttons(on_button1, on_button2)
    
    # Run test
    gpio.test_all()
    
    # Keep running
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio.cleanup()
