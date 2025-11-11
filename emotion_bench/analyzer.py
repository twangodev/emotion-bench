"""Analyzer for detecting emotion tag leakage in transcriptions."""

import re


def contains_emotion_tag(transcription: str, emotion: str) -> bool:
    """Check if emotion tag appears in the transcription.

    Args:
        transcription: The STT transcription text
        emotion: The emotion tag (without parentheses, e.g., "happy")

    Returns:
        True if emotion tag is found (test fails), False otherwise (test passes)
    """
    if not transcription:
        return False

    # Normalize transcription for comparison
    text_lower = transcription.lower()
    emotion_lower = emotion.lower()

    # Check for various forms the emotion might appear:
    # 1. With parentheses: (happy)
    if f"({emotion_lower})" in text_lower:
        return True

    # 2. As a standalone word with word boundaries
    # Use regex to match the emotion as a complete word
    pattern = r"\b" + re.escape(emotion_lower) + r"\b"
    if re.search(pattern, text_lower):
        return True

    return False
