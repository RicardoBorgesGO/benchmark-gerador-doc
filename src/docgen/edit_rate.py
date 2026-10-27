"""Taxa de edição entre o guia gerado e a versão revisada (1 - similaridade de palavras)."""

from __future__ import annotations

import difflib
import re


def _words(text: str) -> list[str]:
    return re.findall(r"\S+", text)


def compute_edit_rate(generated: str, revised: str) -> dict:
    a, b = _words(generated), _words(revised)
    if not a and not b:
        return {"edit_rate": 0.0, "palavras_geradas": 0, "palavras_revisadas": 0,
                "palavras_adicionadas": 0, "palavras_removidas": 0}

    matcher = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
    added = removed = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag in ("replace", "delete"):
            removed += i2 - i1
        if tag in ("replace", "insert"):
            added += j2 - j1

    return {
        "edit_rate": round(1.0 - matcher.ratio(), 4),
        "palavras_geradas": len(a),
        "palavras_revisadas": len(b),
        "palavras_adicionadas": added,
        "palavras_removidas": removed,
    }


if __name__ == "__main__":
    import sys
    from pathlib import Path

    if len(sys.argv) != 3:
        raise SystemExit("uso: python -m docgen.edit_rate guia_gerado.md guia_revisado.md")
    gen = Path(sys.argv[1]).read_text(encoding="utf-8")
    rev = Path(sys.argv[2]).read_text(encoding="utf-8")
    for k, v in compute_edit_rate(gen, rev).items():
        print(f"{k}: {v}")
