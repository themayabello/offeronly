import fitz  # PyMuPDF
import re
from collections import Counter

# parsing and structuring content

def parse_script_from_pdf(path):
    # gets the raw script
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


def structure_script(script_lines):
    structured = []
    current_character = None
    additional_lines = []

    for line in script_lines:
        if line.isupper() and 1 <= len(line.split()) <= 4:
            if current_character and additional_lines:
                structured.append({
                    "character": current_character,
                    "line": ' '.join(additional_lines).strip()
                })
                # reset buffer
                additional_lines = []
            current_character = line
        elif current_character:
            if line.strip().startswith("(") and line.strip().endswith(")"):
                continue  # skip parenthetical
            additional_lines.append(line)

    # Catch the last line
    if current_character and additional_lines:
        structured.append({
            "character": current_character,
            "line": ' '.join(additional_lines).strip()
        })

    # Return full script for now (you can filter later if needed)
    return structured


def extract_characters(script_lines):
    potential_chars = []
    for line in script_lines:
        if line.isupper() and not re.match(r'^(INT\.|EXT\.|FADE|CUT TO|DISSOLVE)', line):
            if len(line.split()) <= 4:
                potential_chars.append(line)
    most_common = Counter(potential_chars).most_common()
    return [char for char, count in most_common]
