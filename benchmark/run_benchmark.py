"""Executa repositórios x modelos x estratégias x repetições e grava runs.csv e sections.csv."""

from __future__ import annotations

import argparse
import csv
import re
import shutil
import traceback
from pathlib import Path

from . import config as cfg
from docgen.analyzer import collect_files, find_reference_doc
from docgen.evaluation import evaluate_run, run_judge
from docgen.hardware import GpuSampler, estimate_vram_gb
from docgen.ollama_client import OllamaClient
from docgen.pipeline import run_pipeline
from docgen.repository import load_from_github

RUN_FIELDS = [
    "repo", "porte", "modelo", "estrategia", "num_ctx", "repeticao", "seed",
    "arquivos_na_entrada", "categoria", "cenario", "tempo_total_s",
    "tokens_prompt", "tokens_saida", "chamadas", "chamadas_truncadas",
    "mermaid_reparado", "meteor", "bert_precision", "bert_recall", "bert_f1",
    "overlap_score", "falhas_juiz_total", "refs_verificadas", "refs_inexistentes",
    "taxa_suporte_refs", "energia_wh", "potencia_media_w", "vram_pico_mb",
    "vram_estimada_gb", "erro",
]
SECTION_FIELDS = [
    "repo", "modelo", "estrategia", "num_ctx", "repeticao", "secao",
    "tempo_s", "tokens_prompt", "tokens_saida", "chamadas_truncadas",
    "arquivos_recuperados", "mermaid_reparado",
]


def slug(text: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", text)


def append_row(path: Path, fields: list[str], row: dict) -> None:
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if new:
            writer.writeheader()
        writer.writerow(row)


def tier_of(url: str) -> str:
    for tier, urls in cfg.REPOSITORIES.items():
        if url in urls:
            return tier
    return "custom"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repos", nargs="*", help="URLs GitHub (substitui --tier)")
    ap.add_argument("--tier", choices=list(cfg.REPOSITORIES), nargs="*", help="porte(s) de repositório")
    ap.add_argument("--models", nargs="*", default=cfg.MODELS["8gb"])
    ap.add_argument("--strategies", nargs="*", default=cfg.STRATEGIES, choices=["baseline", "flat", "rag"])
    ap.add_argument("--num-ctx", nargs="*", type=int, default=cfg.NUM_CTX_VALUES)
    ap.add_argument("--repeats", type=int, default=cfg.REPEATS)
    ap.add_argument("--max-files", type=int, default=cfg.MAX_FILES)
    ap.add_argument("--top-k", type=int, default=cfg.TOP_K)
    ap.add_argument("--embed-model", default=cfg.EMBED_MODEL)
    ap.add_argument("--judge-model", default=cfg.JUDGE_MODEL)
    ap.add_argument("--no-judge", action="store_true", help="não executa o juiz LLM")
    ap.add_argument("--host", default="http://localhost:11434")
    ap.add_argument("--out", default=cfg.OUTPUT_DIR)
    args = ap.parse_args()

    if args.repos:
        repos = args.repos
    else:
        tiers = args.tier or ["pequeno"]
        repos = [u for t in tiers for u in cfg.REPOSITORIES[t]]

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    runs_csv, sections_csv = out / "runs.csv", out / "sections.csv"

    for url in repos:
        print(f"\n=== Repositório: {url}")
        try:
            repo = load_from_github(url)
        except Exception as exc:
            print(f"  falha ao clonar: {exc}")
            continue

        try:
            reference = find_reference_doc(repo.path)
            files = collect_files(repo.path, max_files=args.max_files, exclude_docs=True)
            print(f"  {len(files)} arquivos na entrada | doc de referência: {'sim' if reference.strip() else 'não'}")

            for model in args.models:
                for num_ctx in args.num_ctx:
                    for strategy in args.strategies:
                        for rep in range(1, args.repeats + 1):
                            seed = cfg.BASE_SEED + rep
                            tag = f"{model} | {strategy} | ctx={num_ctx} | r{rep}"
                            print(f"  -> {tag}")
                            row = {
                                "repo": repo.name, "porte": tier_of(url), "modelo": model,
                                "estrategia": strategy, "num_ctx": num_ctx, "repeticao": rep,
                                "seed": seed, "arquivos_na_entrada": len(files),
                                "vram_estimada_gb": estimate_vram_gb(model, num_ctx),
                            }
                            try:
                                client = OllamaClient(model, host=args.host, num_ctx=num_ctx, seed=seed)
                                with GpuSampler() as gpu:
                                    result = run_pipeline(
                                        repo.path, repo.name, files, client,
                                        strategy=strategy, embed_model=args.embed_model,
                                        top_k=args.top_k,
                                    )
                                if not args.no_judge:
                                    run_judge(result, client, args.judge_model)

                                metrics = evaluate_run(result, repo.path, reference)
                                row.update(metrics)
                                row.update({
                                    "categoria": result.category,
                                    "energia_wh": round(gpu.energy_wh, 4) if gpu.available else "",
                                    "potencia_media_w": round(gpu.avg_power_w, 1) if gpu.available else "",
                                    "vram_pico_mb": gpu.peak_vram_mb if gpu.available else "",
                                })

                                doc_dir = out / "docs" / slug(repo.name) / slug(model) / strategy / f"r{rep}"
                                doc_dir.mkdir(parents=True, exist_ok=True)
                                for s in result.sections:
                                    (doc_dir / s.section.filename).write_text(s.content, encoding="utf-8")
                                    append_row(sections_csv, SECTION_FIELDS, {
                                        "repo": repo.name, "modelo": model, "estrategia": strategy,
                                        "num_ctx": num_ctx, "repeticao": rep, "secao": s.section.key,
                                        "tempo_s": round(s.elapsed_seconds, 2),
                                        "tokens_prompt": s.prompt_tokens, "tokens_saida": s.output_tokens,
                                        "chamadas_truncadas": s.truncated_calls,
                                        "arquivos_recuperados": len(s.retrieved_paths),
                                        "mermaid_reparado": int(s.mermaid_repaired),
                                    })
                            except Exception as exc:
                                row["erro"] = f"{type(exc).__name__}: {exc}"
                                traceback.print_exc()
                            append_row(runs_csv, RUN_FIELDS, row)
        finally:
            shutil.rmtree(repo.path.parent, ignore_errors=True)

    print(f"\nConcluído. Resultados em: {out.resolve()}")


if __name__ == "__main__":
    main()
