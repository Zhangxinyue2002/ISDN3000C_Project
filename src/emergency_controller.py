"""
Emergency Controller - State Machine for Emergency Response

Manages the emergency response workflow:
1. Fall detected → Check breathing
2. No breathing → Start countdown
3. Countdown → Can be cancelled by user
4. Timeout → Trigger emergency call

Author: ISDN3000C Project Team
Date: 2025-12-10
"""

import time
import threading
import logging
from enum import Enum
from typing import Optional, Callable
import yaml
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmergencyState(Enum):
    """Emergency system states."""
    IDLE = "idle"
    FALL_DETECTED = "fall_detected"
    CHECKING_BREATHING = "checking_breathing"
    NO_BREATHING = "no_breathing"
    COUNTDOWN_ACTIVE = "countdown_active"
    COUNTDOWN_CANCELLED = "countdown_cancelled"
    EMERGENCY_ACTIVE = "emergency_active"
    EMERGENCY_RESOLVED = "emergency_resolved"


class EmergencyController:
    """
    Manages emergency response state machine.
    
    Coordinates between fall detection, breathing detection, GPIO controls,
    and notification systems to handle emergency situations.
    """
    
    def __init__(self, config_path: str = "config/config.yaml", 
                 gpio_handler=None, database=None):
        """
        Initialize emergency controller.
        
        Args:
            config_path: Path to configuration file
            gpio_handler: GPIOHandler instance for LED/button control
            database: Database instance for logging events
        """
        # Load configuration
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.config = config.get('emergency', {})
        else:
            logger.warning(f"Config file not found: {config_path}. Using defaults.")
            self.config = {}
        
        # Configuration
        self.countdown_duration = self.config.get('countdown_duration', 10)  # seconds
        self.contact_number = self.config.get('contact_number', '999')
        self.enable_actual_call = self.config.get('enable_actual_call', False)
        self.manual_trigger_enabled = self.config.get('manual_trigger', True)
        self.auto_trigger_enabled = self.config.get('auto_trigger', True)
        
        # External components
        self.gpio = gpio_handler
        self.db = database
        
        # State management
        self.state = EmergencyState.IDLE
        self.previous_state = None
        self.countdown_thread = None
        self.countdown_active = False
        self.countdown_time_remaining = 0
        
        # Fall duration tracking (for 1-minute fall scenario)
        self.fall_start_time = None
        self.fall_duration_threshold = self.config.get('fall_duration_threshold', 60)  # 1 minute in seconds
        self.fall_monitor_thread = None
        self.monitoring_fall = False
        
        # Callbacks
        self.on_emergency_triggered_callback = None
        self.on_state_change_callback = None
        
        # Statistics
        self.emergency_count = 0
        self.false_alarm_count = 0
        
        logger.info("EmergencyController initialized")
        logger.info(f"  Countdown duration: {self.countdown_duration}s")
        logger.info(f"  Contact number: {self.contact_number}")
        logger.info(f"  Actual calls: {'ENABLED' if self.enable_actual_call else 'DISABLED (simulation)'}")
    
    def set_state(self, new_state: EmergencyState, reason: str = ""):
        """
        Change emergency state.
        
        Args:
            new_state: New state to transition to
            reason: Optional reason for state change
        """
        if self.state == new_state:
            return
        
        self.previous_state = self.state
        self.state = new_state
        
        logger.info(f"State changed: {self.previous_state.value} → {new_state.value}")
        if reason:
            logger.info(f"  Reason: {reason}")
        
        # Log to database
        if self.db:
            self.db.add_event(
                event_type=f"emergency_state_{new_state.value}",
                details=f"Transitioned from {self.previous_state.value}: {reason}"
            )
        
        # Update GPIO LEDs based on state
        self._update_leds()
        
        # Notify callback
        if self.on_state_change_callback:
            try:
                self.on_state_change_callback(new_state, self.previous_state)
            except Exception as e:
                logger.error(f"Error in state change callback: {e}")
    
    def trigger_emergency(self, manual: bool = False):
        """
        Trigger emergency immediately.
        
        Args:
            manual: True if triggered by button press (no countdown/flashing)
                   False if triggered by system (countdown applies)
        """
        if manual:
            # Manual button press - go directly to EMERGENCY_ACTIVE (no flashing)
            logger.warning("🔴 MANUAL EMERGENCY TRIGGERED - Calling 999 immediately!")
            self.emergency_count += 1
            
            # Stop any ongoing fall monitoring
            self.monitoring_fall = False
            
            # Go directly to emergency active state (LED2 solid, no flashing)
            self.set_state(EmergencyState.EMERGENCY_ACTIVE, "Manual emergency button pressed")
            
            # Make the call
            self._make_emergency_call(manual=True)
        else:
            # Automatic trigger - use countdown
            self.start_countdown("Automatic emergency trigger")
    
    def _update_leds(self):
        """Update LED states based on current emergency state."""
        if not self.gpio:
            return
        
        try:
            if self.state == EmergencyState.IDLE:
                self.gpio.led_fall_off()
                self.gpio.led_emergency_off()
            
            elif self.state == EmergencyState.FALL_DETECTED:
                self.gpio.led_fall_on()
                self.gpio.led_emergency_off()
            
            elif self.state == EmergencyState.CHECKING_BREATHING:
                self.gpio.led_fall_on()
                self.gpio.led_emergency_off()
            
            elif self.state == EmergencyState.NO_BREATHING:
                self.gpio.led_fall_on()
                self.gpio.led_emergency_off()
            
            elif self.state == EmergencyState.COUNTDOWN_ACTIVE:
                self.gpio.led_fall_on()
                self.gpio.led_emergency_flash()
            
            elif self.state == EmergencyState.COUNTDOWN_CANCELLED:
                self.gpio.led_fall_off()
                self.gpio.led_emergency_off()
            
            elif self.state == EmergencyState.EMERGENCY_ACTIVE:
                self.gpio.led_fall_on()
                self.gpio.led_emergency_solid()
            
            elif self.state == EmergencyState.EMERGENCY_RESOLVED:
                self.gpio.led_fall_off()
                self.gpio.led_emergency_off()
        
        except Exception as e:
            logger.error(f"Error updating LEDs: {e}")
    
    def handle_fall_detected(self, fall_confidence: float = 0.0):
        """
        Handle fall detection event.
        Starts 2-minute monitoring - if fall persists for 2+ minutes, triggers emergency.
        
        Args:
            fall_confidence: Confidence score from fall detector
        """
        if not self.auto_trigger_enabled:
            logger.info("Auto-trigger disabled, ignoring fall detection")
            return
        
        if self.state != EmergencyState.IDLE:
            logger.warning(f"Fall detected but system in state: {self.state.value}")
            return
        
        logger.warning(f"🚨 FALL DETECTED! Confidence: {fall_confidence:.2f}")
        logger.info("Starting 2-minute fall monitoring...")
        
        self.set_state(EmergencyState.FALL_DETECTED, 
                      f"Fall detected with confidence {fall_confidence:.2f}")
        
        # Start 2-minute fall duration monitor
        self.fall_start_time = time.time()
        self.monitoring_fall = True
        self.fall_monitor_thread = threading.Thread(target=self._monitor_fall_duration, daemon=True)
        self.fall_monitor_thread.start()
    
    def _monitor_fall_duration(self):
        """
        Monitor if person has been fallen for 1+ minute.
        If yes, trigger emergency countdown even if breathing.
        PAUSES during breathing check - waits for breathing results first.
        """
        logger.info(f"Fall duration monitor started. Will trigger countdown after {self.fall_duration_threshold}s")
        
        while self.monitoring_fall:
            elapsed = time.time() - self.fall_start_time
            remaining = self.fall_duration_threshold - elapsed
            
            # PAUSE monitoring while checking breathing - wait for results first
            if self.state == EmergencyState.CHECKING_BREATHING:
                logger.debug("Fall monitor paused - waiting for breathing check to complete")
                time.sleep(1)
                continue
            
            # Log every 30 seconds
            if int(elapsed) % 30 == 0 and int(elapsed) > 0:
                logger.info(f"Fall duration: {elapsed:.0f}s / {self.fall_duration_threshold}s")
            
            # Check if 1 minute elapsed
            if elapsed >= self.fall_duration_threshold:
                logger.warning(f"⚠️  FALL DURATION EXCEEDED {self.fall_duration_threshold}s!")
                logger.warning("Triggering emergency countdown (fall > 1 minute)...")
                
                # Trigger countdown after 1 minute fall, even if breathing
                self.monitoring_fall = False
                self.start_countdown(f"Fall duration exceeded {self.fall_duration_threshold}s")
                break
            
            # Check every second
            time.sleep(1)
            
            # Stop if person recovered (state changed back to IDLE)
            if self.state == EmergencyState.IDLE:
                logger.info("Person recovered, stopping fall monitor")
                self.monitoring_fall = False
                break
        
        logger.info("Fall duration monitor stopped")
    
    def stop_fall_monitoring(self):
        """
        Stop fall duration monitoring (person recovered).
        """
        if self.monitoring_fall:
            logger.info("Stopping fall duration monitoring - person recovered")
            self.monitoring_fall = False
            self.fall_start_time = None
            if self.fall_monitor_thread:
                self.fall_monitor_thread = None
    
    def handle_breathing_result(self, breathing_detected: bool, confidence: float = 0.0):
        """
        Handle breathing detection result.
        
        Args:
            breathing_detected: True if breathing was detected
            confidence: Confidence score from breathing detector
        """
        if self.state not in [EmergencyState.FALL_DETECTED, EmergencyState.CHECKING_BREATHING]:
            logger.warning(f"⚠️  Breathing result received in unexpected state: {self.state.value}")
            logger.warning("This might happen if Button 2 was pressed during breathing check")
            return
        
        if breathing_detected:
            logger.warning(f"✅ BREATHING DETECTED (confidence: {confidence:.2f})")
            logger.info("Person is breathing - monitoring fall duration (1 minute threshold)")
            # Continue monitoring - if fall persists 1 min, will still trigger countdown
            # Keep state as FALL_DETECTED, monitoring continues
            if self.state == EmergencyState.CHECKING_BREATHING:
                self.set_state(EmergencyState.FALL_DETECTED, "Breathing OK, monitoring duration")
        else:
            logger.warning("="*60)
            logger.warning(f"❌ NO BREATHING DETECTED! (confidence: {confidence:.2f})")
            logger.warning(f"🚨 Starting {self.countdown_duration}s emergency countdown immediately...")
            logger.warning("💡 LED2 will flash - Press Button 2 to cancel!")
            logger.warning("="*60)
            self.set_state(EmergencyState.NO_BREATHING, "No breathing detected")
            # Stop fall monitoring since we're triggering countdown immediately
            self.monitoring_fall = False
            self.start_countdown("No breathing detected after fall")
    
    def start_countdown(self, reason: str = "Emergency countdown started"):
        """
        Start emergency countdown timer.
        LED2 will flash for countdown_duration (10s), then if not cancelled, trigger emergency.
        
        Args:
            reason: Reason for starting countdown
        """
        if self.countdown_active:
            logger.warning("Countdown already active")
            return
        
        # Stop fall monitoring if active
        self.monitoring_fall = False
        
        self.countdown_active = True
        self.countdown_time_remaining = self.countdown_duration
        self.set_state(EmergencyState.COUNTDOWN_ACTIVE, reason)
        
        # Start countdown in separate thread
        self.countdown_thread = threading.Thread(target=self._countdown_worker, daemon=True)
        self.countdown_thread.start()
    
    def _countdown_worker(self):
        """Countdown worker thread. LED2 flashes during this time."""
        logger.info(f"⏱️  Countdown started: {self.countdown_duration} seconds")
        logger.info("LED2 flashing... Press Button 2 to cancel!")
        
        for i in range(self.countdown_duration, 0, -1):
            if not self.countdown_active:
                logger.info("Countdown cancelled by user")
                return
            
            self.countdown_time_remaining = i
            
            if i <= 5:  # Log final 5 seconds
                logger.warning(f"🚨 Emergency call in {i}...")
            
            time.sleep(1)
        
        # Countdown completed - trigger emergency (LED2 goes solid)
        if self.countdown_active:
            logger.warning("⏰ COUNTDOWN EXPIRED - TRIGGERING EMERGENCY CALL")
            self.countdown_active = False  # Reset flag
            
            # Trigger emergency without manual flag (goes through automatic flow)
            self.emergency_count += 1
            self.set_state(EmergencyState.EMERGENCY_ACTIVE, "Countdown expired")
            self._make_emergency_call(manual=False)
    
    def cancel_countdown(self, reason: str = "User pressed cancel button"):
        """
        Cancel active countdown.
        Both LEDs turn off when cancelled.
        
        Args:
            reason: Reason for cancellation
        """
        if not self.countdown_active:
            logger.warning("No active countdown to cancel")
            return
        
        logger.info(f"✅ Countdown cancelled: {reason}")
        self.countdown_active = False
        self.countdown_time_remaining = 0
        
        # Stop fall monitoring if active
        self.monitoring_fall = False
        
        self.set_state(EmergencyState.COUNTDOWN_CANCELLED, reason)
        
        # Wait for thread to finish
        if self.countdown_thread and self.countdown_thread.is_alive():
            self.countdown_thread.join(timeout=2)
        
        # Return to idle (both LEDs off)
        time.sleep(0.5)
        self.set_state(EmergencyState.IDLE, "Returned to normal monitoring")
        
        self.false_alarm_count += 1
    
    def reset_to_idle(self, reason: str = "User reset system"):
        """
        Reset entire system to IDLE state.
        Button 2 pressed - highest priority, resets everything.
        Stops all monitoring, countdowns, and emergency states.
        Turns off all LEDs.
        
        Args:
            reason: Reason for reset
        """
        logger.warning(f"🔄 SYSTEM RESET: {reason}")
        
        # Stop all active processes
        self.countdown_active = False
        self.monitoring_fall = False
        self.fall_start_time = None
        self.countdown_time_remaining = 0
        
        # Log to database
        if self.db:
            self.db.add_event('system_reset', reason)
        
        # Return to IDLE
        self.set_state(EmergencyState.IDLE, reason)
        logger.info("System reset complete - back to monitoring mode")
    
    def trigger_emergency(self, manual: bool = False):
        """
        Trigger emergency immediately.
        
        Args:
            manual: True if triggered by button press (no countdown/flashing)
                   False if triggered by system (countdown applies)
        """
        if manual:
            # Manual button press - go directly to EMERGENCY_ACTIVE (no flashing)
            logger.warning("🔴 MANUAL EMERGENCY TRIGGERED - Calling 999 immediately!")
            self.emergency_count += 1
            
            # Stop any ongoing fall monitoring
            self.monitoring_fall = False
            
            # Go directly to emergency active state (LED2 solid, no flashing)
            self.set_state(EmergencyState.EMERGENCY_ACTIVE, "Manual emergency button pressed")
            
            # Make the call
            self._make_emergency_call(manual=True)
        else:
            # This should not be called directly for automatic triggers
            # Automatic triggers go through start_countdown() -> _countdown_worker()
            logger.warning("trigger_emergency called with manual=False - use start_countdown() instead")
        
        # Notify callback
        if self.on_emergency_triggered_callback:
            try:
                self.on_emergency_triggered_callback(manual)
            except Exception as e:
                logger.error(f"Error in emergency callback: {e}")
    
    def _make_emergency_call(self, manual: bool):
        """
        Execute emergency call.
        
        Args:
            manual: True if manually triggered
        """
        trigger_type = "MANUAL" if manual else "AUTOMATIC"
        
        if self.enable_actual_call:
            # TODO: Implement actual phone call using Twilio or similar
            logger.critical(f"[{trigger_type}] Making REAL call to {self.contact_number}")
            # Placeholder for actual call implementation
            pass
        else:
            # Simulation mode
            logger.critical(f"[{trigger_type}] SIMULATED call to {self.contact_number}")
            logger.critical("In production, this would trigger actual emergency call")
        
        # Log to database
        if self.db:
            self.db.add_event(
                event_type="emergency_call",
                details=f"{trigger_type} emergency call to {self.contact_number}"
            )
    
    def resolve_emergency(self, reason: str = "User pressed cancel button"):
        """
        Resolve active emergency (turn off emergency LED).
        Both LEDs turn off.
        
        Args:
            reason: Reason for resolution
        """
        if self.state != EmergencyState.EMERGENCY_ACTIVE:
            logger.warning(f"No active emergency to resolve (current state: {self.state.value})")
            return
        
        logger.info(f"✅ Emergency resolved: {reason}")
        
        # Stop fall monitoring if active
        self.monitoring_fall = False
        
        self.set_state(EmergencyState.EMERGENCY_RESOLVED, reason)
        
        # Return to idle (both LEDs off)
        time.sleep(0.5)
        self.set_state(EmergencyState.IDLE, "Returned to normal monitoring")
    
    def get_status(self) -> dict:
        """
        Get current emergency system status.
        
        Returns:
            Dictionary with status information
        """
        return {
            'state': self.state.value,
            'previous_state': self.previous_state.value if self.previous_state else None,
            'countdown_active': self.countdown_active,
            'countdown_remaining': self.countdown_time_remaining,
            'emergency_count': self.emergency_count,
            'false_alarm_count': self.false_alarm_count,
            'manual_trigger_enabled': self.manual_trigger_enabled,
            'auto_trigger_enabled': self.auto_trigger_enabled
        }
    
    def set_emergency_callback(self, callback: Callable):
        """
        Set callback for emergency trigger events.
        
        Args:
            callback: Function to call when emergency triggered
                     Signature: callback(manual: bool) -> None
        """
        self.on_emergency_triggered_callback = callback
    
    def set_state_change_callback(self, callback: Callable):
        """
        Set callback for state change events.
        
        Args:
            callback: Function to call when state changes
                     Signature: callback(new_state: EmergencyState, old_state: EmergencyState) -> None
        """
        self.on_state_change_callback = callback
    
    def reset(self):
        """Reset emergency controller to idle state."""
        logger.info("Resetting emergency controller...")
        
        # Cancel any active countdown
        if self.countdown_active:
            self.cancel_countdown("System reset")
        
        # Reset state
        self.set_state(EmergencyState.IDLE, "System reset")
        
        logger.info("Emergency controller reset complete")
    
    def cleanup(self):
        """Cleanup resources."""
        logger.info("Emergency controller cleanup...")
        
        # Cancel countdown
        if self.countdown_active:
            self.countdown_active = False
            if self.countdown_thread:
                self.countdown_thread.join(timeout=2)
        
        # Turn off LEDs
        if self.gpio:
            self.gpio.led_fall_off()
            self.gpio.led_emergency_off()
        
        logger.info("Emergency controller cleanup complete")


# Standalone test function
def test_emergency_controller():
    """Test emergency controller."""
    print("="*60)
    print("Emergency Controller Test")
    print("="*60)
    
    controller = EmergencyController()
    
    print("\nInitial Status:")
    status = controller.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n--- Simulating fall detection ---")
    controller.handle_fall_detected(fall_confidence=0.92)
    time.sleep(1)
    
    print("\n--- Simulating no breathing detected ---")
    controller.handle_breathing_result(breathing_detected=False, confidence=0.85)
    
    print("\n--- Countdown active for 3 seconds ---")
    time.sleep(3)
    
    print("\n--- Cancelling countdown (user pressed button) ---")
    controller.cancel_countdown("User pressed stop button")
    time.sleep(1)
    
    print("\n--- Testing manual emergency trigger ---")
    controller.trigger_emergency(manual=True)
    time.sleep(2)
    
    print("\n--- Resolving emergency ---")
    controller.resolve_emergency("Help arrived")
    
    print("\nFinal Status:")
    status = controller.get_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    controller.cleanup()
    print("\n✓ Test complete!")


if __name__ == '__main__':
    test_emergency_controller()
