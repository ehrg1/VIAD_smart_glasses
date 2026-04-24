import cv2
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.vision import EdgeVision

def run_test():
    vision = EdgeVision()
    print("🚀 Drawing Mode Active. Press 'q' to quit.")

    try:
        while True:
            frame = vision.capture_frame()
            h, w, _ = frame.shape
            
            # Get the detailed results
            results = vision.detect(frame)
            
            for obj in results:
                # 1. Unpack data
                label = obj['label']
                conf = obj['score'] * 100
                ymin, xmin, ymax, xmax = obj['box']

                # 2. Convert normalized coordinates to pixel coordinates
                left = int(xmin * w)
                right = int(xmax * w)
                top = int(ymin * h)
                bottom = int(ymax * h)

                # 3. Draw the Rectangle
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

                # 4. Draw the Label and Confidence %
                label_text = f"{label}: {conf:.1f}%"
                cv2.putText(frame, label_text, (left, top - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow('Smart Glasses Vision System', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        vision.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    run_test()