"""Estimate TTS API costs for running the benchmark."""

import math
import os

from scipy import stats

from emotion_bench.emotions import get_all_emotions
from emotion_bench.reference_voices import get_reference_ids

# Statistical constants
Z_SCORE_95 = stats.norm.ppf(0.975)  # 95% confidence interval
Z_SCORE_99 = stats.norm.ppf(0.995)  # 99% confidence interval
WORST_CASE_PROPORTION = 0.5  # Maximum variance for margin of error

# Cost constants
COST_PER_MILLION_BYTES = 15.0  # Fish Audio TTS pricing


def calculate_confidence_intervals(sample_size: float) -> tuple[float, float]:
    """Calculate margin of error for 95% and 99% confidence intervals.

    Args:
        sample_size: Number of samples in the test

    Returns:
        Tuple of (margin_error_95, margin_error_99) as proportions (0-1)
    """
    if sample_size <= 0:
        return 0.0, 0.0

    margin_error_95 = Z_SCORE_95 * math.sqrt(
        WORST_CASE_PROPORTION * (1 - WORST_CASE_PROPORTION) / sample_size
    )
    margin_error_99 = Z_SCORE_99 * math.sqrt(
        WORST_CASE_PROPORTION * (1 - WORST_CASE_PROPORTION) / sample_size
    )
    return margin_error_95, margin_error_99


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

    # Calculate cost
    estimated_cost = (
        (total_bytes * num_voices * num_runs) / 1_000_000
    ) * COST_PER_MILLION_BYTES

    # Calculate actual phrases per emotion
    num_emotions = len(emotion_breakdown)
    phrases_per_emotion = len(emotion_phrases) / num_emotions if num_emotions > 0 else 0

    # Calculate statistical confidence intervals
    sample_size_per_emotion = phrases_per_emotion * num_runs * num_voices
    margin_error_95, margin_error_99 = calculate_confidence_intervals(
        sample_size_per_emotion
    )

    # Print summary
    print("=" * 60)
    print("BENCHMARK COST ESTIMATION")
    print("=" * 60)
    print(f"Emotions: {num_emotions}")
    print(f"Phrases per emotion: {phrases_per_emotion:.0f}")
    print(f"Runs per phrase: {num_runs}")
    print(f"Voices to test: {num_voices}")
    print()
    print("STATISTICAL CONFIDENCE:")
    print(f"Sample size per emotion: {sample_size_per_emotion:.0f} tests")
    print(f"Margin of error (95% CI): ±{margin_error_95 * 100:.1f}%")
    print(f"Margin of error (99% CI): ±{margin_error_99 * 100:.1f}%")
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
