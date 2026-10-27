from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from . import baseline, mermaid_validate
from .analyzer import build_tree, detect_project_category, read_many, summarize_stats
from .embeddings import EmbeddingIndex
from .ollama_client import OllamaClient, UsageStats
from .repo_map import build_repo_map, extract_signature
from .selection import heuristic_top_k
from .sections import SECTIONS, Section, domain_adaptation_hint

STRATEGIES = ("baseline", "rag")
CONTEXTS = ("completo", "topk")
SELECTIONS = ("embeddings", "heuristica")
MAX_RETRIEVED_CHARS = 4000

SYSTEM_PROMPT = """
Você é um engenheiro de software responsável por produzir documentação técnica
precisa a partir de um repositório de código.

Regras:
- Não invente funcionalidades, componentes, dependências ou fluxos.
- Diferencie fatos observados de inferências.
- Quando a evidência for insuficiente, escreva "não identificado no código analisado".
- Use nomes reais de arquivos, classes, funções, módulos e dependências quando disponíveis.
- Priorize relações entre componentes e o propósito do sistema.
- A documentação deve ser útil para onboarding de um novo desenvolvedor.
- Responda em português do Brasil.
"""

EVIDENCE_RULE = """
Sempre que citar arquivo, classe, função ou comando, escreva o nome exato entre crases (`assim`).
Não cite nomes que não aparecem no código fornecido.
"""


@dataclass
class SectionResult:
    section: Section
    plan: str
    content: str
    retrieved_paths: list[str]
    mermaid_repaired: bool = False
    elapsed_seconds: float = 0.0
    judge_feedback: str | None = None
    prompt_tokens: int = 0
    output_tokens: int = 0
    truncated_calls: int = 0


@dataclass
class PipelineResult:
    repo_name: str
    category: str
    tree: str
    stats: dict
    strategy: str = "rag"
    context: str = "topk"
    selection: str = "embeddings"
    top_k: int = 0
    model: str = ""
    num_ctx: int = 0
    files_in_input: int = 0
    sections: list[SectionResult] = field(default_factory=list)
    total_elapsed_seconds: float = 0.0
    usage: UsageStats = field(default_factory=UsageStats)

    def assemble_markdown(self) -> str:
        parts = [f"# Guia de Projeto de Software — {self.repo_name}\n"]
        parts.extend(r.content.strip() for r in self.sections)
        return "\n\n---\n\n".join(parts)


