from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path

from . import harness, mermaid_validate, prompts
from .analyzer import build_tree
from .documents import DOCUMENTS, Document
from .ollama_client import OllamaClient, UsageStats

MAX_CHARS_PER_FILE = 4000


@dataclass
class DocumentResult:
    document: Document
    content: str
    files_sent: list[str]
    mermaid_repaired: bool = False
    elapsed_seconds: float = 0.0
    prompt_tokens: int = 0
    output_tokens: int = 0
    truncated_calls: int = 0
    judge: dict | None = None
    judge_raw: str | None = None


@dataclass
class PipelineResult:
    repo_name: str
    language: str
    top_k: int | None
    model: str
    num_ctx: int
    tree: str
    stats: dict
    documents: list[DocumentResult] = field(default_factory=list)
    total_elapsed_seconds: float = 0.0
    usage: UsageStats = field(default_factory=UsageStats)

    @property
    def files_in_input(self) -> int:
        return self.stats["selected_files"]

    def assemble_markdown(self) -> str:
        parts = [f"# {prompts.guide_title(self.language)} — {self.repo_name}\n"]
        parts.extend(d.content.strip() for d in self.documents)
        return "\n\n---\n\n".join(parts)


def generate_documents(
    repo_path: Path,
    repo_name: str,
    client: OllamaClient,
    language: str = "pt",
    top_k: int | None = None,
    max_chars_per_file: int = MAX_CHARS_PER_FILE,
    use_mermaid_repair: bool = False,
    progress_callback=None,
) -> PipelineResult:
    if language not in prompts.LANGUAGES:
        raise ValueError(f"language deve ser um de {prompts.LANGUAGES}")

    def notify(stage: str, detail: str, fraction: float) -> None:
        if progress_callback:
            progress_callback(stage, detail, fraction)

    total_start = time.perf_counter()
    usage_start = client.usage.snapshot()

    notify("analise", "Lendo arquivos", 0.02)
    entries, stats = harness.scan_files(repo_path)
    tree = build_tree(repo_path)

    selected = harness.select_files(entries, top_k, max_chars_per_file)
    code = harness.format_files(selected)
    template = prompts.user_template(language, partial=bool(top_k))
    user_prompt = template.format(code=code)
    files_sent = [p for p, _ in selected]

    results: list[DocumentResult] = []
    for i, document in enumerate(DOCUMENTS):
        notify(document.key, f"Gerando: {document.title(language)}", 0.05 + (i / len(DOCUMENTS)) * 0.9)
        start = time.perf_counter()
        before = client.usage.snapshot()

        system = prompts.system_prompt(document.filename, language)
        content = client.chat(system, user_prompt)

        repaired = False
        if use_mermaid_repair and document.needs_mermaid:
            problems = mermaid_validate.validate_document(content, language)
            if problems:
                content = client.chat(system, mermaid_validate.build_repair_prompt(content, problems, language))
                repaired = True

        used = client.usage.minus(before)
        results.append(
            DocumentResult(
                document=document,
                content=content,
                files_sent=files_sent,
                mermaid_repaired=repaired,
                elapsed_seconds=time.perf_counter() - start,
                prompt_tokens=used.prompt_tokens,
                output_tokens=used.output_tokens,
                truncated_calls=used.truncated_calls,
            )
        )

    notify("concluido", "Guia gerado", 1.0)

    return PipelineResult(
        repo_name=repo_name,
        language=language,
        top_k=top_k or None,
        model=client.model,
        num_ctx=client.num_ctx,
        tree=tree,
        stats=stats,
        documents=results,
        total_elapsed_seconds=time.perf_counter() - total_start,
        usage=client.usage.minus(usage_start),
    )
