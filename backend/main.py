from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from scene_runner import speak, SilenceTracker, AudioFrameReader  # adjust if file is renamed
from utils import parse_script_from_pdf, extract_characters

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Welcome to the Offer Only API"}


# Allow frontend to talk to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.mbcreativeenterprises.com"],  # In production, replace with your Netlify domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SCRIPT_CACHE = {}


def structure_script(script_lines, user_character):
    structured = []
    current_char = None
    for line in script_lines:
        if line.isupper():
            current_char = line
        elif current_char:
            # skip parentheticals or directions
            if line.strip().startswith("(") and line.strip().endswith(")"):
                continue
            structured.append({"character": current_char, "line": line})

    # return only the scene partner's lines
    return [entry for entry in structured if entry["character"] == user_character.upper()]


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

    lines = parse_script_from_pdf(temp_path)
    characters = extract_characters(lines)
    return characters


@app.post("/start_scene")
async def start_scene(file: UploadFile = File(...), character: str = Form(...)):
    contents = await file.read()
    temp_path = "uploaded_script.pdf"  # TODO change temp path
    with open(temp_path, "wb") as f:
        f.write(contents)

    lines = parse_script_from_pdf(temp_path)

    # Find the first speaking character
    structured_all = []
    current_char = None
    for line in lines:
        if line.isupper():
            current_char = line
        elif current_char:
            if line.strip().startswith("(") and line.strip().endswith(")"):
                continue
            structured_all.append({"character": current_char, "line": line})

    user_is_first = structured_all and structured_all[0]["character"] == character.upper()
    print(user_is_first)

    # Extract scene partner lines only
    structured = [entry for entry in structured_all if entry["character"] != character.upper()]

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


