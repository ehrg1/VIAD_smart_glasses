import cv2
import numpy as np
import time
from ai_edge_litert.interpreter import Interpreter
from picamera2 import Picamera2

class EdgeVision:
    def __init__(self, model_path="models/detect.tflite", label_path="models/labelmap.txt"):
        # 1. Load labels exactly like the working vision_system.py
        try:
            with open(label_path, 'r') as f:
                self.labels = [line.strip() for line in f.readlines() if line.strip()]
            if self.labels[0] == '???':
                del self.labels[0]
        except Exception as e:
            print(f"❌ Label Load Error: {e}")

        # 2. Load the AI Model using the lightweight Edge Runtime
        print("Loading Pretrained AI Model...")
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        self.model_height = self.input_details[0]['shape'][1]
        self.model_width = self.input_details[0]['shape'][2]

        # 3. Start the Pi Camera with native hardware configuration
        print("Initializing Picamera2...")
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_video_configuration(main={"size": (640, 480)}))
        self.picam2.start()
        
        # Give sensor time to adjust to lighting
        time.sleep(2)

    def capture_frame(self):
        """Grabs a frame and converts RGB to BGR for OpenCV compatibility."""
        frame = self.picam2.capture_array()
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    def detect(self, frame, conf_threshold=0.60):
        """Processes a frame and returns detailed detection data."""
        # 4. Preprocess: Resize and use uint8 (Standard for detect.tflite)
        image_resized = cv2.resize(frame, (self.model_width, self.model_height))
        input_data = np.expand_dims(image_resized, axis=0).astype(np.uint8)

        # 5. Run the neural network
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()

        # 6. Extract results using standard SSD MobileNet indices
        # Index 0: Boxes, Index 1: Classes, Index 2: Scores
        boxes = self.interpreter.get_tensor(self.output_details[0]['index'])[0]
        classes = self.interpreter.get_tensor(self.output_details[1]['index'])[0]
        scores = self.interpreter.get_tensor(self.output_details[2]['index'])[0]

        results = []
        for i in range(len(scores)):
            if scores[i] > conf_threshold:
                class_id = int(classes[i])
                if class_id < len(self.labels):
                    results.append({
                        "label": self.labels[class_id],
                        "score": scores[i],
                        "box": boxes[i] # [ymin, xmin, ymax, xmax]
                    })
        
        return results

    def close(self):
        """Gracefully shuts down the camera."""
        print("\nShutting down vision system...")
        self.picam2.stop()