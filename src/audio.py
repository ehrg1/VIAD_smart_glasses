import subprocess
import speech_recognition as sr

def find_microphone_index():
    """
    Dynamically scans for the best audio input.
    Prioritizes 'pulse' for Bluetooth headsets, then 'default', then USB.
    """
    try:
        mic_list = sr.Microphone.list_microphone_names()
        
        # 1. Search for PulseAudio (Ideal for Bluetooth on Raspberry Pi)
        for index, name in enumerate(mic_list):
            if "pulse" in name.lower():
                print(f"✅ Bluetooth/Pulse Bridge detected at Index {index}")
                return index
                
        # 2. Search for the System Default
        for index, name in enumerate(mic_list):
            if "default" in name.lower():
                print(f"✅ Using Default System Input at Index {index}")
                return index

        # 3. Search for common USB microphone keywords
        for index, name in enumerate(mic_list):
            if any(key in name.lower() for key in ["usb", "pnp", "mic"]):
                print(f"✅ USB Microphone detected: {name} at Index {index}")
                return index
    except Exception as e:
        print(f"⚠️ Error scanning microphones: {e}")
    
    print("ℹ️ No specific device found. Falling back to Index 0.")
    return 0

def speak(text):
    """
    Uses espeak-ng to announce text through the connected Bluetooth/Audio output.
    """
    print(f"🎙️ SPEAKING: {text}")
    try:
        # -s: speed (150 is normal)
        # -v: voice (en+m1 is English male)
        subprocess.run(['espeak-ng', '-s', '150', '-v', 'en+m1', text], check=True)
    except Exception as e:
        print(f"❌ Text-to-Speech Error: {e}")

def listen():
    """
    Finds the microphone, adjusts for background noise, and converts speech to text.
    """
    recognizer = sr.Recognizer()
    target_index = find_microphone_index()
    
    # We wrap the Microphone in a try/except to prevent 'NoneType' crashes
    try:
        with sr.Microphone(device_index=target_index) as source:
            print("👂 Adjusting for ambient noise... (Stay silent)")
            # 1.0 seconds is safer for Bluetooth latency/static
            recognizer.adjust_for_ambient_noise(source, duration=1.0)
            
            print("🎙️ Listening now...")
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            
            print("🔍 Processing speech...")
            text = recognizer.recognize_google(audio_data)
            return text
            
    except sr.WaitTimeoutError:
        print("⚠️ Listening timed out: No speech detected.")
        return None
    except sr.UnknownValueError:
        print("⚠️ Speech Recognition could not understand the audio.")
        return None
    except Exception as e:
        print(f"❌ Microphone Error: {e}")
        return None

if __name__ == "__main__":
    # Quick self-test if run directly
    speak("Testing the integrated audio module.")
    heard = listen()
    if heard:
        speak(f"You said: {heard}")