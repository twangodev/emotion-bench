"""Fish Audio TTS client wrapper."""

from fishaudio import FishAudio


def generate_speech(
    client: FishAudio, text: str, reference_id: str | None = None, model: str = "s1"
) -> bytes:
    """Generate speech from text using Fish Audio TTS.

    Args:
        client: FishAudio client instance
        text: Text to convert to speech (can include emotion tags like "(happy) Hello!")
        reference_id: Optional voice model ID to use
        model: TTS model to use (s1, speech-1.6, speech-1.5). Defaults to s1.

    Returns:
        Audio bytes in MP3 format
    """
    # Collect all audio chunks
    audio_buffer = bytearray()
    for chunk in client.tts.convert(text=text, reference_id=reference_id, model=model):
        audio_buffer.extend(chunk)

    return bytes(audio_buffer)
