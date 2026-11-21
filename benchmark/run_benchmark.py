"""Executa repositórios x modelos x idiomas x top-k x repetições, grava os documentos em autodoc/ e as métricas em CSV."""

from __future__ import annotations

import argparse
import csv
import json
import logging
import shutil
import traceback
from datetime import datetime
from pathlib import Path

from docgen.analyzer import find_readme
from docgen.evaluation import evaluate_markdown, evaluate_run, normalize_judge
from docgen.hardware import GpuSampler, estimate_vram_gb
from docgen.ollama_client import OllamaClient
from docgen.pipeline import generate_documents
from docgen.references import reference_for
from docgen.repository import download_github_repository

from . import config as cfg

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

GENERATION_FIELDS = [
    "repository", "document", "model", "prompt_tokens", "output_tokens", "generation_time_seconds",
    "language", "top_k", "num_ctx", "run", "truncated_calls", "mermaid_repaired",
    "judge_repository_coherence", "judge_framework_adherence", "judge_onboarding_usefulness",
    "judge_content_clarity", "judge_suggestions",
]
EVALUATION_FIELDS = [
    "model", "repository", "meteor", "bert_precision", "bert_recall", "bert_f1",
    "repository_url", "language", "top_k", "num_ctx", "run", "seed", "reference", "overlap_score",
    "generation_time_seconds", "prompt_tokens", "output_tokens", "calls", "truncated_calls",
    "mermaid_repaired", "valid_files", "files_sent",
    "judge_repository_coherence", "judge_framework_adherence", "judge_onboarding_usefulness",
    "judge_content_clarity", "judge_mean", "judge_suggestions_total", "judge_parse_failures",
    "references_checked", "references_missing", "references_support_rate",
    "gpu_energy_wh", "gpu_avg_power_w", "gpu_peak_vram_mb", "estimated_vram_gb", "error",
]
KEY_FIELDS = ("repository", "model", "language", "top_k", "num_ctx", "run")


def append_csv_metric(path: Path, fields: list[str], row: dict) -> None:
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        if new:
            writer.writeheader()
        writer.writerow(row)


def finished_runs(path: Path) -> set[tuple]:
    if not path.exists():
        return set()
    with path.open(encoding="utf-8") as f:
        return {tuple(str(r.get(k, "")) for k in KEY_FIELDS) for r in csv.DictReader(f) if not r.get("error")}


def _judge_columns(item) -> dict:
    normalized = normalize_judge(item.judge)
    scores = normalized["scores"] if normalized else {}
    return {
        "judge_repository_coherence": scores.get("repository_coherence", ""),
        "judge_framework_adherence": scores.get("framework_adherence", ""),
        "judge_onboarding_usefulness": scores.get("onboarding_usefulness", ""),
        "judge_content_clarity": scores.get("content_clarity", ""),
        "judge_suggestions": len(normalized["suggestions"]) if normalized else "",
    }


