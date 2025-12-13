#!/usr/bin/env python3
"""
Test Emergency Logic
Tests the complete emergency response workflow including:
- Button presses
- LED states
- 2-minute fall detection
- Countdown and cancellation
"""

import sys
import time
import yaml
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gpio_handler import GPIOHandler
from src.emergency_controller import EmergencyController, EmergencyState
from src.database import Database

def print_separator():
    print("\n" + "="*60 + "\n")

def print_status(emergency):
    """Print current emergency system status."""
    print(f"State: {emergency.state.value}")
    print(f"Countdown Active: {emergency.countdown_active}")
    print(f"Fall Monitoring: {emergency.monitoring_fall}")
    if emergency.countdown_active:
        print(f"Time Remaining: {emergency.countdown_time_remaining}s")

def test_scenario_1_manual_emergency():
    """Test Scenario 1: Manual emergency button press."""
    print_separator()
    print("TEST 1: MANUAL EMERGENCY BUTTON PRESS")
    print("Expected: LED2 goes SOLID immediately (no flashing)")
    print_separator()
    
    # Setup
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    gpio = GPIOHandler(config['gpio'])
    db = Database(config['storage']['database_path'])
    emergency = EmergencyController(config_path, gpio, db)
    
    print("Initial state:")
    print_status(emergency)
    
    print("\n➡️  Simulating Button 1 press (Manual Emergency)...")
    emergency.trigger_emergency(manual=True)
    
    print("\nState after Button 1 press:")
    print_status(emergency)
    print("\n✓ Check: LED2 should be SOLID (not flashing)")
    
    time.sleep(3)
    
    print("\n➡️  Simulating Button 2 press (Cancel)...")
    emergency.resolve_emergency("User pressed cancel")
    
    print("\nFinal state:")
    print_status(emergency)
    print("✓ Check: Both LEDs should be OFF")
    
    gpio.cleanup()
    print_separator()

def test_scenario_2_fall_duration():
    """Test Scenario 2: Fall detected for 2+ minutes."""
    print_separator()
    print("TEST 2: FALL DURATION (2+ MINUTES)")
    print("Note: This test will simulate 2 minutes in 10 seconds")
    print("Expected: LED1 ON → wait → LED2 FLASHING → LED2 SOLID")
    print_separator()
    
    # Setup
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    gpio = GPIOHandler(config['gpio'])
    db = Database(config['storage']['database_path'])
    emergency = EmergencyController(config_path, gpio, db)
    
    # Override for testing (reduce 2 minutes to 10 seconds)
    emergency.fall_duration_threshold = 10
    print(f"⚡ Test mode: Fall threshold set to {emergency.fall_duration_threshold}s (normally 120s)")
    
    print("\nInitial state:")
    print_status(emergency)
    
    print("\n➡️  Simulating fall detection...")
    emergency.handle_fall_detected(fall_confidence=0.95)
    
    print("\nState after fall detection:")
    print_status(emergency)
    print("✓ Check: LED1 should be ON")
    
    print(f"\n⏱️  Waiting {emergency.fall_duration_threshold} seconds for fall duration threshold...")
    for i in range(emergency.fall_duration_threshold):
        time.sleep(1)
        if i % 3 == 0:
            print(f"   {i}s elapsed...")
    
    time.sleep(2)  # Wait for countdown to start
    
    print("\nState after 2 minutes of fall:")
    print_status(emergency)
    print("✓ Check: LED2 should be FLASHING")
    
    print("\n⏱️  Countdown running for 5 seconds...")
    time.sleep(5)
    
    print("\n➡️  Simulating Button 2 press (Cancel countdown)...")
    emergency.cancel_countdown("User pressed cancel during countdown")
    
    time.sleep(2)
    
    print("\nFinal state:")
    print_status(emergency)
    print("✓ Check: Both LEDs should be OFF")
    
    gpio.cleanup()
    print_separator()

