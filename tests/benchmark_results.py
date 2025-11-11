"""Collect and aggregate benchmark results."""

from dataclasses import dataclass
from pathlib import Path
import json
from tabulate import tabulate


@dataclass
class BenchmarkResult:
    """Single benchmark result for one phrase test."""

    emotion: str
    voice: str
    phrase_idx: int
    phrase: str
    run_number: int
    category: str
    status: str  # PASS, FAIL, or ERROR
    transcription: str | None
    error: str | None


class BenchmarkCollector:
    """Collect benchmark results across all tests."""

    def __init__(self):
        self.results: list[BenchmarkResult] = []

    def add_result(
        self,
        emotion: str,
        voice: str,
        phrase_idx: int,
        phrase: str,
        run_number: int,
        category: str,
        status: str,
        transcription: str | None,
        error: str | None,
    ):
        """Add a benchmark result."""
        self.results.append(
            BenchmarkResult(
                emotion=emotion,
                voice=voice,
                phrase_idx=phrase_idx,
                phrase=phrase,
                run_number=run_number,
                category=category,
                status=status,
                transcription=transcription,
                error=error,
            )
        )

    def save_results(self, output_file: str = "benchmark_results.json"):
        """Save results to JSON file."""
        data = {
            "results": [
                {
                    "emotion": r.emotion,
                    "voice": r.voice,
                    "phrase_idx": r.phrase_idx,
                    "phrase": r.phrase,
                    "run_number": r.run_number,
                    "category": r.category,
                    "status": r.status,
                    "transcription": r.transcription,
                    "error": r.error,
                }
                for r in self.results
            ],
            "summary": self.get_summary(),
        }

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"\nBenchmark results saved to: {output_path.absolute()}")

    def get_summary(self) -> dict:
        """Get summary statistics."""
        if not self.results:
            return {}

        total_tests = len(self.results)
        pass_count = sum(1 for r in self.results if r.status == "PASS")
        fail_count = sum(1 for r in self.results if r.status == "FAIL")
        error_count = sum(1 for r in self.results if r.status == "ERROR")

        success_rate = (pass_count / total_tests * 100) if total_tests > 0 else 0

        # Group by emotion
        emotion_stats = {}
        for result in self.results:
            if result.emotion not in emotion_stats:
                emotion_stats[result.emotion] = {"pass": 0, "fail": 0, "error": 0}
            emotion_stats[result.emotion][result.status.lower()] += 1

        # Calculate success rate per emotion
        emotion_success_rates = {}
        for emotion, stats in emotion_stats.items():
            total = stats["pass"] + stats["fail"] + stats["error"]
            emotion_success_rates[emotion] = (
                (stats["pass"] / total * 100) if total > 0 else 0
            )

        # Find best and worst
        best_emotions = sorted(
            emotion_success_rates.items(), key=lambda x: x[1], reverse=True
        )[:5]
        worst_emotions = sorted(emotion_success_rates.items(), key=lambda x: x[1])[:5]

        return {
            "total_tests": total_tests,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "error_count": error_count,
            "success_rate": round(success_rate, 2),
            "best_emotions": [
                {"emotion": e, "success_rate": round(r, 2)} for e, r in best_emotions
            ],
            "worst_emotions": [
                {"emotion": e, "success_rate": round(r, 2)} for e, r in worst_emotions
            ],
        }

    def save_markdown_summary(self, output_file: str = "output/summary.md"):
        """Save summary as markdown file."""
        if not self.results:
            return

        summary = self.get_summary()

        # Build markdown content
        lines = [
            "# Emotion Benchmark Summary",
            "",
            f"**Total Tests:** {summary['total_tests']}  ",
            f"**Pass:** {summary['pass_count']} | **Fail:** {summary['fail_count']} | **Error:** {summary['error_count']}  ",
            f"**Success Rate:** {summary['success_rate']}%",
            "",
            "## Top 5 Best Performing Emotions\n",
        ]

        # Top 5 Best Performing Emotions
        best_table = [
            [item["emotion"], f"{item['success_rate']:.1f}%"]
            for item in summary["best_emotions"]
        ]
        lines.append(
            tabulate(best_table, headers=["Emotion", "Success Rate"], tablefmt="github")
        )
        lines.append("")

        # Top 5 Worst Performing Emotions
        lines.append("## Top 5 Worst Performing Emotions\n")
        worst_table = [
            [item["emotion"], f"{item['success_rate']:.1f}%"]
            for item in summary["worst_emotions"]
        ]
        lines.append(
            tabulate(
                worst_table, headers=["Emotion", "Success Rate"], tablefmt="github"
            )
        )
        lines.append("")

        # Emotion breakdown
        lines.append("## Results by Emotion\n")

        # Group results by emotion
        emotion_groups = {}
        for result in self.results:
            if result.emotion not in emotion_groups:
                emotion_groups[result.emotion] = []
            emotion_groups[result.emotion].append(result)

        # Create table with pass/fail/error counts per emotion
        emotion_table = []
        for emotion, results in sorted(emotion_groups.items()):
            pass_count = sum(1 for r in results if r.status == "PASS")
            fail_count = sum(1 for r in results if r.status == "FAIL")
            error_count = sum(1 for r in results if r.status == "ERROR")
            total = len(results)
            success_rate = (pass_count / total * 100) if total > 0 else 0

            emotion_table.append(
                [
                    emotion,
                    results[0].category,
                    results[0].voice,
                    f"{success_rate:.1f}%",
                    pass_count,
                    fail_count,
                    error_count,
                    total,
                ]
            )

        # Sort by success rate (best first)
        emotion_table.sort(key=lambda x: float(x[3].rstrip("%")), reverse=True)

        lines.append(
            tabulate(
                emotion_table,
                headers=[
                    "Emotion",
                    "Category",
                    "Voice",
                    "Success Rate",
                    "Pass",
                    "Fail",
                    "Error",
                    "Total",
                ],
                tablefmt="github",
            )
        )

        # Write to file
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            f.write("\n".join(lines))

        print(f"\nMarkdown summary saved to: {output_path.absolute()}")
