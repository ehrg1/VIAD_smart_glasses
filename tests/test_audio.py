import sys
import os
import time

# Ensure the 'src' directory is in the path so we can import our module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.audio import AudioInterface

def test_audio_system():
    print("--- 🛠️ Starting Audio System Test ---")
    
    # 1. Initialize the Interface
    try:
        audio = AudioInterface()
        print("✅ AudioInterface initialized successfully.")
    except Exception as e:
        print(f"❌ Failed to initialize AudioInterface: {e}")
        return

    # 2. Test Output (TTS)
    print("\n[Step 1/2] Testing Speakers (Output)...")
    test_text = "Testing the V I A D audio system. If you hear this, speakers are working."
    audio.speak(test_text)
    
    # Give the user a moment to prepare for the mic test
    time.sleep(1)

    # 3. Test Input (STT)
    print("\n[Step 2/2] Testing Microphone (Input)...")
    print("Please say clearly: 'Hello Gemini'")
    
    heard_text = audio.listen()

    if heard_text:
        print(f"✅ Success! The Pi heard: '{heard_text}'")
        audio.speak(f"You said: {heard_text}. Test complete.")
    else:
        print("❌ Error: Nothing was heard or understood.")
        audio.speak("I could not hear you. Please check your microphone connection.")

    print("\n--- 🏁 Test Finished ---")

if __name__ == "__main__":
    test_audio_system()