def save_documents(output_dir: Path, model: str, repo_name: str, result, meta: dict) -> Path:
    folder = output_dir / model.replace(":", "_") / repo_name / result.language
    folder.mkdir(parents=True, exist_ok=True)
    for item in result.documents:
        (folder / item.document.filename).write_text(item.content, encoding="utf-8")

    if any(item.judge_raw is not None for item in result.documents):
        evaluations = {item.document.filename: item.judge for item in result.documents}
        (folder / "llm_eval.json").write_text(json.dumps(evaluations, indent=2, ensure_ascii=False), encoding="utf-8")

    (folder / "run_info.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return folder


def run_pipeline(
    repository_urls: list[str],
    ollama_models: list[str],
    languages: list[str] | None = None,
    top_k_values: list[int] | None = None,
    num_ctx_values: list[int] | None = None,
    repeats: int = cfg.REPEATS,
    seed_base: int | None = None,
    judge_model: str = cfg.JUDGE_MODEL,
    use_judge: bool = True,
    use_mermaid_repair: bool = False,
    translated_dir: str = cfg.TRANSLATED_README_DIR,
    resume: bool = False,
    host: str = cfg.OLLAMA_API_URL,
    output_dir: str = cfg.OUTPUT_DIR,
    csv_dir: str = ".",
) -> None:
    languages = languages or cfg.LANGUAGES
    top_k_values = top_k_values if top_k_values is not None else cfg.TOP_K_VALUES
    num_ctx_values = num_ctx_values or cfg.NUM_CTX_VALUES

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    generation_csv = Path(csv_dir) / cfg.CSV_REPORT_FILE
    evaluation_csv = Path(csv_dir) / cfg.EVALUATION_REPORT_FILE
    done = finished_runs(evaluation_csv) if resume else set()

    for repo_url in repository_urls:
        logging.info(f"PROCESSING REPOSITORY: {repo_url}")
        try:
            repo = download_github_repository(repo_url)
        except Exception as exc:
            logging.error(f"Failed to clone {repo_url}: {exc}")
            continue

        try:
            readme = find_readme(repo.path)
            for model in ollama_models:
                for num_ctx in num_ctx_values:
                    for language in languages:
                        for top_k in top_k_values:
                            for run in range(1, repeats + 1):
                                key = (repo.name, model, language, str(top_k), str(num_ctx), str(run))
                                if key in done:
                                    continue
                                seed = seed_base + run if seed_base is not None else None
                                logging.info(f"{model} | {language} | k={top_k or 'all'} | ctx={num_ctx} | run {run}")
                                row = {
                                    "model": model, "repository": repo.name, "repository_url": repo_url,
                                    "language": language, "top_k": top_k, "num_ctx": num_ctx, "run": run,
                                    "seed": seed or "", "estimated_vram_gb": estimate_vram_gb(model, num_ctx),
                                }
                                try:
                                    client = OllamaClient(model, host=host, num_ctx=num_ctx, seed=seed)
                                    with GpuSampler() as gpu:
                                        result = generate_documents(
                                            repo.path, repo.name, client, language=language,
                                            top_k=top_k or None, use_mermaid_repair=use_mermaid_repair,
                                        )
                                    if use_judge:
                                        for item in result.documents:
                                            evaluate_markdown(client, language, item, readme, judge_model)

                                    reference, kind = reference_for(repo.path, repo.name, language, translated_dir)
                                    row.update(evaluate_run(result, repo.path, reference, kind))
                                    row.update({
                                        "valid_files": result.stats["selected_files"],
                                        "files_sent": len(result.documents[0].files_sent),
                                        "gpu_energy_wh": round(gpu.energy_wh, 4) if gpu.available else "",
                                        "gpu_avg_power_w": round(gpu.avg_power_w, 1) if gpu.available else "",
                                        "gpu_peak_vram_mb": gpu.peak_vram_mb if gpu.available else "",
                                    })

                                    save_documents(out, model, repo.name, result, {
                                        "repository": repo_url, "model": model, "language": language,
                                        "top_k": top_k, "num_ctx": num_ctx, "run": run, "seed": seed,
                                        "generated_at": datetime.now().isoformat(timespec="seconds"),
                                    })
                                    for item in result.documents:
                                        append_csv_metric(generation_csv, GENERATION_FIELDS, {
                                            "repository": repo_url, "document": item.document.filename,
                                            "model": model, "prompt_tokens": item.prompt_tokens,
                                            "output_tokens": item.output_tokens,
                                            "generation_time_seconds": f"{item.elapsed_seconds:.2f}",
                                            "language": language, "top_k": top_k, "num_ctx": num_ctx, "run": run,
                                            "truncated_calls": item.truncated_calls,
                                            "mermaid_repaired": int(item.mermaid_repaired),
                                            **_judge_columns(item),
                                        })
                                except Exception as exc:
                                    row["error"] = f"{type(exc).__name__}: {exc}"
                                    traceback.print_exc()
                                append_csv_metric(evaluation_csv, EVALUATION_FIELDS, row)
        finally:
            shutil.rmtree(repo.path.parent, ignore_errors=True)

    logging.info(f"Done. Documents in {out.resolve()}; metrics in {generation_csv} and {evaluation_csv}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repos", nargs="*", default=cfg.REPOSITORIES, help="URLs do GitHub")
    ap.add_argument("--models", nargs="*", default=cfg.OLLAMA_MODELS)
    ap.add_argument("--languages", nargs="*", default=cfg.LANGUAGES, choices=["pt", "en"])
    ap.add_argument("--top-k", nargs="*", type=int, default=cfg.TOP_K_VALUES, help="0 = todos os arquivos")
    ap.add_argument("--num-ctx", nargs="*", type=int, default=cfg.NUM_CTX_VALUES)
    ap.add_argument("--repeats", type=int, default=cfg.REPEATS)
    ap.add_argument("--seed-base", type=int, default=None)
    ap.add_argument("--judge-model", default=cfg.JUDGE_MODEL)
    ap.add_argument("--no-judge", action="store_true")
    ap.add_argument("--mermaid-repair", action="store_true")
    ap.add_argument("--translated-dir", default=cfg.TRANSLATED_README_DIR)
    ap.add_argument("--resume", action="store_true", help="pula execuções já registradas em evaluation_results.csv")
    ap.add_argument("--host", default=cfg.OLLAMA_API_URL)
    ap.add_argument("--out", default=cfg.OUTPUT_DIR)
    ap.add_argument("--csv-dir", default=".")
    args = ap.parse_args()

    run_pipeline(
        args.repos, args.models,
        languages=args.languages, top_k_values=args.top_k, num_ctx_values=args.num_ctx,
        repeats=args.repeats, seed_base=args.seed_base, judge_model=args.judge_model,
        use_judge=not args.no_judge, use_mermaid_repair=args.mermaid_repair,
        translated_dir=args.translated_dir, resume=args.resume, host=args.host,
        output_dir=args.out, csv_dir=args.csv_dir,
    )


if __name__ == "__main__":
    main()
