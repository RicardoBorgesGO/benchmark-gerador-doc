"""Resume runs.csv: média e desvio por configuração e comparação pareada entre estratégias."""

from __future__ import annotations

import csv
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

METRICS = [
    "tempo_total_s", "tokens_prompt", "chamadas_truncadas", "bert_f1", "meteor",
    "refs_inexistentes", "taxa_suporte_refs", "falhas_juiz_total", "energia_wh",
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


def main(path: str) -> None:
    rows = [r for r in csv.DictReader(Path(path).open(encoding="utf-8")) if not r.get("erro")]
    if not rows:
        raise SystemExit("Sem execuções válidas no CSV.")

    groups: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        groups[(r["repo"], r["modelo"], r["num_ctx"], r["estrategia"])].append(r)

    print("\n== Média ± desvio por configuração ==")
    header = ["repo", "modelo", "ctx", "estratégia", "n"] + METRICS
    print(" | ".join(header))
    for key, rs in sorted(groups.items()):
        cells = list(key) + [str(len(rs))]
        for m in METRICS:
            cells.append(fmt([v for v in (num(r.get(m)) for r in rs) if v is not None]))
        print(" | ".join(cells))

    pairs = defaultdict(dict)
    for r in rows:
        pairs[(r["repo"], r["modelo"], r["num_ctx"], r["repeticao"])][r["estrategia"]] = r

    try:
        from scipy.stats import wilcoxon
    except ImportError:
        wilcoxon = None

    pair_metrics = ["tempo_total_s", "chamadas_truncadas", "refs_inexistentes", "bert_f1", "meteor", "falhas_juiz_total"]
    for baseline in ("baseline", "flat"):
        print(f"\n== Pareado: rag - {baseline} ==")
        for m in pair_metrics:
            diffs = []
            for pair in pairs.values():
                if baseline in pair and "rag" in pair:
                    a, b = num(pair[baseline].get(m)), num(pair["rag"].get(m))
                    if a is not None and b is not None:
                        diffs.append(b - a)
            if not diffs:
                continue
            line = f"{m}: diferença média = {st.mean(diffs):+.3f} (n={len(diffs)})"
            if wilcoxon and len(diffs) >= 5 and any(d != 0 for d in diffs):
                line += f", Wilcoxon p = {wilcoxon(diffs).pvalue:.4f}"
            print(line)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "benchmark_results/runs.csv")
