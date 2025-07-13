import re


def clean_text(text: str) -> str:
    # Normalize newlines to spaces
    text = text.replace('\n\n', '\n').replace('\r', ' ')

    # Remove extra punctuation or symbols (keep
    # alphanumerics and basic punctuation)
    text = re.sub(r'[^a-zA-Z0-9\s.,!?\'"-]', '', text)

    # Collapse multiple spaces
    text = re.sub(r' +', ' ', text)

    # Strip leading/trailing whitespace
    text = text.strip()

    return text
