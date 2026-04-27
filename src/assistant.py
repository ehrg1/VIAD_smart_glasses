import os
import cv2
import PIL.Image
from dotenv import load_dotenv
from google import genai

# Load environment variables from .env
load_dotenv()

class GeminiAssistant:
    def __init__(self):
        """
        Initializes the Gemini 2.5 Flash client using the API key from .env.
        """
        self.api_key = os.getenv("GEMINI_API_KEY")
        
        if not self.api_key:
            raise ValueError("❌ ERROR: GEMINI_API_KEY not found in .env file.")

        # Initialize the modern GenAI Client
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.5-flash"

    def query(self, frame, user_question):
        """
        Sends a frame and a voice-transcribed question to Gemini 2.5 Flash.
        """
        # Convert OpenCV BGR to RGB for PIL/Gemini
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(rgb_frame)
        
        print(f"🧠 [Gemini 2.5] Analyzing frame with question: '{user_question}'")
        
        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[user_question, img]
            )
            return response.text
        except Exception as e:
            return f"Brain connection error: {str(e)}"