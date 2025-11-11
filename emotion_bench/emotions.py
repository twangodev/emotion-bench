"""Emotion registry with all Fish Audio supported emotions and contextual test phrases."""

from pathlib import Path
import yaml


def _load_emotions() -> dict[str, list[str]]:
    """Load emotions from YAML file."""
    yaml_path = Path(__file__).parent.parent / "emotions.yaml"
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    # Combine all emotion categories
    all_emotions = {}
    # Official emotions and markers
    all_emotions.update(data.get("basic_emotions", {}))
    all_emotions.update(data.get("advanced_emotions", {}))
    all_emotions.update(data.get("tone_and_special_markers", {}))
    # Unofficial emotions and markers
    all_emotions.update(data.get("unofficial_emotions", {}))
    all_emotions.update(data.get("unofficial_markers", {}))

    return all_emotions


# Load emotions from YAML file
ALL_EMOTIONS = _load_emotions()


def get_all_emotions() -> list[tuple[str, str, int]]:
    """Get all emotions as a list of (emotion_tag, test_phrase, phrase_index) tuples.

    Returns one tuple for each phrase in each emotion's list.
    """
    emotion_phrases = []
    for emotion, phrases in ALL_EMOTIONS.items():
        for idx, phrase in enumerate(phrases, 1):
            emotion_phrases.append((emotion, phrase, idx))
    return emotion_phrases


def get_emotion_phrases(emotion: str) -> list[str]:
    """Get all test phrases for a specific emotion."""
    if emotion not in ALL_EMOTIONS:
        raise ValueError(f"Unknown emotion: {emotion}")
    return ALL_EMOTIONS[emotion]
