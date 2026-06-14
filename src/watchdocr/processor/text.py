import re


def cleanup_text_simple(text: str):
    ctext = re.sub(r'[ \t]+', ' ', text)  # Clean multiple whitespaces
    return ctext
