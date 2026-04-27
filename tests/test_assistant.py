import sys
import os
import cv2

# Add root directory to path to allow imports from src/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.assistant import GeminiAssistant
from src.vision import EdgeVision

def test_ai_integration():
    print("--- 🛠️ Starting Gemini 2.5 Flash Integration Test ---")

    # 1. Initialize Vision and Assistant
    try:
        vision = EdgeVision()
        assistant = GeminiAssistant()
        print("✅ Systems Initialized.")
    except Exception as e:
        print(f"❌ Initialization Failed: {e}")
        return

    # 2. Capture a live frame
    print("📸 Capturing frame from camera...")
    frame = vision.capture_frame()
    
    if frame is None:
        print("❌ Camera capture failed.")
        return

    # 3. Perform a test query
    test_prompt = "What do you see in this image? Describe it in one short sentence."
    
    print("📡 Sending to Gemini 2.5 Flash...")
    response = assistant.query(frame, test_prompt)

    # 4. Show Result
    print("\n--- 🤖 AI RESPONSE ---")
    print(response)
    print("----------------------\n")

    # Clean up
    vision.close()
    print("🏁 Test Finished.")

if __name__ == "__main__":
    test_ai_integration()