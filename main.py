import argparse
import os
from context_extractor import CrossFileContextExtractor
from bug_detector import BugDetector
from summarizer import CodeSummarizer
from evaluation import Evaluator
# Optional RAG – uncomment if needed
# from rag_retriever import RAGContextRetriever

def main():
    parser = argparse.ArgumentParser(description="Context‑Aware Code Summarizer")
    parser.add_argument("--project_root", required=True, help="Path to project root")
    parser.add_argument("--target_file", required=True, help="Path to the main .py file to summarize")
    parser.add_argument("--model", default="deepseek-ai/deepseek-coder-1.3b-base", help="HuggingFace model name")
    parser.add_argument("--use_rag", action="store_true", help="Use RAG for related files (slower but smarter)")
    args = parser.parse_args()

    # 1. Cross‑file context
    extractor = CrossFileContextExtractor(args.project_root)
    context = extractor.build_context(args.target_file)

    # 2. Bug detection
    detector = BugDetector()
    code_content = open(args.target_file, 'r', encoding='utf-8').read()
    bug_warnings = detector.detect(code_content)

    # 3. Summarization
    print("Loading LLM... (this may take a minute)")
    summarizer = CodeSummarizer(model_name=args.model)
    print("Generating summary...")
    result = summarizer.summarize_function(context, bug_warnings)

    # 4. Output results
    print("\n" + "="*60)
    print("🔍 NORMAL SUMMARY")
    print("="*60)
    print(result["normal_summary"])
    print("\n" + "="*60)
    print("📘 BEGINNER EXPLANATION")
    print("="*60)
    print(result["beginner_explanation"])
    print("\n" + "="*60)
    print("⚠️ BUG WARNING")
    print("="*60)
    print(result["bug_warning"])
    print("\n" + "="*60)
    print("🔗 CROSS-FILE CONTEXT")
    print("="*60)
    print(result["cross_file_context"])

    # 5. Evaluation (readability)
    combined_text = result["beginner_explanation"] + " " + result["bug_warning"]
    flesch = Evaluator.readability_flesch(combined_text)
    grade = Evaluator.readability_grade(combined_text)
    print("\n" + "="*60)
    print("📊 EVALUATION METRICS")
    print("="*60)
    print(f"Flesch Reading Ease: {flesch:.1f} (higher = better)")
    print(f"Flesch-Kincaid Grade: {grade:.1f} (US school grade level)")

    # Optional: compare with baseline (if you have baseline summaries)
    # baseline_summary = "Authenticates user login."   # dummy example
    # comparison = Evaluator.compare_with_baseline(baseline_summary, result["beginner_explanation"])
    # print(comparison)

if __name__ == "__main__":
    main()