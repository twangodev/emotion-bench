"""Fish Audio TTS client wrapper."""

from fishaudio import FishAudio
from fishaudio.types import TTSConfig


def generate_speech(
    client: FishAudio, text: str, reference_id: str | None = None
) -> bytes:
    """Generate speech from text using Fish Audio TTS.

    Args:
        client: FishAudio client instance
        text: Text to convert to speech (can include emotion tags like "(happy) Hello!")
        reference_id: Optional voice model ID to use

    Returns:
        Audio bytes in MP3 format
    """
    # Create TTS config with reference_id if provided
    config = TTSConfig(reference_id=reference_id) if reference_id else TTSConfig()

    # Collect all audio chunks
    audio_buffer = bytearray()
    for chunk in client.tts.convert(text=text, config=config):
        audio_buffer.extend(chunk)

    return bytes(audio_buffer)
