"""Métricas de avaliação: BERTScore/METEOR (opcionais), sobreposição lexical, juiz e verificador."""

from __future__ import annotations

import re


def lightweight_overlap_score(candidate: str, reference: str) -> float:
    def tokenize(text: str) -> set[str]:
        return set(re.findall(r"[a-zA-ZÀ-ÿ0-9]+", text.lower()))

    cand_tokens = tokenize(candidate)
    ref_tokens = tokenize(reference)
    if not cand_tokens or not ref_tokens:
        return 0.0

    intersection = cand_tokens & ref_tokens
    union = cand_tokens | ref_tokens
    return len(intersection) / len(union)


def full_metrics_available() -> bool:
    try:
        import bert_score  # noqa: F401
        import nltk  # noqa: F401

        return True
    except ImportError:
        return False


def evaluate_with_reference(generated_text: str, reference_text: str) -> dict:
    if not full_metrics_available():
        return {
            "metodo": "fallback_leve (bert-score/nltk não instalados)",
            "overlap_score": round(lightweight_overlap_score(generated_text, reference_text), 4),
        }

    import nltk
    from bert_score import score
    from nltk.translate.meteor_score import meteor_score

    nltk.download("wordnet", quiet=True)
    nltk.download("punkt", quiet=True)
    nltk.download("punkt_tab", quiet=True)

    generated_tokens = nltk.word_tokenize(generated_text)
    reference_tokens = nltk.word_tokenize(reference_text)

    meteor_val = meteor_score([reference_tokens], generated_tokens)

    precision, recall, f1 = score(
        cands=[generated_text],
        refs=[reference_text],
        model_type="bert-base-multilingual-cased",
        verbose=False,
    )

    return {
        "metodo": "bert_score + meteor",
        "meteor": round(float(meteor_val), 4),
        "bert_precision": round(float(precision.mean().item()), 4),
        "bert_recall": round(float(recall.mean().item()), 4),
        "bert_f1": round(float(f1.mean().item()), 4),
    }


_BULLET_RE = re.compile(r"^\s*(?:[\*\-•]|\d+[\.\)])\s+(.+)$")


def count_judge_issues(judge_text: str | None) -> int:
    if not judge_text:
        return 0
    issues = 0
    for line in judge_text.splitlines():
        m = _BULLET_RE.match(line)
        if m and "nenhum problema" not in m.group(1).lower():
            issues += 1
    return issues


def evaluate_run(result, repo_path, reference_text: str = "") -> dict:
    from .verifier import verify_document

    guide = result.assemble_markdown()
    row: dict = {
        "cenario": "com_referencia" if reference_text.strip() else "sem_referencia",
        "tempo_total_s": round(result.total_elapsed_seconds, 2),
        "tokens_prompt": result.usage.prompt_tokens,
        "tokens_saida": result.usage.output_tokens,
        "chamadas": result.usage.calls,
        "chamadas_truncadas": result.usage.truncated_calls,
        "mermaid_reparado": sum(1 for s in result.sections if s.mermaid_repaired),
    }

    if reference_text.strip():
        row.update(evaluate_with_reference(guide, reference_text))

    judged = [s for s in result.sections if s.judge_feedback is not None]
    if judged:
        row["falhas_juiz_total"] = sum(count_judge_issues(s.judge_feedback) for s in judged)

    report = verify_document(guide, repo_path)
    row["refs_verificadas"] = report.checked
    row["refs_inexistentes"] = report.n_missing
    row["taxa_suporte_refs"] = round(report.support_rate, 4)
    return row


def run_judge(result, client, judge_model: str | None = None) -> None:
    from .sections import JUDGE_SYSTEM_PROMPT

    for s in result.sections:
        prompt = f"ALVO DA AUDITORIA: seção '{s.section.title}'\n\n<document>\n{s.content}\n</document>"
        s.judge_feedback = client.chat(JUDGE_SYSTEM_PROMPT, prompt, temperature=0.2, model=judge_model)
