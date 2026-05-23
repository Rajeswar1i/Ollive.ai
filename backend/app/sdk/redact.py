import re

_PATTERNS = [
    (re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'), '[EMAIL]'),
    (re.compile(r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'), '[PHONE]'),
    (re.compile(r'\b\d{3}-\d{2}-\d{4}\b'), '[SSN]'),
    (re.compile(r'\b4[0-9]{12}(?:[0-9]{3})?\b'), '[CARD]'),   # Visa
    (re.compile(r'\b5[1-5][0-9]{14}\b'), '[CARD]'),            # Mastercard
]

def redact(text: str) -> str:
    if not text:
        return text
    for pattern, replacement in _PATTERNS:
        text = pattern.sub(replacement, text)
    return text
