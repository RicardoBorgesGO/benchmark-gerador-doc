"""Documentação de referência de um repositório (README original ou traduzido)."""

from __future__ import annotations

import re
from pathlib import Path

from .analyzer import find_readme

DEFAULT_TRANSLATED_DIR = "translated_readme"


def _name_variants(repo_name: str) -> list[str]:
    normalized = re.sub(r"[^A-Za-z0-9]+", "_", repo_name).strip("_")
    return list(dict.fromkeys([repo_name, normalized, normalized.lower()]))


def find_translated_readme(repo_name: str, directory: str | Path = DEFAULT_TRANSLATED_DIR) -> str | None:
    base = Path(directory)
    if not base.is_dir():
        return None
    for variant in _name_variants(repo_name):
        path = base / f"{variant}.md"
        if path.is_file():
            return path.read_text(encoding="utf-8", errors="ignore")
    return None


def reference_for(
    repo_path: Path,
    repo_name: str,
    language: str,
    translated_dir: str | Path = DEFAULT_TRANSLATED_DIR,
) -> tuple[str, str]:
    """Retorna (texto, origem): 'translated', 'original' ou 'none'."""
    if language == "pt":
        translated = find_translated_readme(repo_name, translated_dir)
        if translated is not None:
            return translated, "translated"
    original = find_readme(repo_path)
    return (original, "original") if original.strip() else ("", "none")
