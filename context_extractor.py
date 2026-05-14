import ast
import os
from typing import List, Set, Dict

class CrossFileContextExtractor:
    """Extracts imports, function calls, and builds cross-file context."""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.file_cache: Dict[str, str] = {}  # path -> content

    def _read_file(self, file_path: str) -> str:
        if file_path not in self.file_cache:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.file_cache[file_path] = f.read()
        return self.file_cache[file_path]

    def extract_imports(self, file_path: str) -> List[str]:
        """Return list of module names imported in the file."""
        try:
            tree = ast.parse(self._read_file(file_path))
        except SyntaxError:
            return []
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split('.')[0])
        return list(set(imports))

    def extract_function_calls(self, file_path: str) -> List[str]:
        """Return list of called function names (simple names only)."""
        try:
            tree = ast.parse(self._read_file(file_path))
        except SyntaxError:
            return []
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.append(node.func.id)
        return list(set(calls))

    def find_related_files(self, main_file: str) -> List[str]:
        """
        Find files that are likely related to the main_file.
        Uses imports and function calls to locate definitions.
        """
        imports = self.extract_imports(main_file)
        calls = self.extract_function_calls(main_file)
        related = set()

        # Search all .py files in project root (excluding main file)
        all_files = []
        for root, _, files in os.walk(self.project_root):
            for f in files:
                if f.endswith('.py'):
                    full = os.path.join(root, f)
                    if full != main_file:
                        all_files.append(full)

        # Heuristic: if a file defines a function that is called, or its module name is imported
        for candidate in all_files:
            base_name = os.path.splitext(os.path.basename(candidate))[0]
            # Check if module name matches any import
            if base_name in imports:
                related.add(candidate)
            # Check if candidate defines any called function
            defined_funcs = self._extract_defined_functions(candidate)
            if set(defined_funcs) & set(calls):
                related.add(candidate)
        return list(related)

    def _extract_defined_functions(self, file_path: str) -> List[str]:
        try:
            tree = ast.parse(self._read_file(file_path))
        except SyntaxError:
            return []
        funcs = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                funcs.append(node.name)
        return funcs

    def build_context(self, main_file: str, max_related: int = 3) -> str:
        """
        Returns a string containing main_file + up to max_related related files.
        Each related file is prefixed with a marker.
        """
        context = f"# MAIN FILE: {os.path.basename(main_file)}\n"
        context += self._read_file(main_file) + "\n\n"
        related_files = self.find_related_files(main_file)[:max_related]
        for rf in related_files:
            context += f"# RELATED FILE: {os.path.basename(rf)}\n"
            context += self._read_file(rf) + "\n\n"
        return context