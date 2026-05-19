# VIAD: Vision Integrated Assistive Device

> AI-powered Smart glasses we built to help visually impaired people navigate safely and understand their surroundings using AI.

Submitted to Qassim University in partial fulfillment of the requirements for the degree of B.Sc. in Computer Science, Department of Computer Science, 1447/1448 (2025/2026).

**Students:** Rayan Altawijari | Faris Alsuhibani | Mohammed Alsharekh | Mohaya Almutairi | Abdullah Alfayez  
**Supervisor:** Dr. Ali Mustafa Qamar Khan  
**Qassim University — Computer Science, 2025/2026**

---

## Table of Contents

- [Overview](#overview)
- [Motivation](#motivation)
- [System Architecture](#system-architecture)
- [Hardware Requirements](#hardware-requirements)
- [System Setup](#system-setup)
- [Software Environment](#software-environment)
- [Model & API Setup](#model--api-setup)
- [Project Structure](#project-structure)
- [Operating Instructions](#operating-instructions)
- [How It Works](#how-it-works)
  - [Safety Loop](#safety-loop-continuous--offline)
  - [Cognitive Loop](#cognitive-loop-on-demand--online)
  - [Bilingual Operation](#bilingual-operation)
- [Test Results](#test-results)
- [GPIO Pin Reference](#gpio-pin-reference)
- [Troubleshooting](#troubleshooting)
- [Future Work](#future-work)

---

## Overview

VIAD is a wearable assistive device built into a glasses frame, designed to enhance the spatial awareness and independence of visually impaired users. It uses a **Dual-Loop Architecture**:

1. **Safety Loop (Local)** — Runs continuously without any user input. Uses an HC-SR04 ultrasonic sensor and a locally hosted SSD-MobileNet V2 model to detect nearby obstacles and announce them by name and distance (e.g., *"Careful, chair at 50 centimeters"*). Operates fully offline.

2. **Cognitive Loop (Cloud)** — Triggered on demand by a physical button. Captures a camera frame, sends it with the user's voice question to **Google Gemini Flash**, and speaks the response aloud. Requires an internet connection.

Unlike existing solutions such as smart canes (which only detect ground-level obstacles) or commercial smart glasses (which are expensive and internet-dependent), VIAD provides hands-free, head-level protection with both offline safety and online contextual understanding in a single affordable wearable device.

---

## Motivation

Around 295 million people worldwide live with moderate to severe visual impairment, with approximately 43 million classified as legally blind. Existing tools such as white canes and guide dogs have critical limitations — canes only detect obstacles within reach and miss head-level hazards like signs or branches. Commercial alternatives like the OrCam MyEye or Ray-Ban Meta glasses can cost upwards of $2,000 and still rely on internet connectivity.

VIAD was built to address these gaps by providing a reliable, affordable, and offline-capable assistive device using a Raspberry Pi and open-source AI models.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        VIAD System (main.py)                    │
│                                                                 │
│  ┌──────────────┐    ┌─────────────────────────────────────┐   │
│  │  Safety Loop │    │           Main Loop Thread          │   │
│  │  Background  │    │                                     │   │
│  │   Thread     │    │  ┌──────────┐   ┌────────────────┐ │   │
│  │              │    │  │ picamera2│──▶│ SSD-MobileNet  │ │   │
│  │  HC-SR04     │───▶│  │  Frame   │   │   V2 (TFLite)  │ │   │
│  │  Ultrasonic  │    │  └──────────┘   └───────┬────────┘ │   │
│  │  Sensor      │    │                          │          │   │
│  │  ~150ms      │    │  Smart Alert: label +    │          │   │
│  │  latency     │    │  distance → espeak-ng    │          │   │
│  └──────────────┘    └──────────────────┬───────┘          │   │
│                                         │ Button (GPIO 26)  │   │
│                      ┌──────────────────▼──────────────────┐   │
│                      │      Cognitive Loop (Cloud)         │   │
│                      │  Listen → Capture → Gemini → Speak  │   │
│                      │        ~2.5s avg response           │   │
│                      └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Hardware Requirements

| Component | Details |
|-----------|---------|
| Raspberry Pi 4B | Main controller, 4GB RAM recommended |
| Pi Camera Module | Connected via CSI port |
| HC-SR04 Ultrasonic Sensor | Placed at the bridge of the glasses frame, GPIO 23 (Trig), GPIO 24 (Echo) |
| Tactile Button | GPIO 26, triggers the Gemini assistant |
| Bluetooth Earbuds | Wireless audio output — keeps hands free and ensures privacy |
| USB Microphone | For voice input |
| 3D-Printed Wayfarer Frame | Modified frame housing all components |
| Portable 5V/3A Power Bank | Keeps Pi running under full detection + AI load |

> The ultrasonic sensor is positioned at the bridge of the glasses for a clear, forward-looking view that matches the user's line of sight. GPIO pins 23, 24, and 26 were selected specifically to ensure snappy hardware interrupts for the tactile button.

---

## System Setup

Run these commands to install the core drivers and speech engine:

```bash
sudo apt update
sudo apt install python3-pip python3-venv build-essential libcap-dev portaudio19-dev swig liblgpio-dev espeak-ng ffmpeg pulseaudio flac -y
```

> `ffmpeg` provides `ffplay`, which the audio module uses to play the cached neural-voice alert MP3s.

---

## Software Environment

Execute these steps inside your project folder to set up the virtual environment with access to system camera drivers:

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
```

> `--system-site-packages` is required to inherit system-compiled packages like `picamera2` and `numpy`.

---

## Model & API Setup

**1. Download the Edge Model (SSD-MobileNet V2, COCO):**

```bash
mkdir -p models && cd models
wget https://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
unzip *.zip && rm *.zip
cd ..
```

**2. Set your API Key:**
> you can use this method or follow instruction in .env.example.
```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

> Get a free API key at [Google AI Studio](https://aistudio.google.com/). For a permanent setup, add the export line to your `~/.bashrc`.

---

## Project Structure

```
VIAD_smart_glasses/
├── main.py               # Orchestrator — language picker, multithreading, data flow
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variable template
├── .gitignore
├── models/               # SSD-MobileNet V2 TFLite model and label map
├── sounds/
│   └── cache/            # Pre-built neural-voice alert MP3s (en/ + ar/)
├── src/
│   ├── hardware.py       # GPIO button + HC-SR04 ultrasonic sensor
│   ├── vision.py         # picamera2 capture + TFLite object detection pipeline
│   ├── assistant.py      # Gemini Flash multimodal queries (bilingual prompts)
│   └── audio.py          # Bilingual TTS — cached neural voice + espeak-ng fallback
└── tests/
    └── ...               # Component unit tests
```

---

## Operating Instructions

**Launch:**
```bash
source venv/bin/activate
python main.py
```

On startup, the system asks for a language **out loud** and listens for the user's reply — no keyboard needed:

> *"For English say English. For Arabic say Arabic."*
> *"للإنجليزية قل إنجليزي، للعربية قل عربي"*

The microphone then listens for ~5 seconds. The clip is sent to Google STT in both English (`en-US`) and Arabic (`ar-SA`); the transcripts are scanned for keywords like *english / arabic / إنجليزي / عربي*. If the user stays silent, the mic times out, STT fails, or no keyword is recognized, the system **defaults to English** so launch never blocks.

The chosen language then drives all spoken output (obstacle alerts, listening prompt, Gemini's reply) and the STT locale used for subsequent voice questions.

### Runtime Reference

| Action | Effect |
|--------|--------|
| System starts | Safety Loop activates automatically — obstacle detection runs continuously |
| Obstacle within 100 cm | Voice alert: *"Careful, [object] at [N] centimeters"* |
| Obstacle within 30 cm | Immediate close-proximity warning |
| Press button (GPIO 26) | Cognitive Loop activates — ask a voice question, Gemini responds aloud |
| Press `q` | Graceful shutdown |
| `Ctrl+C` | Safe shutdown with GPIO cleanup |

> Voice alerts for the same obstacle are suppressed for 4 seconds to avoid repeated announcements.

---

## How It Works

### Safety Loop (Continuous — Offline)

A dedicated background thread polls the HC-SR04 sensor at ~20Hz, writing the latest distance into a shared variable. The main loop runs SSD-MobileNet V2 on each camera frame to identify objects. The model focuses on 26 classes relevant to indoor and urban navigation. When an obstacle is detected, the system fuses the object label with the distance reading and speaks a contextual alert in a non-blocking thread — the sensor and GUI never freeze during audio output.

**Neural-voice alert cache.** Every alert phrase the app can ever say — *(label, distance bucket)* in both Arabic and English — is pre-rendered as an MP3 under `sounds/cache/<lang>/` using Microsoft Edge neural voices (`en-US-GuyNeural`, `ar-SA-HamedNeural`). Distances are floor-bucketed to 10 cm (10–90 cm) so the cache covers every reachable combination. At runtime the alert path checks for the cached file and plays it with `ffplay` at ~80 ms latency. If a cache entry is ever missing, the system instantly falls back to `espeak-ng` and synthesizes the missing phrase in the background via `edge-tts` so the next occurrence plays from disk — so the user is never left in silence.

### Cognitive Loop (On Demand — Online)

Pressing the physical button on GPIO 26 triggers the assistant. The system:
1. Announces *"Button Pressed, wait"* as acknowledgment
2. Records audio and transcribes it with `SpeechRecognition`
3. Captures a still frame from the Pi Camera
4. Encodes the frame and sends it with the transcribed question to **Gemini Flash**
5. Speaks the returned answer aloud with `espeak-ng`

During an active assistant query, `is_busy = True` suspends local detection alerts to prevent audio overlap.

### Bilingual Operation

The selected language flows through every spoken interface in the system:

- **Obstacle alerts** play from the matching `sounds/cache/<lang>/` directory (neural Arabic or English voice).
- **Speech recognition** uses the matching Google STT locale (`ar-SA` or `en-US`).
- **Gemini prompts** are written in the user's language, instructing the model to answer in 1–2 short sentences in that language only.
- **System prompts** (*"Button Pressed, wait"*, *"I am listening"*, *"I didn't catch that"*) are translated upfront in `main.py` and `src/audio.py`.

### Sensor Fusion

When the camera detects an object but lighting or transparency (e.g., glass doors) reduces confidence, the ultrasonic sensor acts as a critical redundancy — the user still receives a proximity warning even when the object label cannot be determined. This bridges the "perception gap" that affects vision-only assistive devices.

---

## Test Results

Testing was conducted in three stages: component-level validation, integration stress testing, and real-world navigation scenarios.

| Metric | Result |
|--------|--------|
| Object detection confidence (well-lit) | >85% with SSD-MobileNet V2 |
| Safety Loop latency | ~150ms (near-instantaneous) |
| Cognitive Loop (Gemini) response time | ~2.5 seconds average |
| CPU temperature under sustained load | ~68°C with passive cooling (no throttling) |
| Ultrasonic sensor range tested | 10 cm – 300 cm |

**Key findings:**
- The dual-loop architecture successfully prevented the Cognitive Loop from starving the Safety Loop of CPU resources during concurrent operation.
- The sensor fusion approach ensured users received proximity warnings even when the camera's object detection failed (e.g., glass doors, low light).
- Thermal throttling was avoided at 68°C with passive heat sinks and improved frame airflow design.
- The 2.5s cloud response time is an acceptable trade-off for high-level semantic queries, where depth of information outweighs speed.

---

## GPIO Pin Reference

| GPIO (BCM) | Component | Direction |
|------------|-----------|-----------|
| 23 | HC-SR04 Trigger | Output |
| 24 | HC-SR04 Echo | Input |
| 26 | Push Button | Input (pull-up) |

---

## Troubleshooting

**No audio output** — Ensure PulseAudio is running:
```bash
pulseaudio --start
```

**Camera not detected** — Ensure the `pi` user is in the video group:
```bash
sudo usermod -aG video pi
```

**High CPU temperature** — Monitor heat during long sessions:
```bash
watch -n 2 vcgencmd measure_temp
```

**Noisy ultrasonic readings** — The sensor can produce unstable data in tight spaces due to sound wave reflections. A software averaging filter on the last few readings is implemented in `hardware.py` to smooth this out.

> The Safety Loop works fully offline. The Cognitive Loop (Gemini assistant) requires an active internet connection.

---

## Future Work

Based on the project report, the following enhancements are planned for future iterations:

- **Edge AI Accelerators** — Integrating a Coral Edge TPU or similar NPU to offload SSD-MobileNet inference from the CPU, achieving higher frame rates with lower power consumption.
- **Offline Semantic Understanding** — Deploying Small Language Models (SLMs) like TinyLlama locally on the device to enable Visual Q&A without internet, improving privacy and reliability.
- **Advanced Sensor Fusion** — Adding LiDAR or stereo-depth cameras for 3D spatial mapping, enabling more granular alerts like *"uneven pavement at 2 o'clock"*.
- **Haptic Feedback** — Integrating vibration motors into the frame arms to signal obstacle direction through touch, reducing auditory overload.
- **Bone Conduction Audio** — Switching to bone-conduction transducers to keep the user's ears open to environmental sounds like traffic.
- **Custom PCB & Miniaturization** — Replacing external wiring with flexible printed circuit boards inside the frame temples for a consumer-ready form factor.

---

## License

This project is open source. See [LICENSE](LICENSE) for details.

---

*Built as part of a Final Year Project at Qassim University, Department of Computer Science, 2025/2026.*

*Contributions and feedback welcome.*