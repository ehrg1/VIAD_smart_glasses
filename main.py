import time
import cv2
import sys
import threading
from src.hardware import SmartGlassesHW
from src.vision import EdgeVision
from src.audio import AudioInterface
from src.assistant import GeminiAssistant

class VIADSystem:
    def __init__(self):
        print("🔧 Initializing VIAD Modules...")
        # Initialize hardware, vision, audio, and Gemini
        self.hw = SmartGlassesHW()
        self.vision = EdgeVision()
        self.audio = AudioInterface()
        self.assistant = GeminiAssistant()
        
        # System State
        self.is_busy = False
        self.current_dist = 100.0  # Shared distance value
        self.last_alert_time = 0
        self.alert_cooldown = 4.0  # Seconds between voice alerts
        self.window_name = "VIAD Live Feed"

    def distance_worker(self):
        """Background thread to keep the sensor active independently of the AI."""
        while True:
            if not self.is_busy:
                dist = self.hw.get_distance()
                # Only update if the reading is valid
                if dist > 0:
                    self.current_dist = dist
            time.sleep(0.05)

    def trigger_ai_assistant(self):
        """Triggered by the physical button on GPIO 26."""
        if self.is_busy:
            return
            
        self.is_busy = True
        self.audio.speak("Button Pressed, wait")
        
        # 1. Listen for voice question
        question = self.audio.listen()
        
        if question:
            print(f"📡 Querying Gemini: {question}")
            # 2. Capture a frame for Gemini context
            frame = self.vision.capture_frame()
            # 3. Get response from Gemini 2.5 Flash
            answer = self.assistant.query(frame, question)
            # 4. Speak result
            self.audio.speak(answer)
        else:
            self.audio.speak("I didn't catch that.")
            
        self.is_busy = False

    def start(self):
        print("🚀 VIAD Smart Glasses System: ONLINE")
        
        # Set up button interrupt
        self.hw.set_button_callback(self.trigger_ai_assistant)
        
        # Start distance sensor thread
        t = threading.Thread(target=self.distance_worker, daemon=True)
        t.start()
        
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        
        try:
            while True:
                # 1. Capture frame
                frame = self.vision.capture_frame()
                if frame is None:
                    continue

                if not self.is_busy:
                    # 2. Local Object Detection (SSD MobileNet)
                    detections = self.vision.detect(frame)
                    
                    # 3. Get labels for the Smart Alert
                    labels = [det.get('label', '').lower() for det in detections]
                    
                    # 4. Smart Audio Alert Logic
                    if 0 < self.current_dist < 100:
                        now = time.time()
                        if now - self.last_alert_time > self.alert_cooldown:
                            
                            dist_speech = int(self.current_dist)
                            if labels:
                                obstacle = labels[0]
                                msg = f"Careful, {obstacle} at {dist_speech} centimeters"
                            else:
                                msg = f"Careful, obstacle at {dist_speech} centimeters"
                            
                            # Speak in background to keep GUI smooth
                            threading.Thread(target=self.audio.speak, args=(msg,), daemon=True).start()
                            self.last_alert_time = now

                    # 5. Drawing the GUI
                    for det in detections:
                        label = det.get('label', 'Object')
                        box = det.get('box', None)
                        
                        # CRITICAL FIX: NumPy array truth value check
                        if box is not None:
                            h, w, _ = frame.shape
                            ymin, xmin, ymax, xmax = box
                            l, t, r, b = int(xmin*w), int(ymin*h), int(xmax*w), int(ymax*h)
                            
                            # Draw detection box and info
                            cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)
                            cv2.putText(frame, f"{label} | {int(self.current_dist)}cm", (l, t-10), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                    # Visual danger indicator
                    if self.current_dist < 40:
                        cv2.putText(frame, "CLOSE PROXIMITY", (50, 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                # 6. Show the feed
                cv2.imshow(self.window_name, frame)
                
                # Check for 'q' to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            print(f"💥 System Crash: {e}")
            self.shutdown()

    def shutdown(self):
        print("\n🛑 Shutting down VIAD...")
        cv2.destroyAllWindows()
        self.vision.close()
        sys.exit(0)

if __name__ == "__main__":
    viad = VIADSystem()
    viad.start()