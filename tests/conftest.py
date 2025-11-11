"""Pytest configuration and fixtures for emotion benchmark tests."""

import os
import shutil
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fishaudio import FishAudio

from tests.benchmark_results import BenchmarkCollector

# Load environment variables from .env file
load_dotenv()

# Global collector for aggregating results from all workers
aggregated_collector = BenchmarkCollector()


def pytest_sessionstart(session):
    """Clear output directory before starting test session."""
    output_dir = Path("output")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir()


@pytest.fixture(scope="session")
def fish_client() -> FishAudio:
    """Create a Fish Audio client instance."""
    api_key = os.getenv("FISH_AUDIO_API_KEY")
    if not api_key:
        pytest.skip("FISH_AUDIO_API_KEY environment variable not set")

    return FishAudio(api_key=api_key)


@pytest.fixture(scope="session")
def benchmark_collector(request):
    """Get a benchmark collector for this test session."""
    collector = BenchmarkCollector()
    # Store reference in session for pytest_sessionfinish to access
    request.session._benchmark_collector = collector
    return collector


def pytest_testnodedown(node, error):
    """Collect results from workers as they complete (controller only)."""
    if hasattr(node, "workeroutput") and "benchmark_results" in node.workeroutput:
        worker_results = node.workeroutput["benchmark_results"]

        # Add all worker results to aggregated collector
        for result in worker_results:
            aggregated_collector.add_result(
                emotion=result["emotion"],
                voice=result["voice"],
                phrase_idx=result["phrase_idx"],
                phrase=result["phrase"],
                run_number=result["run_number"],
                status=result["status"],
                transcription=result["transcription"],
                error=result["error"],
            )


def pytest_sessionfinish(session):
    """Save results: either from workers (xdist) or direct execution."""
    is_worker = hasattr(session.config, "workerinput")

    if is_worker:
        # Worker: send results to controller via workeroutput
        if hasattr(session, "_benchmark_collector"):
            collector = session._benchmark_collector
            if collector.results:
                session.config.workeroutput["benchmark_results"] = [
                    {
                        "emotion": r.emotion,
                        "voice": r.voice,
                        "phrase_idx": r.phrase_idx,
                        "phrase": r.phrase,
                        "run_number": r.run_number,
                        "status": r.status,
                        "transcription": r.transcription,
                        "error": r.error,
                    }
                    for r in collector.results
                ]
    else:
        # Controller: save aggregated results
        if aggregated_collector.results:
            # Had workers - use aggregated results
            aggregated_collector.save_results("output/benchmark_results.json")
            aggregated_collector.save_markdown_summary("output/summary.md")
        elif hasattr(session, "_benchmark_collector"):
            # No workers - save from session collector
            collector = session._benchmark_collector
            if collector.results:
                collector.save_results("output/benchmark_results.json")
                collector.save_markdown_summary("output/summary.md")
