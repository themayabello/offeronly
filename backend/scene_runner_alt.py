import fitz  # PyMuPDF
from collections import Counter
import re


def parse_script_from_pdf(path):
    doc = fitz.open(path)
    all_lines = []
    for page in doc:
        text = page.get_text()
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line:
                all_lines.append(line)
    return all_lines


def extract_characters(script_lines):
    potential_chars = []
    for line in script_lines:
        if line.isupper() and 2 <= len(line.split()) <= 4:
            if not re.match(r'^(INT\.|EXT\.|FADE|CUT TO|DISSOLVE)', line):
                potential_chars.append(line)
    most_common = Counter(potential_chars).most_common()
    return [char for char, count in most_common]


def structure_script(script_lines, user_character):
    structured = []
    current_char = None
    for line in script_lines:
        if line.isupper():
            current_char = line
        elif current_char:
            structured.append({"character": current_char, "line": line})
    filtered_script = [entry for entry in structured if entry["character"] != user_character.upper()]
    return filtered_script


def run_scene(script, user_character):
    print(f"\n🎬 Starting scene — YOU are: {user_character}")
    for entry in script:
        print(f"{entry['character']}: {entry['line']}")
    print("\n[This is where the ElevenLabs + VAD logic goes]\n")


def main():
    path_to_pdf = input("Enter path to your PDF script: ")
    script_lines = parse_script_from_pdf(path_to_pdf)
    characters = extract_characters(script_lines)

    print("🎭 Characters detected:")
    for idx, name in enumerate(characters):
        print(f"{idx + 1}. {name}")

    selected = int(input("\nSelect your character number: ")) - 1
    user_character = characters[selected]

    filtered_script = structure_script(script_lines, user_character)
    run_scene(filtered_script, user_character)


if __name__ == "__main__":
    main()