def test_scenario_3_countdown_expire():
    """Test Scenario 3: Countdown expires without cancellation."""
    print_separator()
    print("TEST 3: COUNTDOWN EXPIRES (NO CANCELLATION)")
    print("Expected: Fall → LED1 ON → LED2 FLASHING → LED2 SOLID")
    print_separator()
    
    # Setup
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    gpio = GPIOHandler(config['gpio'])
    db = Database(config['storage']['database_path'])
    emergency = EmergencyController(config_path, gpio, db)
    
    # Override for testing
    emergency.fall_duration_threshold = 5  # 5 seconds instead of 2 minutes
    emergency.countdown_duration = 5  # 5 seconds instead of 10
    
    print(f"⚡ Test mode: Fall threshold={emergency.fall_duration_threshold}s, Countdown={emergency.countdown_duration}s")
    
    print("\n➡️  Simulating fall detection...")
    emergency.handle_fall_detected(fall_confidence=0.92)
    
    print("\nState after fall detection:")
    print_status(emergency)
    print("✓ Check: LED1 should be ON")
    
    print(f"\n⏱️  Waiting for fall duration threshold ({emergency.fall_duration_threshold}s)...")
    time.sleep(emergency.fall_duration_threshold + 2)
    
    print("\nState during countdown:")
    print_status(emergency)
    print("✓ Check: LED2 should be FLASHING")
    
    print(f"\n⏱️  Waiting for countdown to expire ({emergency.countdown_duration}s)...")
    time.sleep(emergency.countdown_duration + 2)
    
    print("\nFinal state after countdown expired:")
    print_status(emergency)
    print("✓ Check: LED2 should be SOLID (calling 999)")
    
    time.sleep(2)
    
    print("\n➡️  Simulating Button 2 press (Cancel emergency)...")
    emergency.resolve_emergency("User pressed cancel")
    
    time.sleep(2)
    
    print("\nFinal state:")
    print_status(emergency)
    print("✓ Check: Both LEDs should be OFF")
    
    gpio.cleanup()
    print_separator()

def interactive_test():
    """Interactive test with real buttons and LEDs."""
    print_separator()
    print("INTERACTIVE TEST: REAL BUTTON AND LED TEST")
    print("This test uses your actual hardware connections")
    print_separator()
    
    # Setup
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    gpio = GPIOHandler(config['gpio'])
    db = Database(config['storage']['database_path'])
    emergency = EmergencyController(config_path, gpio, db)
    
    # Override for testing
    emergency.fall_duration_threshold = 10  # 10 seconds
    
    # Setup callbacks for buttons
    def on_button1():
        print("\n🔴 Button 1 pressed - Triggering manual emergency!")
        emergency.trigger_emergency(manual=True)
    
    def on_button2():
        print("\n🟢 Button 2 pressed - Cancelling!")
        if emergency.countdown_active:
            emergency.cancel_countdown("User pressed cancel button")
        elif emergency.state == EmergencyState.EMERGENCY_ACTIVE:
            emergency.resolve_emergency("User pressed cancel button")
        else:
            print("   (No active emergency to cancel)")
    
    gpio.setup_buttons(on_button1, on_button2)
    
    print("\n✅ System ready! Try the following:")
    print("\n1. Press Button 1 (Manual Emergency):")
    print("   → LED2 should go SOLID immediately")
    print("   → Press Button 2 to cancel")
    print("\n2. Wait for simulated fall test:")
    print("   → LED1 will turn ON")
    print("   → After 10s, LED2 will start FLASHING")
    print("   → Press Button 2 to cancel, or wait for LED2 to go SOLID")
    print("\nPress Ctrl+C to exit\n")
    
    try:
        # Simulate a fall after 5 seconds
        print("⏱️  Simulating fall detection in 5 seconds...")
        time.sleep(5)
        
        print("\n🚨 FALL DETECTED!")
        emergency.handle_fall_detected(fall_confidence=0.90)
        
        # Keep running to allow button presses
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n\n✅ Test ended by user")
        emergency.monitoring_fall = False
        emergency.countdown_active = False
        gpio.cleanup()
        print_separator()

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("  EMERGENCY LOGIC TEST SUITE")
    print("="*60)
    
    print("\nThis test suite will verify:")
    print("  ✓ Manual emergency button (Button 1)")
    print("  ✓ Cancel button (Button 2)")
    print("  ✓ 2-minute fall detection")
    print("  ✓ LED flashing and solid states")
    print("  ✓ Countdown and cancellation")
    
    print("\nSelect test mode:")
    print("  1. Test Scenario 1: Manual Emergency")
    print("  2. Test Scenario 2: Fall Duration (2 min)")
    print("  3. Test Scenario 3: Countdown Expires")
    print("  4. Interactive Test (Real Hardware)")
    print("  5. Run All Automated Tests")
    
    try:
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            test_scenario_1_manual_emergency()
        elif choice == '2':
            test_scenario_2_fall_duration()
        elif choice == '3':
            test_scenario_3_countdown_expire()
        elif choice == '4':
            interactive_test()
        elif choice == '5':
            test_scenario_1_manual_emergency()
            time.sleep(2)
            test_scenario_2_fall_duration()
            time.sleep(2)
            test_scenario_3_countdown_expire()
        else:
            print("Invalid choice")
            return
        
        print("\n✅ All tests completed!")
        
    except KeyboardInterrupt:
        print("\n\n❌ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
