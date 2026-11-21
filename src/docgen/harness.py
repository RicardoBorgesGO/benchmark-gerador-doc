"""Seleção de arquivos do harness: extensões válidas, sem pastas de teste, documentação e ocultas."""

from __future__ import annotations

import os
from pathlib import Path

from .hardware import estimate_tokens_from_chars
from .selection import heuristic_top_k

IGNORABLE_FOLDERS = ["node_modules", ".git", "__pycache__", "doc", "docs", "env", "venv", "dist", "build", "test", "tests"]
VALID_FILE_EXTENSIONS = (
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".cs", ".cpp", ".c", ".h", ".hpp", ".rs", ".php", ".rb",
    ".html", ".css", ".scss", ".vue", ".svelte",
    ".json", ".toml", ".yaml", ".yml", ".ini", ".xml", ".gradle", ".properties",
    ".sh", ".ps1", ".bat", ".cmd", ".sql", ".prisma",
)


def scan_files(repo_path: Path) -> tuple[list[tuple[str, str]], dict]:
    root_path = str(repo_path)
    entries: list[tuple[str, str]] = []
    total_files = 0

    for root, _, files in os.walk(root_path):
        relative_root = os.path.relpath(root, root_path)
        parts = [] if relative_root == "." else relative_root.split(os.sep)
        if any(p in IGNORABLE_FOLDERS or p.startswith(".") for p in parts):
            continue
        for name in files:
            total_files += 1
            if not name.endswith(VALID_FILE_EXTENSIONS):
                continue
            full_path = os.path.join(root, name)
            try:
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
            except OSError:
                continue
            entries.append((os.path.relpath(full_path, root_path), content))

    characters = sum(len(c) for _, c in entries)
    stats = {
        "total_files": total_files,
        "selected_files": len(entries),
        "characters": characters,
        "estimated_tokens": estimate_tokens_from_chars(characters),
    }
    return entries, stats


def scan_repository(path: str | Path) -> str:
    entries, _ = scan_files(Path(path))
    return format_files(entries)


def select_files(
    entries: list[tuple[str, str]], top_k: int | None, max_chars_per_file: int
) -> list[tuple[str, str]]:
    if not top_k:
        return entries
    return [(p, c[:max_chars_per_file]) for p, c in heuristic_top_k(entries, top_k)]


def format_files(entries: list[tuple[str, str]]) -> str:
    return "\n".join(f"--- {path} ---\n{content}\n" for path, content in entries)
