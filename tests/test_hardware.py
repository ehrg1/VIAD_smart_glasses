import sys
import os
import time
import RPi.GPIO as GPIO

# Point Python to the root directory so it can find the 'src' folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import hardware

def button_callback(channel):
    print("\n🟢 [TEST SUCCESS] Button was physically pressed! Interrupts are working.")

def run_test():
    print("="*40)
    print("🛠️  VIAD HARDWARE COMPONENT TEST")
    print("="*40)
    
    hardware.setup_gpio()
    
    # Attach a temporary test event to your button
    GPIO.add_event_detect(hardware.BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=1000)
    
    print("1. Press the physical button to test the interrupt.")
    print("2. Wave your hand in front of the ultrasonic sensor.")
    print("Press Ctrl+C to exit.\n")
    
    try:
        while True:
            dist = hardware.get_distance()
            print(f"📡 Sensor Distance: {dist} cm")
            time.sleep(0.5)  # Update twice a second
            
    except KeyboardInterrupt:
        print("\n🛑 Test stopped by user.")
    finally:
        hardware.cleanup()

if __name__ == "__main__":
    run_test()