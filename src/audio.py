import asyncio
import os
import subprocess
import threading

import speech_recognition as sr

# Lazy on-disk cache for neural-voice alerts. The first time a particular
# (label, distance_bucket) is encountered we speak it via espeak (instant)
# AND synthesize the same phrase with edge-tts in the background, saving the
# MP3 to disk. Every subsequent occurrence plays from disk — Microsoft neural
# Arabic quality at ~80 ms latency, fully offline once warmed up.
_CACHE_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "sounds", "cache")
)


class AudioInterface:
    def __init__(self, language="en"):
        self.recognizer = sr.Recognizer()
        self.mic_index = self._find_microphone_index()
        self.language = language
        # Serializes TTS playback so utterances never overlap.
        self._speak_lock = threading.Lock()
        # Guards _synth_pending across alert + worker threads.
        self._synth_pending_lock = threading.Lock()
        self._synth_pending = set()

        if language == "ar":
            self.espeak_voice = "ar"
            self.stt_locale = "ar-SA"
            self.listening_prompt = "أنا أستمع"
            self.edge_voice = "ar-SA-HamedNeural"
        else:
            self.espeak_voice = "en+m3"
            self.stt_locale = "en-US"
            self.listening_prompt = "I am listening"
            self.edge_voice = "en-US-GuyNeural"

        self.cache_dir = os.path.join(_CACHE_ROOT, language)
        os.makedirs(self.cache_dir, exist_ok=True)

    def _find_microphone_index(self):
        """Internal scan for the best audio input."""
        try:
            mic_list = sr.Microphone.list_microphone_names()
            for index, name in enumerate(mic_list):
                if any(key in name.lower() for key in ["pulse", "usb", "mic"]):
                    print(f"✅ Mic detected: {name} at Index {index}")
                    return index
        except Exception as e:
            print(f"⚠️ Error scanning microphones: {e}")
        return 0

    def speak(self, text):
        """Speak text via espeak-ng. Blocking, serialized."""
        with self._speak_lock:
            print(f"🎙️ SPEAKING: {text}")
            try:
                subprocess.run(
                    ['espeak-ng', '-s', '160', '-v', self.espeak_voice, text],
                    check=True,
                )
            except Exception as e:
                print(f"❌ TTS Error: {e}")

    def speak_alert(self, text):
        """Generic time-sensitive alert via espeak (used for non-templated messages).

        Skips if audio is already busy so stale alerts don't queue up.
        """
        if not self._speak_lock.acquire(blocking=False):
            print(f"⏭️  Skipping alert (audio busy): {text}")
            return
        try:
            print(f"🎙️ SPEAKING (alert): {text}")
            subprocess.run(
                ['espeak-ng', '-s', '170', '-v', self.espeak_voice, text],
                check=True,
            )
        except Exception as e:
            print(f"❌ TTS Error: {e}")
        finally:
            self._speak_lock.release()

    def speak_obstacle_alert(self, label, distance_cm):
        """Voice an obstacle alert. Plays from cache if available, otherwise
        falls back to espeak now and builds the cache in the background for
        next time.
        """
        if not self._speak_lock.acquire(blocking=False):
            print(f"⏭️  Skipping alert (audio busy): {label} @ {distance_cm}cm")
            return
        try:
            bucket = self._bucket_distance(distance_cm)
            cache_path = self._cache_path(label, bucket)

            if os.path.isfile(cache_path):
                print(f"🎙️ ALERT (cached): {os.path.basename(cache_path)}")
                subprocess.run(
                    ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet',
                     cache_path],
                    check=False,
                )
                return

            # Cache miss: speak espeak NOW so we're not silent, and kick off a
            # background neural synth that will populate the cache for later.
            msg = self._format_alert_text(label, bucket)
            print(f"🎙️ ALERT (espeak, caching '{os.path.basename(cache_path)}'): {msg}")
            subprocess.run(
                ['espeak-ng', '-s', '170', '-v', self.espeak_voice, msg],
                check=False,
            )
            self._kick_off_cache_build(label, bucket, cache_path)
        except Exception as e:
            print(f"❌ TTS Error: {e}")
        finally:
            self._speak_lock.release()

    @staticmethod
    def _bucket_distance(distance_cm):
        """Floor-bucket to nearest 10 cm with a min of 10.

        Floor is safer than round for alerts — under-reports rather than
        over-reports the distance.
        """
        return max(10, (int(distance_cm) // 10) * 10)

    def _cache_path(self, label, bucket):
        key = (label or "obstacle").lower().replace(" ", "_")
        return os.path.join(self.cache_dir, f"{key}_{bucket}.mp3")

    def _format_alert_text(self, label, dist_cm):
        if self.language == "ar":
            noun = label if label else "عائق"
            return f"احذر، {noun} على بعد {dist_cm} سنتيمتر"
        noun = label if label else "obstacle"
        return f"Careful, {noun} at {dist_cm} centimeters"

    def _kick_off_cache_build(self, label, bucket, cache_path):
        """Spawn a background thread to synth + save the missing cache entry.

        De-duplicates concurrent misses for the same key so we don't fire off
        multiple edge-tts requests for the same phrase.
        """
        key = (self.language, label or "", bucket)
        with self._synth_pending_lock:
            if key in self._synth_pending or os.path.isfile(cache_path):
                return
            self._synth_pending.add(key)

        threading.Thread(
            target=self._build_cache_entry,
            args=(key, label, bucket, cache_path),
            daemon=True,
        ).start()

    def _build_cache_entry(self, key, label, bucket, cache_path):
        try:
            text = self._format_alert_text(label, bucket)
            tmp_path = cache_path + ".tmp"
            asyncio.run(self._edge_synth(text, tmp_path))
            os.replace(tmp_path, cache_path)  # atomic, so partial files never get played
            print(f"💾 Cached alert: {os.path.basename(cache_path)}")
        except Exception as e:
            print(f"⚠️ Cache build failed for {key}: {e}")
            try:
                os.remove(cache_path + ".tmp")
            except OSError:
                pass
        finally:
            with self._synth_pending_lock:
                self._synth_pending.discard(key)

    async def _edge_synth(self, text, out_path):
        import edge_tts
        c = edge_tts.Communicate(text, self.edge_voice)
        await c.save(out_path)

    def listen(self):
        """Captures voice and converts to text."""
        try:
            with sr.Microphone(device_index=self.mic_index) as source:
                print("👂 Adjusting... (Stay silent)")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.0)

                print("🎙️ Listening...")
                self.speak(self.listening_prompt)
                audio_data = self.recognizer.listen(source, timeout=5, phrase_time_limit=8)

                print("🔍 Processing...")
                return self.recognizer.recognize_google(audio_data, language=self.stt_locale)

        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return None
        except Exception as e:
            print(f"❌ Mic Error: {e}")
            return None
