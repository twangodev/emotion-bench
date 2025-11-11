"""Estimate TTS API costs for running the benchmark."""

import os

from emotion_bench.emotions import get_all_emotions
from emotion_bench.reference_voices import get_reference_ids


def estimate_cost():
    """Calculate total characters and estimated cost for benchmark."""

    # Get all test cases
    emotion_phrases = get_all_emotions()
    reference_ids = get_reference_ids()

    # Group by emotion and calculate
    emotion_breakdown = {}
    total_chars = 0
    total_bytes = 0

    for emotion, phrase, phrase_idx, _ in emotion_phrases:
        if emotion not in emotion_breakdown:
            emotion_breakdown[emotion] = []

        # Format text as it will be sent to TTS
        text_with_emotion = f"({emotion}) {phrase}"

        # Count characters and UTF-8 bytes
        chars = len(text_with_emotion)
        bytes_count = len(text_with_emotion.encode("utf-8"))

        emotion_breakdown[emotion].append(
            {
                "phrase_idx": phrase_idx,
                "text": text_with_emotion,
                "chars": chars,
                "bytes": bytes_count,
            }
        )

        total_chars += chars
        total_bytes += bytes_count

    # Get NUM_RUNS and number of voices
    num_runs = int(os.getenv("NUM_RUNS", "1"))
    num_voices = len(reference_ids)

    # Multiply by voices and runs
    total_api_calls = len(emotion_phrases) * num_voices * num_runs

    # Calculate cost ($15 per 1M UTF-8 bytes)
    cost_per_million_bytes = 15.0
    estimated_cost = (
        (total_bytes * num_voices * num_runs) / 1_000_000
    ) * cost_per_million_bytes

    # Calculate actual phrases per emotion
    num_emotions = len(emotion_breakdown)
    phrases_per_emotion = len(emotion_phrases) / num_emotions if num_emotions > 0 else 0

    # Print summary
    print("=" * 60)
    print("BENCHMARK COST ESTIMATION")
    print("=" * 60)
    print(f"Emotions: {num_emotions}")
    print(f"Phrases per emotion: {phrases_per_emotion:.0f}")
    print(f"Runs per phrase: {num_runs}")
    print(f"Voices to test: {num_voices}")
    print()
    print(f"Base test cases: {len(emotion_phrases)}")
    print(
        f"Total TTS calls: {total_api_calls:,} ({len(emotion_phrases)} × {num_voices} voices × {num_runs} runs)"
    )
    print()
    print(f"Characters per run: {total_chars:,}")
    print(f"UTF-8 bytes per run: {total_bytes:,}")
    print(f"Total UTF-8 bytes (all runs): {total_bytes * num_voices * num_runs:,}")
    print(f"Total UTF-8 MB: {(total_bytes * num_voices * num_runs) / 1_000_000:.3f}")
    print()
    print(f"Estimated TTS cost: ${estimated_cost:.4f}")
    print()
    print("Note: This only accounts for TTS. STT costs are separate.")
    print("      (STT pricing depends on audio duration)")
    print("=" * 60)

    # Show reference voices being tested
    print("\nVoices being tested:")
    for voice_id in reference_ids:
        label = voice_id if voice_id else "default (no reference)"
        print(f"  - {label}")


if __name__ == "__main__":
    estimate_cost()
