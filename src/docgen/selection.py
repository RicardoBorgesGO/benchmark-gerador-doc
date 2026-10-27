from __future__ import annotations

from pathlib import Path

MANIFEST_NAMES = {"pyproject.toml", "package.json", "pom.xml", "build.gradle"}
SOURCE_SUFFIXES = {".py", ".java", ".ts", ".tsx", ".js", ".php"}


def priority(path: str) -> int:
    p = Path(path)
    score = 0
    if p.name.lower().startswith("readme"):
        score += 100
    if p.name.lower() in MANIFEST_NAMES:
        score += 80
    if p.suffix.lower() in SOURCE_SUFFIXES:
        score += 20
    return score


def heuristic_top_k(entries: list[tuple[str, str]], k: int) -> list[tuple[str, str]]:
    ranked = sorted(entries, key=lambda e: (-priority(e[0]), -e[1].count("\n"), e[0]))
    return ranked[:k]
