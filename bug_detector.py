import re
from typing import List, Tuple

class BugDetector:
    """Rule‑based detector for common bugs and security issues."""

    RULES = [
        (r'==\s*["\'].*password.*["\']', "Plain‑text password comparison – use a secure hashing library (bcrypt, argon2)."),
        (r'eval\s*\(', "Dangerous use of eval() – can execute arbitrary code."),
        (r'exec\s*\(', "Dangerous use of exec() – can execute arbitrary code."),
        (r'\.execute\s*\(.*\+', "Possible SQL injection – use parameterised queries."),
        (r'import\s+pickle', "Use of pickle – deserialization can be unsafe with untrusted data."),
        (r'os\.system\s*\(', "Shell injection risk – avoid os.system, use subprocess with list arguments."),
        (r'password\s*=\s*["\'][^"\']+["\']', "Hardcoded password – store credentials in environment variables."),
        (r'setattr\s*\(|getattr\s*\(', "Dynamic attribute access – can lead to unexpected behavior if not sanitized."),
    ]

    def __init__(self, custom_rules: List[Tuple[str, str]] = None):
        self.rules = custom_rules or self.RULES

    def detect(self, code: str) -> List[str]:
        """Return list of warning messages for the given code."""
        warnings = []
        for pattern, msg in self.rules:
            if re.search(pattern, code, re.IGNORECASE):
                warnings.append(msg)
        return warnings

    def detect_with_lines(self, code: str) -> List[Tuple[int, str]]:
        """Return (line_number, warning) for each match."""
        lines = code.splitlines()
        warnings_lines = []
        for i, line in enumerate(lines, start=1):
            for pattern, msg in self.rules:
                if re.search(pattern, line, re.IGNORECASE):
                    warnings_lines.append((i, msg))
                    break  # avoid duplicate messages on same line
        return warnings_lines