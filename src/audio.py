import subprocess
import speech_recognition as sr

class AudioInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.mic_index = self._find_microphone_index()

    def _find_microphone_index(self):
        """Internal scan for the best audio input."""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            # Priority: Pulse (BT) -> Default -> USB
            for index, name in enumerate(mic_list):
                if any(key in name.lower() for key in ["pulse", "usb", "mic"]):
                    print(f"✅ Mic detected: {name} at Index {index}")
                    return index
        except Exception as e:
            print(f"⚠️ Error scanning microphones: {e}")
        return 0

    def speak(self, text):
        """Uses espeak-ng for low-latency TTS on Pi 4."""
        print(f"🎙️ SPEAKING: {text}")
        try:
            # -s 150 (speed), -v en+m3 (English male voice 3)
            subprocess.run(['espeak-ng', '-s', '160', '-v', 'en+m3', text], check=True)
        except Exception as e:
            print(f"❌ TTS Error: {e}")

    def listen(self):
        """Captures voice and converts to text."""
        try:
            with sr.Microphone(device_index=self.mic_index) as source:
                print("👂 Adjusting... (Stay silent)")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                
                print("🎙️ Listening...")
                self.speak("I am listening")
                # timeout=5: wait 5s for speech to start
                # phrase_time_limit=8: record for max 8s
                audio_data = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)
                
                print("🔍 Processing...")
                return self.recognizer.recognize_google(audio_data)
                
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return None
        except Exception as e:
            print(f"❌ Mic Error: {e}")
            return None