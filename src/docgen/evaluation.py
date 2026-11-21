"""Métricas: BERTScore e METEOR contra o README, juiz por rubrica e verificador de referências."""

from __future__ import annotations

import json
import re

from . import prompts
from .verifier import verify_document

SCORE_KEYS = ("repository_coherence", "framework_adherence", "onboarding_usefulness", "content_clarity")
_SCORE_ALIASES = {
    "coerencia_repositorio": "repository_coherence",
    "repository_coherence": "repository_coherence",
    "adesao_frameworks": "framework_adherence",
    "framework_adherence": "framework_adherence",
    "utilidade_onboarding": "onboarding_usefulness",
    "onboarding_usefulness": "onboarding_usefulness",
    "clareza_conteudo": "content_clarity",
    "content_clarity": "content_clarity",
}


def lightweight_overlap_score(candidate: str, reference: str) -> float:
    def tokenize(text: str) -> set[str]:
        return set(re.findall(r"[a-zA-ZÀ-ÿ0-9]+", text.lower()))

    cand_tokens = tokenize(candidate)
    ref_tokens = tokenize(reference)
    if not cand_tokens or not ref_tokens:
        return 0.0
    return len(cand_tokens & ref_tokens) / len(cand_tokens | ref_tokens)


def full_metrics_available() -> bool:
    try:
        import bert_score  # noqa: F401
        import nltk  # noqa: F401

        return True
    except ImportError:
        return False


def evaluate_documentation(generated_text: str, reference_text: str) -> dict:
    if not full_metrics_available():
        return {
            "method": "lexical_overlap",
            "overlap_score": round(lightweight_overlap_score(generated_text, reference_text), 4),
        }

    import nltk
    from bert_score import score
    from nltk.translate.meteor_score import meteor_score

    nltk.download("wordnet", quiet=True)
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)

    meteor_val = meteor_score([nltk.word_tokenize(reference_text)], nltk.word_tokenize(generated_text))
    precision, recall, f1 = score(
        cands=[generated_text],
        refs=[reference_text],
        model_type="bert-base-multilingual-cased",
        verbose=False,
    )
    return {
        "method": "bertscore_meteor",
        "meteor": round(float(meteor_val), 4),
        "bert_precision": round(float(precision.mean().item()), 4),
        "bert_recall": round(float(recall.mean().item()), 4),
        "bert_f1": round(float(f1.mean().item()), 4),
    }


def combined_documents(result) -> str:
    return "\n\n".join(d.content for d in result.documents)


def parse_llm_json(raw: str | None) -> dict | None:
    if not raw:
        return None
    text = raw.replace("```json", "").replace("```", "").replace("\u00a0", " ").strip()

    candidates = [text]
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        candidates.append(text[start:end + 1])

    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data

    try:
        from json_repair import repair_json

        data = repair_json(text, return_objects=True)
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def normalize_judge(parsed: dict | None) -> dict | None:
    if not isinstance(parsed, dict):
        return None
    raw_scores = parsed.get("scores") if isinstance(parsed.get("scores"), dict) else {}
    scores = {}
    for key, value in raw_scores.items():
        canonical = _SCORE_ALIASES.get(key)
        try:
            number = float(value)
        except (TypeError, ValueError):
            continue
        if canonical and 1 <= number <= 5:
            scores[canonical] = number
    if not scores:
        return None
    suggestions = parsed.get("suggestions") if isinstance(parsed.get("suggestions"), list) else []
    return {"scores": scores, "suggestions": [str(s) for s in suggestions if str(s).strip()]}


def evaluate_markdown(client, language: str, item, readme_text: str, judge_model: str | None = None) -> dict | None:
    message = prompts.judge_user_message(
        language,
        readme_text,
        prompts.system_prompt(item.document.filename, language),
        item.document.filename,
        item.content,
    )
    item.judge_raw = client.chat(prompts.judge_system_prompt(language), message, model=judge_model)
    item.judge = parse_llm_json(item.judge_raw)
    return item.judge


def judge_summary(result) -> dict:
    judged = [d for d in result.documents if d.judge_raw is not None]
    if not judged:
        return {}
    normalized = [n for n in (normalize_judge(d.judge) for d in judged) if n]
    summary: dict = {}
    for key in SCORE_KEYS:
        values = [n["scores"][key] for n in normalized if key in n["scores"]]
        summary[f"judge_{key}"] = round(sum(values) / len(values), 3) if values else ""
    all_scores = [v for n in normalized for v in n["scores"].values()]
    summary["judge_mean"] = round(sum(all_scores) / len(all_scores), 3) if all_scores else ""
    summary["judge_suggestions_total"] = sum(len(n["suggestions"]) for n in normalized)
    summary["judge_parse_failures"] = len(judged) - len(normalized)
    return summary


def evaluate_run(result, repo_path, reference_text: str = "", reference_kind: str = "none") -> dict:
    row: dict = {
        "language": result.language,
        "reference": reference_kind,
        "generation_time_seconds": round(result.total_elapsed_seconds, 2),
        "prompt_tokens": result.usage.prompt_tokens,
        "output_tokens": result.usage.output_tokens,
        "calls": result.usage.calls,
        "truncated_calls": result.usage.truncated_calls,
        "mermaid_repaired": sum(1 for d in result.documents if d.mermaid_repaired),
    }

    combined = combined_documents(result)
    if reference_text.strip():
        row.update(evaluate_documentation(combined, reference_text))

    row.update(judge_summary(result))

    report = verify_document(combined, repo_path)
    row["references_checked"] = report.checked
    row["references_missing"] = report.n_missing
    row["references_support_rate"] = round(report.support_rate, 4)
    return row
