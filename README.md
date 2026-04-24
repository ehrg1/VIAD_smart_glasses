# VIAD: Visually Impaired Assistive Device

VIAD is an edge-computing smart glasses wearable designed to assist visually impaired individuals with real-time spatial awareness and complex scene understanding. 

## System Architecture
This system fuses multiple sensor modalities and AI models on a Raspberry Pi:
1. **Offline Obstacle Detection:** Ultrasonic sensors mapped to hardware interrupts for zero-latency proximity warnings.
2. **Edge Computer Vision:** A locally hosted TensorFlow Lite object detection model for identifying hazards without internet reliance.
3. **Cloud Vision-Language Model:** Google Gemini 2.5 Flash integration via USB/Bluetooth microphone arrays to answer complex contextual questions about the user's environment.
4. **Audio Routing:** PulseAudio-to-ALSA bridging for seamless text-to-speech feedback via `espeak-ng`.

## Setup
*(Installation instructions will be  added in future commits)*
