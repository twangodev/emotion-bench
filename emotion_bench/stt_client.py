"""Fish Audio STT client wrapper."""

from fishaudio import FishAudio


def transcribe_audio(
    client: FishAudio, audio_bytes: bytes, language: str | None = None
) -> str:
    """Transcribe audio to text using Fish Audio STT.

    Args:
        client: FishAudio client instance
        audio_bytes: Audio data in bytes (MP3, WAV, etc.)
        language: Optional language code (e.g., "en", "zh"). Auto-detected if not provided.

    Returns:
        Transcribed text
    """
    result = client.asr.transcribe(audio=audio_bytes, language=language)
    return result.text
