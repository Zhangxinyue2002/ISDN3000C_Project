"""
GPIO Handler for Elderly Fall Detection System
Manages buttons and LEDs
Supports RDK X5 (Hobot.GPIO) and Raspberry Pi (RPi.GPIO)
"""
import threading
import time
import sys

# Try to import GPIO library (RDK X5 or Raspberry Pi)
GPIO = None
GPIO_MODE = None

try:
    # Try RDK X5 Hobot.GPIO first
    import Hobot.GPIO as GPIO
    GPIO_MODE = 'HOBOT'
    print("Using Hobot.GPIO (RDK X5)")
except ImportError:
    try:
        # Try Raspberry Pi GPIO
        import RPi.GPIO as GPIO
        GPIO_MODE = 'RPI'
        print("Using RPi.GPIO (Raspberry Pi)")
    except ImportError:
        print("WARNING: No GPIO library found. Running in MOCK mode.")
        print("Hardware control will be simulated.")
        GPIO_MODE = 'MOCK'


class GPIOHandler:
    def __init__(self, config):
        """Initialize GPIO pins from configuration."""
        self.config = config
        self.mode = GPIO_MODE
        
        # Pin assignments
        self.pin_button_call = config['button_call_999']
        self.pin_button_stop = config['button_stop_call']
        self.pin_led_fall = config['led_fall']
        self.pin_led_emergency = config['led_emergency']
        
        # Flash control
        self.flash_thread = None
        self.flashing = False
        
        # Button callbacks
        self.callback_call_999 = None
        self.callback_stop_call = None
        
        # LED states (for mock mode)
        self.led_fall_state = False
        self.led_emergency_state = False
        
        # Initialize GPIO based on available library
        if self.mode == 'MOCK':
            print("GPIO in MOCK mode - simulating hardware")
        else:
            self._init_real_gpio()
        
        print(f"GPIO initialized ({self.mode} mode):")
        print(f"  Button 1 (Call 999): GPIO {self.pin_button_call}")
        print(f"  Button 2 (Stop Call): GPIO {self.pin_button_stop}")
        print(f"  LED 1 (Fall): GPIO {self.pin_led_fall}")
        print(f"  LED 2 (Emergency): GPIO {self.pin_led_emergency}")
    
    def _init_real_gpio(self):
        """Initialize real GPIO hardware."""
        GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
        GPIO.setwarnings(False)
        
        # Setup LED pins as outputs
        GPIO.setup(self.pin_led_fall, GPIO.OUT)
        GPIO.setup(self.pin_led_emergency, GPIO.OUT)
        
        # Setup button pins as inputs with pull-down resistors
        GPIO.setup(self.pin_button_call, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.pin_button_stop, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        # Initialize LEDs to OFF
        GPIO.output(self.pin_led_fall, GPIO.LOW)
        GPIO.output(self.pin_led_emergency, GPIO.LOW)
    
    def setup_buttons(self, call_999_callback, stop_call_callback):
        """Setup button event handlers."""
        self.callback_call_999 = call_999_callback
        self.callback_stop_call = stop_call_callback
        
        if self.mode != 'MOCK':
            # Setup interrupt detection
            bounce_time = self.config['bounce_time']
            GPIO.add_event_detect(self.pin_button_call, GPIO.RISING, 
                                callback=lambda x: call_999_callback(), 
                                bouncetime=bounce_time)
            GPIO.add_event_detect(self.pin_button_stop, GPIO.RISING, 
                                callback=lambda x: stop_call_callback(), 
                                bouncetime=bounce_time)
        
        print("Button callbacks registered")
    
    def led_fall_on(self):
        """Turn on fall detection LED."""
        if self.mode == 'MOCK':
            self.led_fall_state = True
            print("[MOCK] LED 1 (Fall) -> ON")
        else:
            GPIO.output(self.pin_led_fall, GPIO.HIGH)
    
    def led_fall_off(self):
        """Turn off fall detection LED."""
        if self.mode == 'MOCK':
            self.led_fall_state = False
            print("[MOCK] LED 1 (Fall) -> OFF")
        else:
            GPIO.output(self.pin_led_fall, GPIO.LOW)
    
    def led_fall_blink(self, duration=0.5):
        """Blink fall LED briefly."""
        self.led_fall_on()
        time.sleep(duration)
        self.led_fall_off()
    
    def led_emergency_flash(self):
        """Flash emergency LED (non-blocking)."""
        self.led_emergency_off()  # Stop any existing flash
        self.flashing = True
        self.flash_thread = threading.Thread(target=self._flash_loop)
        self.flash_thread.start()
    
    def _flash_loop(self):
        """Internal flash loop."""
        while self.flashing:
            if self.mode == 'MOCK':
                self.led_emergency_state = True
                print("[MOCK] LED 2 (Emergency) -> FLASH ON")
            else:
                GPIO.output(self.pin_led_emergency, GPIO.HIGH)
            time.sleep(0.5)
            
            if self.mode == 'MOCK':
                self.led_emergency_state = False
                print("[MOCK] LED 2 (Emergency) -> FLASH OFF")
            else:
                GPIO.output(self.pin_led_emergency, GPIO.LOW)
            time.sleep(0.5)
    
    def led_emergency_solid(self):
        """Turn emergency LED solid on."""
        self.flashing = False
        if self.flash_thread:
            self.flash_thread.join()
        
        if self.mode == 'MOCK':
            self.led_emergency_state = True
            print("[MOCK] LED 2 (Emergency) -> SOLID ON")
        else:
            GPIO.output(self.pin_led_emergency, GPIO.HIGH)
    
    def led_emergency_off(self):
        """Turn off emergency LED."""
        self.flashing = False
        if self.flash_thread:
            self.flash_thread.join()
        
        if self.mode == 'MOCK':
            self.led_emergency_state = False
            print("[MOCK] LED 2 (Emergency) -> OFF")
        else:
            GPIO.output(self.pin_led_emergency, GPIO.LOW)
    
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
        
        if self.mode != 'MOCK':
            GPIO.cleanup()
        
        print("GPIO cleanup complete")


if __name__ == '__main__':
    """Test GPIO independently."""
    import yaml
    import signal
    import sys
    import os
    
    def signal_handler(sig, frame):
        print("\nExiting...")
        gpio.cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Load config
    config_path = os.path.join(os.path.dirname(__file__), '../config/config.yaml')
    with open(config_path, 'r') as f:
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
    print("\nPress buttons to test (Ctrl+C to exit)...")
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        gpio.cleanup()
