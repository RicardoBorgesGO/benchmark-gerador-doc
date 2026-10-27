"""Validação estrutural de blocos Mermaid e prompt de reparo."""

from __future__ import annotations

import re

_MERMAID_BLOCK_RE = re.compile(r"```mermaid\s*\n(.*?)```", re.DOTALL)


def find_mermaid_blocks(text: str) -> list[str]:
    return _MERMAID_BLOCK_RE.findall(text)


def validate_block(block: str) -> list[str]:
    problems = []
    stripped = block.strip()

    if stripped.startswith("C4Context") or stripped.startswith("C4Container"):
        problems.append(
            "Usa a sintaxe nativa C4Context/C4Container, que não é suportada "
            "por todos os renderizadores. Deve usar `flowchart TB` ou `flowchart LR`."
        )
    elif not (stripped.startswith("flowchart TB") or stripped.startswith("flowchart LR")):
        problems.append("Não começa com `flowchart TB` ou `flowchart LR`.")

    if "\\n" in block:
        problems.append(
            "Contém `\\n` literal dentro de rótulo; quebras de linha devem usar `<br/>`."
        )

    if re.search(r"-->\|[^\"][^|]*\|", block):
        problems.append(
            "Há rótulo de seta sem aspas duplas. Formato exigido: "
            '`Origem -->|"Rótulo"| Destino`.'
        )

    return problems


def validate_document(markdown_text: str) -> dict[int, list[str]]:
    blocks = find_mermaid_blocks(markdown_text)
    results = {}
    for i, block in enumerate(blocks):
        problems = validate_block(block)
        if problems:
            results[i] = problems
    return results


def build_repair_prompt(markdown_text: str, problems_by_block: dict[int, list[str]]) -> str:
    problems_text = "\n".join(
        f"- Bloco mermaid #{i + 1}: " + "; ".join(probs)
        for i, probs in problems_by_block.items()
    )
    return f"""
O documento abaixo tem problemas de sintaxe Mermaid que precisam ser corrigidos.
Corrija APENAS a sintaxe Mermaid apontada, mantendo todo o resto do documento
(texto, tabelas, estrutura) exatamente como está.

PROBLEMAS ENCONTRADOS:
{problems_text}

DOCUMENTO ORIGINAL:
{markdown_text}

Retorne o documento completo corrigido, começando direto com o título (#).
"""
