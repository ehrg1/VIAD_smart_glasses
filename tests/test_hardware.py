import sys
import os
import time

# Add the project root to the sys.path so we can import 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.hardware import SmartGlassesHW

def test_button_press():
    """Callback function to verify the interrupt works."""
    print("\n🟢 [SUCCESS] Button physically pressed! Interrupt triggered.")

def run_hardware_test():
    print("="*45)
    print("🛠️  VIAD SYSTEM: HARDWARE INTEGRATION TEST")
    print("="*45)
    
    try:
        # Initialize the hardware class
        # Pins: Button=26, Trigger=17, Echo=27
        hw = SmartGlassesHW()
        print("✅ Hardware Class Initialized.")
        
        # Attach the test callback to the button
        hw.set_button_callback(test_button_press)
        
        print("\nINSTRUCTIONS:")
        print("1. Press the physical button on GPIO 26.")
        print("2. Move an object toward/away from the ultrasonic sensor.")
        print("3. Press Ctrl+C to finish the test.\n")
        print("-" * 45)

        while True:
            # Test the ultrasonic sensor
            distance = hw.get_distance()
            
            # Formatting the output to stay on one line
            print(f"📡 Current Distance: {distance:6.2f} cm", end="\r")
            
            # Check for very close obstacles (Safety test)
            if distance < 20.0:
                print(f"\n⚠️ WARNING: Object detected at {distance:.2f} cm!")
            
            time.sleep(0.5)

    except FileNotFoundError:
        print("\n❌ ERROR: Could not find the hardware. Is the Pi GPIO configured?")
    except KeyboardInterrupt:
        print("\n\n🛑 Test stopped by user. Cleaning up...")
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")

if __name__ == "__main__":
    run_hardware_test()