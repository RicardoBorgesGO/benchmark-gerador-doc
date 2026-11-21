from __future__ import annotations

from pathlib import Path

IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules",
    "vendor", "dist", "build", "target", "__pycache__",
    ".idea", ".vscode", ".next", ".nuxt", "coverage",
}

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go",
    ".rs", ".c", ".h", ".cpp", ".hpp", ".cs", ".php", ".rb",
    ".swift", ".scala", ".sql", ".html", ".css", ".scss",
    ".vue", ".svelte", ".xml", ".yml", ".yaml", ".json",
    ".toml", ".ini", ".cfg", ".conf", ".md", ".rst", ".txt",
    ".properties", ".gradle", ".sh", ".bat", ".ps1",
}


def build_tree(repo_path: Path, max_entries: int = 300) -> str:
    rows = []
    for path in sorted(repo_path.rglob("*")):
        if len(rows) >= max_entries:
            rows.append("... [árvore truncada]")
            break
        rel = path.relative_to(repo_path)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        prefix = "  " * (len(rel.parts) - 1)
        marker = "[D]" if path.is_dir() else "[F]"
        rows.append(f"{prefix}{marker} {rel}")
    return "\n".join(rows)


def find_readme(repo_path: Path, max_chars: int = 200_000) -> str:
    candidates = sorted(p for p in repo_path.glob("README*") if p.is_file())
    candidates.sort(key=lambda p: (p.suffix.lower() != ".md", p.name))
    for path in candidates:
        try:
            return path.read_text(encoding="utf-8", errors="ignore")[:max_chars]
        except OSError:
            continue
    return ""
