import sys
import os
import time

# Point to the src folder
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import audio

def run_test():
    print("="*40)
    print("🛠️  VIAD AUDIO MODULE TEST")
    print("="*40)

    # 1. Test Output
    print("\n[TEST 1] Testing Voice Output...")
    audio.speak("Audio system test. If you hear this, the speakers are working.")
    
    time.sleep(1)

    # 2. Test Input
    print("\n[TEST 2] Testing Microphone...")
    print("Please say 'Testing 1 2 3' clearly...")
    result = audio.listen()
    
    if result:
        print(f"\n✅ SUCCESS! System heard: '{result}'")
    else:
        print("\n❌ FAILURE: System did not hear or recognize speech.")

if __name__ == "__main__":
    run_test()