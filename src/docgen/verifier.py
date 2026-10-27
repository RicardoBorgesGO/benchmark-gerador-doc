"""Confere se arquivos e identificadores citados entre crases existem no repositório."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from .analyzer import IGNORED_DIRS, TEXT_EXTENSIONS

_BACKTICK_RE = re.compile(r"(?<!`)`([^`\n]{2,80})`(?!`)")
_PATH_RE = re.compile(r"^[\w.\-/\\]+\.[A-Za-z0-9]{1,6}$")
_IDENT_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)*(\(\))?$")

_STOPWORDS = {
    "python", "pip", "npm", "node", "yarn", "git", "docker", "true", "false", "none",
    "null", "main", "test", "tests", "src", "http", "https", "localhost", "json",
    "yaml", "markdown", "mermaid", "flowchart", "string", "int", "float", "bool",
    "list", "dict", "self", "return", "import", "from", "class", "def", "function",
    "const", "var", "let", "async", "await", "print", "ollama", "streamlit",
}


@dataclass
class VerificationReport:
    checked: int = 0
    missing: list[str] = field(default_factory=list)
    supported: list[str] = field(default_factory=list)

    @property
    def n_missing(self) -> int:
        return len(self.missing)

    @property
    def support_rate(self) -> float:
        return 1.0 if self.checked == 0 else (self.checked - self.n_missing) / self.checked

    def to_dict(self) -> dict:
        return {
            "referencias_verificadas": self.checked,
            "referencias_inexistentes": self.n_missing,
            "taxa_de_suporte": round(self.support_rate, 4),
            "exemplos_inexistentes": self.missing[:15],
        }


def _repo_index(repo_path: Path) -> tuple[set[str], set[str], str]:
    """(caminhos relativos, basenames, texto concatenado em minúsculas)."""
    rel_paths: set[str] = set()
    basenames: set[str] = set()
    chunks: list[str] = []
    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_path)
        if any(part in IGNORED_DIRS for part in rel.parts):
            continue
        rel_paths.add(str(rel).replace("\\", "/"))
        basenames.add(path.name)
        if path.suffix.lower() in TEXT_EXTENSIONS:
            try:
                if path.stat().st_size <= 400_000:
                    chunks.append(path.read_text(encoding="utf-8", errors="ignore"))
            except OSError:
                pass
    return rel_paths, basenames, "\n".join(chunks)


def verify_document(markdown_text: str, repo_path: Path) -> VerificationReport:
    rel_paths, basenames, corpus = _repo_index(repo_path)
    corpus_lower = corpus.lower()
    report = VerificationReport()
    seen: set[str] = set()

    for raw in _BACKTICK_RE.findall(markdown_text):
        token = raw.strip().rstrip(".,;:")
        if token in seen or " " in token:
            continue
        seen.add(token)

        if _PATH_RE.match(token):
            norm = token.replace("\\", "/").lstrip("./")
            ext = "." + norm.rsplit(".", 1)[-1].lower()
            if ext not in TEXT_EXTENSIONS and ext not in {".png", ".svg", ".lock"}:
                continue
            report.checked += 1
            ok = (
                norm in rel_paths
                or any(p.endswith("/" + norm) for p in rel_paths)
                or norm.split("/")[-1] in basenames
            )
            (report.supported if ok else report.missing).append(token)
        elif _IDENT_RE.match(token):
            ident = token.replace("()", "")
            if len(ident) < 4 or ident.lower() in _STOPWORDS:
                continue
            report.checked += 1
            last = ident.split(".")[-1].lower()
            ok = ident.lower() in corpus_lower or last in corpus_lower
            (report.supported if ok else report.missing).append(token)

    return report
