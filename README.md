# Context-Aware Code Summarizer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Paper](https://img.shields.io/badge/paper-arXiv-red.svg)](https://arxiv.org/abs/your-paper-link)

A lightweight framework for **context-aware, beginner-friendly, and bug-aware code summarization** using open-source Large Language Models. This system analyzes multi-file Python projects, detects security vulnerabilities, and generates comprehensive summaries tailored for both technical developers and novice programmers.

> 📄 **Paper**: *"Context-Aware Beginner-Friendly and Bug-Aware Code Summarization Using Lightweight Large Language Models"* — Aashish Devthiya, IIT Patna

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Output Examples](#output-examples)
- [Evaluation Metrics](#evaluation-metrics)
- [Configuration](#configuration)
- [Limitations & Future Work](#limitations--future-work)
- [Citation](#citation)

---

## Overview

Modern software systems consist of interconnected multi-file codebases that are difficult for beginners and developers to understand efficiently. Existing code summarization systems primarily generate concise technical summaries but fail to provide:

- **Beginner-friendly explanations** for educational settings
- **Bug/security awareness** highlighting vulnerabilities
- **Cross-file contextual understanding** of dependencies

This framework addresses these gaps by combining:

| Component | Technology |
|-----------|-------------|
| Cross-file context | AST-based dependency extraction |
| Bug detection | Rule-based static analysis (8 patterns) |
| Summarization | DeepSeek Coder 1.3B with structured prompting |
| Optional semantic search | FAISS + LangChain RAG |

---

## Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Cross-File Context** | Extracts imports, function calls, and dependencies across multiple files |
| ⚠️ **Bug Detection** | Identifies 8 common vulnerability patterns (SQL injection, eval(), pickle, etc.) |
| 📘 **Dual Summaries** | Generates both technical and beginner-friendly explanations |
| 🔗 **Dependency Tracking** | AST-based analysis of imported modules and called functions |
| 🧠 **Optional RAG** | FAISS-based semantic retrieval for smarter context selection |
| 📊 **Built-in Evaluation** | Readability scores (Flesch, Flesch-Kincaid) and bug detection accuracy |

### Supported Bug Patterns

| Pattern | Detection Rule |
|---------|----------------|
| Plain-text password comparison | `== "password"` |
| `eval()` / `exec()` usage | Security risk |
| SQL injection | String concatenation in `.execute()` |
| `pickle` deserialization | Unsafe with untrusted data |
| `os.system()` | Shell injection risk |
| Hardcoded passwords | Credentials in source |
| Dynamic attribute access | `setattr()` / `getattr()` |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           INPUT: Python Project                              │
│                    (target file + project root directory)                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CROSS-FILE CONTEXT EXTRACTOR                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────────┐  │
│  │  AST Parsing    │  │ Import Analysis │  │ Function Call Detection     │  │
│  │  (ast module)   │  │ Module names    │  │ Cross-file function lookup  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────────┘  │
│                                      │                                       │
│                              Related Files (max 3)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            BUG DETECTION MODULE                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │  Rule-based pattern matching (8 security & correctness patterns)      │  │
│  │  → Returns list of warning messages with line numbers (optional)      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        PROMPT ENGINEERING LAYER                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Structured Prompt Template:                                         │    │
│  │  • Code Context (main + related files)                              │    │
│  │  • Bug Warnings                                                     │    │
│  │  → 5 Required Output Sections                                       │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         LLM SUMMARIZATION ENGINE                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  deepseek-ai/deepseek-coder-1.3b-instruct                           │    │
│  │  • Deterministic decoding (temperature = 0.1)                       │    │
│  │  • Float16 quantization for efficiency                              │    │
│  │  • Max new tokens: 800                                              │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT (5 Sections)                             │
│  ┌───────────────┐ ┌─────────────────┐ ┌─────────────┐ ┌──────────────┐ ┌──────────────┐ │
│  │ Normal        │ │ Beginner        │ │ Bug         │ │ Cross-File   │ │ Commented    │ │
│  │ Summary       │ │ Explanation     │ │ Warning     │ │ Context      │ │ Code         │ │
│  │ (technical)   │ │ (step-by-step)  │ │ (security)  │ │ (dependencies)│ │ (with comments)│ │
│  └───────────────┘ └─────────────────┘ └─────────────┘ └──────────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EVALUATION MODULE                                   │
│  • Flesch Reading Ease    • Flesch-Kincaid Grade Level                       │
│  • Bug Detection Accuracy • Optional: Human Evaluation Form                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Optional RAG Pipeline (Enable with `--use_rag`)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│ Index all   │ ──▶ │ FAISS Vector │ ──▶ │ Semantic    │ ──▶ │ Augmented    │
│ .py files   │     │ Store        │     │ Search      │     │ Context      │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
```

---

## Project Structure

```
code_summarizer/
├── main.py                 # Entry point, orchestrates all modules
├── context_extractor.py   # AST-based dependency & cross-file context
├── bug_detector.py         # Rule-based bug/security warnings
├── summarizer.py           # LLM prompt generation + inference
├── evaluation.py           # Readability metrics & accuracy calculation
├── rag_retriever.py        # Optional FAISS/LangChain RAG module
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

---

## Installation

### Prerequisites

- Python 3.10 or higher
- pip package manager
- (Optional) CUDA-capable GPU for faster inference

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/code_summarizer.git
cd code_summarizer

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) For GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### requirements.txt

```
transformers>=4.36.0
torch>=2.0.0
accelerate>=0.25.0
sentencepiece>=0.1.99
bitsandbytes>=0.41.0
textstat>=0.7.3
langchain>=0.1.0
faiss-cpu>=1.7.4
tree-sitter>=0.20.0
```

---

## Usage

### Basic Usage

```bash
python main.py --project_root /path/to/project --target_file /path/to/project/main.py
```

### With RAG (semantic context retrieval)

```bash
python main.py --project_root /path/to/project --target_file /path/to/project/main.py --use_rag
```

### Custom Model

```bash
python main.py --project_root ./my_project --target_file ./my_project/app.py --model "deepseek-ai/deepseek-coder-6.7b-instruct"
```

### Command-line Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--project_root` | ✅ | - | Path to project root directory |
| `--target_file` | ✅ | - | Path to main Python file to summarize |
| `--model` | ❌ | `deepseek-ai/deepseek-coder-1.3b-base` | HuggingFace model name |
| `--use_rag` | ❌ | `False` | Enable FAISS-based semantic retrieval |

---

## Output Examples

The system generates **5 distinct outputs** for each target file:

### 1. Normal Summary (Technical)
```
Authenticates user credentials by comparing input password with 
stored hash using bcrypt, returning a session token on success.
```

### 2. Beginner Explanation (Step-by-Step)
```
1. The function takes a username and password from the user
2. It looks up the stored password hash for that username
3. It uses bcrypt to securely compare the input with the stored hash
4. If they match, it creates a new session token
5. Returns the token so the user stays logged in
```

### 3. Bug Warning
```
⚠️ Hardcoded password found in line 12 - store credentials in environment variables
⚠️ Using eval() on line 34 - can execute arbitrary code (security risk)
```

### 4. Cross-File Context
```
This function depends on:
- auth.py (imported: login, verify_hash)
- database.py (imported: get_user)
- utils.py (called: generate_token, log_attempt)
```

### 5. Commented Code (with explanatory comments)
```python
# Import bcrypt for secure password hashing
import bcrypt

def authenticate_user(username, password):
    # Query database for user record by username
    user = db.query("SELECT * FROM users WHERE username = ?", username)
    
    # Use bcrypt to compare input password with stored hash (secure)
    if bcrypt.checkpw(password.encode('utf-8'), user.password_hash):
        return generate_session_token()
    return None
```

### Evaluation Metrics (Auto-generated)
```
Flesch Reading Ease: 80.2 (higher = better, very easy to read)
Flesch-Kincaid Grade: 4.1 (US school grade level - accessible to beginners)
```

---

## Evaluation Metrics

The framework includes comprehensive evaluation capabilities:

| Metric | Formula | Description |
|--------|---------|-------------|
| **Flesch Reading Ease** | `206.835 - 1.015×(words/sentence) - 84.6×(syllables/word)` | 0-100 scale; higher = easier |
| **Flesch-Kincaid Grade** | `0.39×(words/sentence) + 11.8×(syllables/word) - 15.59` | US grade level required |
| **Bug Detection Recall** | `TP / (TP + FN)` | Percentage of known bugs found |
| **Dependency Accuracy** | `CorrectDependencies / TotalDependencies` | Context extraction correctness |

### Experimental Results (from paper)

| Metric | Result |
|--------|--------|
| Average Bug Recall | 90.2% |
| Dependency Accuracy | 96.9% |
| Average Flesch Reading Ease | 80.2 |
| Average Flesch-Kincaid Grade | 4.1 |
| Average Inference Time | 7.1 sec/file |
| Projects Evaluated | 10 |
| Functions Tested | 50 |
| Supported Bug Rules | 8 |

---

## Configuration

### Custom Bug Detection Rules

Edit `bug_detector.py` and modify the `RULES` list:

```python
RULES = [
    (r'==\s*["\'].*password.*["\']', "Plain-text password comparison..."),
    (r'eval\s*\(', "Dangerous use of eval()..."),
    # Add your custom rules here
    (r'custom_pattern', "Your warning message"),
]
```

### Custom Context Extraction

Modify `context_extractor.py` to adjust:

- `max_related` parameter (default: 3 related files)
- Import/func extraction logic
- AST parsing depth

### LLM Generation Parameters

In `summarizer.py`, adjust:

```python
outputs = self.model.generate(
    **inputs,
    max_new_tokens=800,      # Increase for longer outputs
    do_sample=False,         # Set True for more creative outputs
    temperature=0.7,         # Only if do_sample=True
)
```

---

## Limitations & Future Work

### Current Limitations

- **Python-only** — Dependency extraction works only for Python projects
- **Rule-based bugs** — May miss complex or context-dependent vulnerabilities
- **Hallucination risk** — Lightweight LLMs occasionally generate incorrect information
- **Limited token window** — Code context truncated to ~2000 characters

### Future Work

| Area | Planned Enhancement |
|------|---------------------|
| Multi-language | Support for JavaScript, Java, Go |
| Advanced context | Graph-based repository reasoning |
| Security analysis | Dynamic taint tracking integration |
| Model fine-tuning | Domain-specific educational data |
| Vector storage | Persistent FAISS index caching |

---

## Citation

If you use this work in your research, please cite:

```bibtex
@inproceedings{devthiya2025context,
  title={Context-Aware Beginner-Friendly and Bug-Aware Code Summarization Using Lightweight Large Language Models},
  author={Devthiya, Aashish},
  booktitle={Proceedings of ...},
  year={2025},
  organization={IIT Patna}
}
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [DeepSeek AI](https://deepseek.ai/) for the DeepSeek Coder model
- [HuggingFace](https://huggingface.co/) for transformers library
- IIT Patna Department of Computer Science & Engineering

---

## Contact

**Aashish Devthiya**  
Department of Computer Science and Engineering  
Indian Institute of Technology Patna  
📧 aashishdevthiya@gmail.com

---

*Built for educational software engineering, lightweight research environments, and AI-assisted code understanding.*