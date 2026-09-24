from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules",
    "vendor", "dist", "build", "target", "__pycache__",
    ".idea", ".vscode", ".next", ".nuxt", "coverage"
}

IGNORED_FILES = {
    ".DS_Store", "package-lock.json", "pnpm-lock.yaml",
    "yarn.lock", "poetry.lock"
}

TEXT_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go",
    ".rs", ".c", ".h", ".cpp", ".hpp", ".cs", ".php", ".rb",
    ".swift", ".scala", ".sql", ".html", ".css", ".scss",
    ".vue", ".svelte", ".xml", ".yml", ".yaml", ".json",
    ".toml", ".ini", ".cfg", ".conf", ".md", ".rst", ".txt",
    ".properties", ".gradle", ".sh", ".bat", ".ps1"
}

IMPORTANT_FILENAMES = {
    "README", "README.md", "README.rst", "LICENSE", "Dockerfile",
    "docker-compose.yml", "compose.yml", "pyproject.toml",
    "package.json", "pom.xml", "build.gradle", "requirements.txt",
    "composer.json", "go.mod", "Cargo.toml"
}


@dataclass
class FileInfo:
    path: str
    size: int
    lines: int
    language: str


def is_candidate(path: Path, max_file_bytes: int = 60_000) -> bool:
    if any(part in IGNORED_DIRS for part in path.parts):
        return False
    if path.name in IGNORED_FILES:
        return False
    if path.name in IMPORTANT_FILENAMES:
        return True
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return False
    try:
        return path.stat().st_size <= max_file_bytes
    except OSError:
        return False


def language_for(path: Path) -> str:
    return path.suffix.lower().lstrip(".") or "text"


def collect_files(repo_path: Path, max_files: int = 60) -> list[FileInfo]:
    candidates = []
    for path in repo_path.rglob("*"):
        if path.is_file() and is_candidate(path):
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                candidates.append(
                    FileInfo(
                        path=str(path.relative_to(repo_path)),
                        size=path.stat().st_size,
                        lines=text.count("\n") + 1,
                        language=language_for(path),
                    )
                )
            except OSError:
                continue

    def score(item: FileInfo) -> tuple[int, int, str]:
        name = Path(item.path).name.lower()
        priority = 0
        if name.startswith("readme"):
            priority += 100
        if name in {"pyproject.toml", "package.json", "pom.xml", "build.gradle"}:
            priority += 80
        if Path(item.path).suffix.lower() in {".py", ".java", ".ts", ".tsx", ".js", ".php"}:
            priority += 20
        return (-priority, -item.lines, item.path)

    candidates.sort(key=score)
    return candidates[:max_files]


def read_file(repo_path: Path, relative_path: str, max_chars: int = 60_000) -> str:
    path = repo_path / relative_path
    text = path.read_text(encoding="utf-8", errors="ignore")
    if len(text) > max_chars:
        return text[:max_chars] + "\n\n[TRUNCADO PELO PILOTO]"
    return text


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


def summarize_stats(repo_path: Path, files: list[FileInfo]) -> dict:
    total_bytes = 0
    all_files = 0
    for p in repo_path.rglob("*"):
        if p.is_file() and not any(part in IGNORED_DIRS for part in p.parts):
            all_files += 1
            try:
                total_bytes += p.stat().st_size
            except OSError:
                pass

    by_language = {}
    for f in files:
        by_language[f.language] = by_language.get(f.language, 0) + 1

    return {
        "all_files_visible": all_files,
        "files_analyzed": len(files),
        "repository_bytes_visible": total_bytes,
        "languages_in_analyzed_files": by_language,
    }
