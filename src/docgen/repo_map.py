"""Assinaturas compactas (classes, funções, imports) usadas como resumo estrutural dos arquivos."""

from __future__ import annotations

import ast
import re
from pathlib import Path

_GENERIC_PATTERNS = [
    re.compile(r"^\s*(export\s+)?(default\s+)?(async\s+)?function\b.*"),
    re.compile(r"^\s*(export\s+)?class\b.*"),
    re.compile(r"^\s*(export\s+)?interface\b.*"),
    re.compile(r"^\s*(public|private|protected)\s+[\w<>\[\],\s]+\(.*\).*"),
    re.compile(r"^\s*func\s+\w+.*"),
    re.compile(r"^\s*(public|private|internal)\s+(class|interface|struct)\b.*"),
    re.compile(r"^\s*(pub\s+)?fn\s+\w+.*"),
    re.compile(r"^\s*def\s+\w+.*"),
    re.compile(r"^\s*(const|let|var)\s+\w+\s*=\s*(async\s*)?\(.*=>.*"),
]

_MAX_LINES = 80
_TEXT_SUFFIXES = {".md", ".rst", ".txt", ".toml", ".json", ".yaml", ".yml", ".cfg", ".ini", ".properties"}


def _first_line(doc: str | None) -> str:
    return doc.strip().splitlines()[0] if doc and doc.strip() else ""


def _python_signature(content: str) -> str:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return _generic_signature(content)

    lines: list[str] = []
    module_doc = _first_line(ast.get_docstring(tree))
    if module_doc:
        lines.append(f'"""{module_doc}"""')

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = ", ".join(a.arg for a in node.args.args)
            prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            doc = _first_line(ast.get_docstring(node))
            lines.append(f"{prefix} {node.name}({args})" + (f"  # {doc}" if doc else ""))
        elif isinstance(node, ast.ClassDef):
            bases = ", ".join(b.id for b in node.bases if isinstance(b, ast.Name))
            doc = _first_line(ast.get_docstring(node))
            lines.append(f"class {node.name}" + (f"({bases})" if bases else "") + (f"  # {doc}" if doc else ""))
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    lines.append(f"    def {sub.name}({', '.join(a.arg for a in sub.args.args)})")
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            lines.append(ast.unparse(node))
        elif isinstance(node, ast.Assign):
            names = ", ".join(t.id for t in node.targets if isinstance(t, ast.Name))
            if names and names.isupper():
                lines.append(f"{names} = ...")

    return "\n".join(line for line in lines if line.strip())


def _generic_signature(content: str) -> str:
    lines = []
    for line in content.splitlines():
        if any(p.match(line) for p in _GENERIC_PATTERNS):
            lines.append(line.strip())
        if len(lines) >= _MAX_LINES:
            lines.append("...")
            break
    return "\n".join(lines)


def extract_signature(path: str, content: str) -> str:
    suffix = Path(path).suffix.lower()
    name = Path(path).name.lower()

    if name.startswith("readme") or suffix in _TEXT_SUFFIXES:
        return content[:4000]

    signature = _python_signature(content) if suffix == ".py" else _generic_signature(content)
    return signature or content[:500]


def build_repo_map(files_with_content: list[tuple[str, str]]) -> str:
    blocks = []
    for path, content in files_with_content:
        signature = extract_signature(path, content)
        if signature.strip():
            blocks.append(f"### {path}\n{signature}")
    return "\n\n".join(blocks)
