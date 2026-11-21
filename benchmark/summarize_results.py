"""Resume evaluation_results.csv: média e desvio por configuração e comparação pareada entre top-k e todos os arquivos."""

from __future__ import annotations

import csv
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

METRICS = [
    "generation_time_seconds", "prompt_tokens", "truncated_calls", "bert_f1", "meteor",
    "judge_mean", "judge_suggestions_total", "references_missing", "references_support_rate", "gpu_energy_wh",
]
PAIRED_METRICS = [
    "generation_time_seconds", "prompt_tokens", "truncated_calls", "bert_f1", "meteor",
    "judge_mean", "judge_suggestions_total", "references_missing",
]


def num(value: str):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt(values: list[float]) -> str:
    if not values:
        return "-"
    if len(values) == 1:
        return f"{values[0]:.2f}"
    return f"{st.mean(values):.2f}±{st.stdev(values):.2f}"


def label(row: dict) -> str:
    k = int(row["top_k"] or 0)
    return f"{row['language']}/" + (f"k{k}" if k else "all")


def main(path: str) -> None:
    rows = [r for r in csv.DictReader(Path(path).open(encoding="utf-8")) if not r.get("error")]
    if not rows:
        raise SystemExit("Sem execuções válidas no CSV.")

    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        groups[(r["repository"], r["model"], r["num_ctx"], label(r))].append(r)

    print("\n== Média ± desvio por configuração ==")
    print(" | ".join(["repository", "model", "num_ctx", "language/files", "n"] + METRICS))
    for key, rs in sorted(groups.items()):
        cells = list(key) + [str(len(rs))]
        for m in METRICS:
            cells.append(fmt([v for v in (num(r.get(m)) for r in rs) if v is not None]))
        print(" | ".join(cells))

    pairs: dict[tuple, dict] = defaultdict(dict)
    for r in rows:
        mode = "top_k" if int(r["top_k"] or 0) else "all"
        pairs[(r["repository"], r["model"], r["num_ctx"], r["language"], r["run"])][mode] = r

    try:
        from scipy.stats import wilcoxon
    except ImportError:
        wilcoxon = None

    print("\n== Pareado: top-k - todos os arquivos ==")
    for m in PAIRED_METRICS:
        diffs = []
        for pair in pairs.values():
            if "all" in pair and "top_k" in pair:
                a, b = num(pair["all"].get(m)), num(pair["top_k"].get(m))
                if a is not None and b is not None:
                    diffs.append(b - a)
        if not diffs:
            continue
        line = f"{m}: diferença média = {st.mean(diffs):+.3f} (n={len(diffs)})"
        if wilcoxon and len(diffs) >= 5 and any(d != 0 for d in diffs):
            line += f", Wilcoxon p = {wilcoxon(diffs).pvalue:.4f}"
        print(line)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "evaluation_results.csv")