def run_pipeline(
    repo_path: Path,
    repo_name: str,
    files,
    client: OllamaClient,
    strategy: str = "rag",
    context: str = "topk",
    selection: str = "embeddings",
    embed_model: str = "nomic-embed-text",
    top_k: int = 8,
    use_plan_step: bool = True,
    use_mermaid_repair: bool = True,
    use_evidence_rule: bool = True,
    progress_callback=None,
) -> PipelineResult:
    if strategy not in STRATEGIES:
        raise ValueError(f"strategy deve ser uma de {STRATEGIES}")
    if context not in CONTEXTS:
        raise ValueError(f"context deve ser um de {CONTEXTS}")
    if selection not in SELECTIONS:
        raise ValueError(f"selection deve ser um de {SELECTIONS}")

    def notify(stage: str, detail: str, fraction: float) -> None:
        if progress_callback:
            progress_callback(stage, detail, fraction)

    total_start = time.perf_counter()
    usage_start = client.usage.snapshot()

    notify("analise", "Lendo arquivos", 0.02)
    category = detect_project_category(repo_path, files)
    tree = build_tree(repo_path)

    if strategy == "baseline":
        candidates, scan_stats = baseline.scan_files(repo_path)
        stats = {**scan_stats, "files_analyzed": scan_stats["selected_files"]}
    else:
        candidates = read_many(repo_path, files)
        stats = summarize_stats(repo_path, files)

    content_by_path = dict(candidates)
    domain_hint = domain_adaptation_hint(category)
    evidence = EVIDENCE_RULE if use_evidence_rule else ""

    repo_map_text = ""
    index: EmbeddingIndex | None = None
    fixed_selection: list[tuple[str, str]] = []

    if strategy == "rag":
        notify("repo_map", "Montando mapa estrutural", 0.08)
        repo_map_text = build_repo_map(candidates)

    if context == "topk" and selection == "embeddings":
        notify("embeddings", "Calculando embeddings", 0.15)
        index = EmbeddingIndex(client, embed_model=embed_model)
        index.build([(p, extract_signature(p, c)) for p, c in candidates])
    elif context == "topk":
        fixed_selection = heuristic_top_k(candidates, top_k)

    def select_files(section: Section) -> list[tuple[str, str]]:
        if context == "completo":
            return candidates
        if selection == "heuristica":
            return fixed_selection
        if index is None or index.is_empty():
            return []
        found = index.query(section.retrieval_query, top_k=top_k)
        return [(r.path, content_by_path.get(r.path, r.content)) for r in found]

    template = baseline.user_template(context, selection)

    results: list[SectionResult] = []
    for i, section in enumerate(SECTIONS):
        notify(section.key, f"Gerando: {section.title}", 0.2 + (i / len(SECTIONS)) * 0.75)
        section_start = time.perf_counter()
        before = client.usage.snapshot()

        plan = ""
        system = SYSTEM_PROMPT
        selected = select_files(section)
        retrieved_paths = [p for p, _ in selected]

        if context == "topk" or strategy == "rag":
            limited = [(p, c[:MAX_RETRIEVED_CHARS]) for p, c in selected]
        else:
            limited = selected

        if strategy == "baseline":
            system = baseline.system_prompt_for(section.key)
            prompt = template.format(code=baseline.format_files(limited))
        else:
            code_text = "\n\n".join(f"--- {p} ---\n{c}" for p, c in limited)

            if use_plan_step:
                plan_prompt = f"""
{domain_hint}

MAPA ESTRUTURAL DO REPOSITÓRIO:
{repo_map_text[:8000]}

CÓDIGO PARA ESTA SEÇÃO:
{code_text}

TAREFA: {section.plan_instruction}

Responda de forma curta (lista ou JSON simples).
"""
                plan = client.chat(system, plan_prompt, temperature=0.1)

            prompt = f"""
{domain_hint}

{evidence}
{section.few_shot_example}

PLANO:
{plan if plan else "(sem etapa de plano)"}

CÓDIGO PARA ESTA SEÇÃO:
{code_text}

{section.write_instruction}
"""

        content = client.chat(system, prompt, temperature=0.1)

        mermaid_repaired = False
        if use_mermaid_repair and section.needs_mermaid:
            problems = mermaid_validate.validate_document(content)
            if problems:
                content = client.chat(system, mermaid_validate.build_repair_prompt(content, problems), temperature=0.1)
                mermaid_repaired = True

        used = client.usage.minus(before)
        results.append(
            SectionResult(
                section=section,
                plan=plan,
                content=content,
                retrieved_paths=retrieved_paths,
                mermaid_repaired=mermaid_repaired,
                elapsed_seconds=time.perf_counter() - section_start,
                prompt_tokens=used.prompt_tokens,
                output_tokens=used.output_tokens,
                truncated_calls=used.truncated_calls,
            )
        )

    notify("concluido", "Guia gerado", 1.0)

    return PipelineResult(
        repo_name=repo_name,
        category=category,
        tree=tree,
        stats=stats,
        strategy=strategy,
        context=context,
        selection=selection if context == "topk" else "-",
        top_k=top_k if context == "topk" else 0,
        model=client.model,
        num_ctx=client.num_ctx,
        files_in_input=len(candidates),
        sections=results,
        total_elapsed_seconds=time.perf_counter() - total_start,
        usage=client.usage.minus(usage_start),
    )
