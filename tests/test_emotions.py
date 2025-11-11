"""Main benchmark tests for emotion tag leakage."""

import os
from pathlib import Path

import pytest
from fishaudio import FishAudio

from emotion_bench.emotions import get_all_emotions
from emotion_bench.reference_voices import get_reference_ids
from emotion_bench.tts_client import generate_speech
from emotion_bench.stt_client import transcribe_audio
from emotion_bench.analyzer import contains_emotion_tag


def get_num_runs() -> int:
    """Get the number of runs per phrase from environment variable."""
    return int(os.getenv("NUM_RUNS", "1"))


@pytest.mark.parametrize("reference_id", get_reference_ids())
@pytest.mark.parametrize("emotion,phrase,phrase_idx,category", get_all_emotions())
def test_emotion_benchmark(
    fish_client: FishAudio,
    benchmark_collector,
    reference_id: str | None,
    emotion: str,
    phrase: str,
    phrase_idx: int,
    category: str,
):
    """Test that emotion tags do not leak into STT transcriptions.

    Each emotion has 10 different test phrases for comprehensive coverage.

    Args:
        fish_client: Fish Audio client instance
        benchmark_collector: Collector for aggregating results
        reference_id: Voice model ID to use (or None for default voice)
        emotion: The emotion tag (e.g., "happy")
        phrase: The test phrase for this emotion
        phrase_idx: The phrase number (1-10)
        category: The emotion category (e.g., "basic_emotions")
    """
    text_with_emotion = f"({emotion}) {phrase}"
    voice_label = reference_id if reference_id else "default"
    num_runs = get_num_runs()

    # Create output directory for this emotion
    audio_dir = Path("output/audio") / emotion
    audio_dir.mkdir(parents=True, exist_ok=True)

    # Run the same phrase NUM_RUNS times
    for run in range(num_runs):
        result_status = "PASS"
        error_message = None
        transcription = None

        try:
            # Step 1: Generate audio using TTS
            audio_bytes = generate_speech(
                client=fish_client, text=text_with_emotion, reference_id=reference_id
            )

            # Save audio file (include run number if NUM_RUNS > 1)
            if num_runs > 1:
                audio_file = audio_dir / f"{voice_label}_{phrase_idx}_run{run + 1}.mp3"
            else:
                audio_file = audio_dir / f"{voice_label}_{phrase_idx}.mp3"

            with open(audio_file, "wb") as f:
                f.write(audio_bytes)

            # Step 2: Transcribe audio using STT
            transcription = transcribe_audio(
                client=fish_client, audio_bytes=audio_bytes
            )

            # Step 3: Check if emotion tag leaked into transcription
            tag_found = contains_emotion_tag(transcription, emotion)

            if tag_found:
                result_status = "FAIL"
                error_message = f"Tag leaked: '{transcription}'"

        except Exception as e:
            result_status = "ERROR"
            error_message = str(e)

        # Add to collector (one result per run)
        benchmark_collector.add_result(
            emotion=emotion,
            voice=voice_label,
            phrase_idx=phrase_idx,
            phrase=phrase,
            run_number=run + 1,
            category=category,
            status=result_status,
            transcription=transcription,
            error=error_message,
        )
