import fitz  # PyMuPDF
import re
from collections import Counter

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
        if line.isupper() and not re.match(r'^(INT\.|EXT\.|FADE|CUT TO|DISSOLVE)', line):
            if len(line.split()) <= 4:
                potential_chars.append(line)
    most_common = Counter(potential_chars).most_common()
    return [char for char, count in most_common]
