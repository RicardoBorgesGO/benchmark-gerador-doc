"""Estratégia baseline: prompts de sistema por documento e seleção de arquivos originais do projeto."""

from __future__ import annotations

import os
from pathlib import Path

from .baseline_prompts import SYSTEM_PROMPTS

IGNORABLE_FOLDERS = ["node_modules", ".git", "__pycache__", "env", "venv", "dist", "build", "test", "tests"]
VALID_FILE_EXTENSIONS = (
    ".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".java", ".cs", ".cpp", ".c", ".h", ".hpp", ".rs", ".php", ".rb",
    ".html", ".css", ".scss", ".vue", ".svelte",
    ".json", ".toml", ".yaml", ".yml", ".ini", ".xml", ".gradle", ".properties",
    ".sh", ".ps1", ".bat", ".cmd", ".sql", ".prisma",
)

# seção do docgen -> documento do prompt original
DOCUMENT_BY_SECTION = {
    "tutorial": "01_tutorials.md",
    "howto": "02_how_to_guide.md",
    "reference": "03_reference.md",
    "explanation": "04_explanation.md",
    "c4_level1": "C4_architecture_level1.md",
    "c4_level2": "C4_architecture_level2.md",
    "c4_level3": "C4_architecture_level3.md",
}

USER_TEMPLATE = (
    "Abaixo está o código-fonte completo do repositório delimitado pelas tags <repository_code>.\n"
    "Analise o código e gere OBRIGATORIAMENTE o documento específico solicitado no seu SYSTEM PROMPT.\n\n"
    "<repository_code>\n{code}\n</repository_code>\n\n"
    "REGRAS DE EXECUÇÃO:\n"
    "1. Idioma: EXCLUSIVAMENTE Português (Brasil).\n"
    "2. Fonte da Verdade: Use APENAS o código dentro de <repository_code>.\n"
    "3. ADAPTAÇÃO DE DOMÍNIO: Classifique internamente o software em sua categoria (API, Game, Lib, CLI, UI/App ou Plugin) "
    "e use APENAS a terminologia e tipos de exemplos próprios dessa categoria no documento.\n"
    "4. FOCO EXCLUSIVO DO DOCUMENTO: Não gere uma visão geral genérica. Execute ESTRITAMENTE a estrutura, "
    "o propósito e o nível de detalhe definidos no seu SYSTEM PROMPT.\n"
    "5. Formato: Retorne APENAS Markdown puro. Para diagramas Mermaid, use sintaxe `flowchart TB/LR` pura.\n"
    "6. Início Imediato: Comece sua resposta diretamente com o caractere `#` do título principal."
)


_INTRO_COMPLETE = "Abaixo está o código-fonte completo do repositório delimitado"
_INTRO_BY_RELEVANCE = "Abaixo estão trechos do código-fonte do repositório, selecionados por relevância e delimitados"
_INTRO_MAIN_FILES = "Abaixo estão os principais arquivos do repositório, delimitados"


def user_template(context: str, selection: str) -> str:
    if context == "completo":
        return USER_TEMPLATE
    intro = _INTRO_BY_RELEVANCE if selection == "embeddings" else _INTRO_MAIN_FILES
    return USER_TEMPLATE.replace(_INTRO_COMPLETE, intro)


def system_prompt_for(section_key: str) -> str:
    return SYSTEM_PROMPTS[DOCUMENT_BY_SECTION[section_key]]


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

    return entries, {"total_files": total_files, "selected_files": len(entries)}


def format_files(entries: list[tuple[str, str]]) -> str:
    return "\n".join(f"--- {path} ---\n{content}\n" for path, content in entries)
