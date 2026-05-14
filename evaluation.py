import textstat
from typing import List, Dict

class Evaluator:
    """Provides metrics: readability, bug detection accuracy, and human evaluation helpers."""

    @staticmethod
    def readability_flesch(text: str) -> float:
        """Higher score = easier to read (0‑100)."""
        return textstat.flesch_reading_ease(text)

    @staticmethod
    def readability_grade(text: str) -> float:
        """US grade level (e.g., 8.3 = 8th grade)."""
        return textstat.flesch_kincaid_grade(text)

    @staticmethod
    def bug_detection_accuracy(ground_truth_bugs: List[str], predicted_warnings: List[str]) -> float:
        """
        Simple accuracy: fraction of ground truth bugs that appear in predicted warnings.
        ground_truth_bugs: list of bug descriptions (strings)
        predicted_warnings: list of warnings from BugDetector or LLM bug section.
        """
        if not ground_truth_bugs:
            return 1.0 if not predicted_warnings else 0.0
        found = 0
        for gt in ground_truth_bugs:
            # Check if any predicted warning contains the ground truth text (case‑insensitive)
            if any(gt.lower() in p.lower() for p in predicted_warnings):
                found += 1
        return found / len(ground_truth_bugs)

    @staticmethod
    def human_evaluation_form() -> dict:
        """Return a template for human evaluation scores."""
        return {
            "understandability": 0,   # 1-5
            "bug_usefulness": 0,      # 1-5
            "context_helpfulness": 0, # 1-5
            "comments": ""
        }

    # Example of generating a report
    @staticmethod
    def compare_with_baseline(baseline_summary: str, our_summary: str) -> dict:
        """Compare readability between baseline (original paper) and our model."""
        return {
            "baseline_readability": Evaluator.readability_flesch(baseline_summary),
            "our_readability": Evaluator.readability_flesch(our_summary)
        }