from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from scene_runner import speak, SilenceTracker, AudioFrameReader
from utils import parse_script_from_pdf, extract_characters, structure_script
import os

app = FastAPI()

# Fix 1: Combine root and health check
@app.get("/")
async def root():
    return {
        "message": "Welcome to the Offer Only API",
        "status": "ok",
        "port": os.getenv("PORT", 10000)
    }

# Fix 2: Complete CORS middleware (missing quotes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Fixed quotes
    allow_headers=["*"],  # Fixed quotes
)

SCRIPT_CACHE = {}

def run_scene(script, user_character):
    print(f"\n🎬 Starting scene — YOU are: {user_character}")
    for entry in script:
        print(f"🎭 {entry['character']}: {entry['line']}")
        speak(entry['line'])  # <-- this triggers the audio!


# ---- API Endpoints ----
@app.post("/upload")
async def upload_script(file: UploadFile = File(...)):
    contents = await file.read()
    temp_path = "uploaded_script.pdf" # TODO change temp path
    with open(temp_path, "wb") as f:
        f.write(contents)
    print("contents")
    print(contents)
    print("temp_path")
    print(temp_path)
    lines = parse_script_from_pdf(temp_path)
    characters = extract_characters(lines)
    return characters


@app.post("/start_scene")
async def start_scene(file: UploadFile = File(...), character: str = Form(...)):
    contents = await file.read()
    temp_path = "uploaded_script.pdf"  # TODO change temp path
    with open(temp_path, "wb") as f:
        f.write(contents)

    script_lines = parse_script_from_pdf(temp_path)
    structured_all = structure_script(script_lines)

    # Find the first speaking character
    user_is_first = structured_all and structured_all[0]["character"] == character.upper()
    print("user_is_first")
    print(user_is_first)

    # Extract scene partner lines only
    structured = [entry for entry in structured_all if entry["character"] != character.upper()]
    print("structured")
    print(structured)

    # 🎭 Run scene using dynamic timeout + ElevenLabs
    silence_tracker = SilenceTracker()
    audio_reader = AudioFrameReader(silence_tracker)

    # Wait for user to speak if they're first
    if user_is_first:
        print(f"🗣️ Waiting for {character} to say their first line...")
        audio_reader.listen_until_silence()

    for entry in structured:
        speak(entry['line'])
        audio_reader.listen_until_silence()

    return {"message": f"Scene with {character} complete!"}

