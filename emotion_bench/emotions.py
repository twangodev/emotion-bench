"""Emotion registry with all Fish Audio supported emotions and contextual test phrases."""

from pathlib import Path
import yaml


def _load_emotions() -> tuple[dict[str, list[str]], dict[str, str]]:
    """Load emotions from YAML file.

    Returns:
        Tuple of (all_emotions dict, emotion_to_category mapping)
    """
    yaml_path = Path(__file__).parent.parent / "emotions.yaml"
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)

    all_emotions = {}
    emotion_to_category = {}

    # Load each category and track which category each emotion belongs to
    for category_name in ["basic_emotions", "advanced_emotions", "tone_and_special_markers",
                          "unofficial_emotions", "unofficial_markers"]:
        category_data = data.get(category_name, {})
        all_emotions.update(category_data)

        # Map each emotion to its category
        for emotion in category_data.keys():
            emotion_to_category[emotion] = category_name

    return all_emotions, emotion_to_category


# Load emotions from YAML file
ALL_EMOTIONS, EMOTION_CATEGORIES = _load_emotions()


def get_all_emotions() -> list[tuple[str, str, int, str]]:
    """Get all emotions as a list of (emotion_tag, test_phrase, phrase_index, category) tuples.

    Returns one tuple for each phrase in each emotion's list.
    """
    emotion_phrases = []
    for emotion, phrases in ALL_EMOTIONS.items():
        category = EMOTION_CATEGORIES.get(emotion, "unknown")
        for idx, phrase in enumerate(phrases, 1):
            emotion_phrases.append((emotion, phrase, idx, category))
    return emotion_phrases


def get_emotion_phrases(emotion: str) -> list[str]:
    """Get all test phrases for a specific emotion."""
    if emotion not in ALL_EMOTIONS:
        raise ValueError(f"Unknown emotion: {emotion}")
    return ALL_EMOTIONS[emotion]


def get_emotion_category(emotion: str) -> str:
    """Get the category for a specific emotion."""
    return EMOTION_CATEGORIES.get(emotion, "unknown")
