import subprocess
import speech_recognition as sr

def speak(text):
    """Uses espeak-ng to announce text through the earbuds."""
    print(f"🎙️ SPEAKING: {text}")
    try:
        # Using the m1 male voice at speed 150
        subprocess.run(['espeak-ng', '-s', '150', '-v', 'en+m1', text], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Audio Command Failed! Error Code: {e.returncode}")

def listen():
    """Listens to the USB microphone and returns recognized text."""
    recognizer = sr.Recognizer()
    # Based on your setup, the USB mic is usually at index 7
    with sr.Microphone(device_index=1) as source:
        print("👂 Listening for your question...")
        try:
            # Adjusting for ambient noise helps accuracy
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio_data = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            
            print("🔍 Processing speech...")
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.WaitTimeoutError:
            print("⚠️ Listening timed out.")
            return None
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio.")
            return None
        except Exception as e:
            print(f"❌ Microphone Error: {e}")
            return None