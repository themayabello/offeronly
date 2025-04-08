import fitz  # PyMuPDF
import re
from collections import Counter
import webrtcvad
import pyaudio
import time
import tempfile
import requests
import os
from dotenv import load_dotenv
from utils import parse_script_from_pdf, extract_characters, structure_script


# -------- CONFIG --------
load_dotenv()
api_key = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_VOICE_ID = "cjVigY5qzO86Huf0OWal"

# -------- PDF + Script Parsing --------
def get_user_character_and_script():
    path = input("📄 Enter path to your PDF script: ")
    lines = parse_script_from_pdf(path)
    characters = extract_characters(lines)

    if not characters:
        print("❌ No characters detected. Please check the format of your script.")
        exit(1)

    print("\n🎭 Characters detected:")
    for i, char in enumerate(characters):
        print(f"{i+1}. {char}")

    idx = int(input("\nSelect your character number: ")) - 1
    user_character = characters[idx]
    full_script = structure_script(lines, user_character)
    return full_script, user_character

# -------- ElevenLabs Voice --------
def speak(text, voice_id=ELEVENLABS_VOICE_ID, api_key=api_key):
    print(f"\n🔊 Scene Partner: {text}")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.4,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            fp.write(response.content)
            fp.flush()
            if os.name == "nt":
                os.system(f"start {fp.name}")
            else:
                os.system(f"afplay {fp.name}")
    else:
        print("❌ Failed to get audio from ElevenLabs:", response.text)

# -------- Dynamic Silence Tracker --------
class SilenceTracker:
    def __init__(self):
        self.recent_silences = []

    def get_dynamic_timeout(self):
        if not self.recent_silences:
            return 1.6
        avg = sum(self.recent_silences[-5:]) / min(len(self.recent_silences), 5)
        return max(min(avg, 2.0), 0.8)

    def add_pause(self, duration):
        self.recent_silences.append(duration)

# -------- Voice Activity Detection --------
class AudioFrameReader:
    def __init__(self, silence_tracker, aggressiveness=2):
        self.vad = webrtcvad.Vad(aggressiveness)
        self.rate = 16000
        self.chunk = int(self.rate / 100)  # 10ms
        self.format = pyaudio.paInt16
        self.channels = 1
        self.tracker = silence_tracker

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(format=self.format,
                                      channels=self.channels,
                                      rate=self.rate,
                                      input=True,
                                      frames_per_buffer=self.chunk)

    def listen_until_silence(self):
        print("🎤 Listening for your line...")
        speaking = False
        silent_chunks = 0
        speech_started = None

        timeout = self.tracker.get_dynamic_timeout()
        adjusted_chunks = int((timeout * 1000) / 10 * 0.8)

        print(f"🕐 Dynamic timeout: {timeout:.2f}s | Trigger after ~{adjusted_chunks * 10}ms silence")

        while True:
            data = self.stream.read(self.chunk, exception_on_overflow=False)
            is_speech = self.vad.is_speech(data, self.rate)

            if is_speech:
                if not speaking:
                    speaking = True
                    silent_chunks = 0
                    speech_started = time.time()
            else:
                if speaking:
                    silent_chunks += 1

            if silent_chunks >= adjusted_chunks:
                speaking = False
                if speech_started:
                    pause_duration = time.time() - speech_started
                    self.tracker.add_pause(pause_duration)
                    print(f"⏹️ You paused for: {pause_duration:.2f}s")
                return

# -------- Scene Runner --------
def run_scene():
    script, user_character = get_user_character_and_script()
    silence_tracker = SilenceTracker()
    audio_reader = AudioFrameReader(silence_tracker)

    print(f"\n🎬 Starting scene — YOU are: {user_character}")

    for entry in script:
        if entry['character'].upper() != user_character.upper():
            speak(entry['line'])
        else:
            audio_reader.listen_until_silence()

    print("\n🎭 Scene complete!")

# -------- Main --------
if __name__ == "__main__":
    run_scene()
