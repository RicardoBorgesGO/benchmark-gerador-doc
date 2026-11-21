"""Validação estrutural de blocos Mermaid e prompt de reparo."""

from __future__ import annotations

import re

from . import prompts

_MERMAID_BLOCK_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


def find_mermaid_blocks(text: str) -> list[str]:
    return _MERMAID_BLOCK_RE.findall(text)


def validate_block(block: str, language: str = "pt") -> list[str]:
    problems = []
    stripped = block.strip()

    if stripped.startswith("C4Context") or stripped.startswith("C4Container") or stripped.startswith("C4Component"):
        problems.append(prompts.mermaid_problem(language, "native_c4"))
    elif not (stripped.startswith("flowchart TB") or stripped.startswith("flowchart LR")):
        problems.append(prompts.mermaid_problem(language, "no_flowchart"))

    if "\\n" in block:
        problems.append(prompts.mermaid_problem(language, "newline"))

    if re.search(r"-->\|[^\"][^|]*\|", block):
        problems.append(prompts.mermaid_problem(language, "label_quotes"))

    return problems


def validate_document(markdown_text: str, language: str = "pt") -> dict[int, list[str]]:
    results = {}
    for i, block in enumerate(find_mermaid_blocks(markdown_text)):
        problems = validate_block(block, language)
        if problems:
            results[i] = problems
    return results


def build_repair_prompt(markdown_text: str, problems_by_block: dict[int, list[str]], language: str = "pt") -> str:
    label = "Bloco mermaid" if language == "pt" else "Mermaid block"
    problems_text = "\n".join(
        f"- {label} #{i + 1}: " + "; ".join(problems) for i, problems in problems_by_block.items()
    )
    return prompts.mermaid_repair_prompt(language, problems_text, markdown_text)
