import speech_recognition as sr

def list_microphones():
    print("🔎 Scanning for Audio Input Devices...")
    # List names of all detected microphones
    mic_list = sr.Microphone.list_microphone_names()
    
    if not mic_list:
        print("❌ No microphones found! Check your USB connection.")
        return

    for index, name in enumerate(mic_list):
        print(f"Index [{index}]: {name}")

if __name__ == "__main__":
    list_microphones()