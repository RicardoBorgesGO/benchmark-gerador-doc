import re
import os
import json
import logging
import requests
from config import *
from glob import glob
from pathlib import Path

import logging
import re
from pathlib import Path
import requests

def evaluate_markdown(file_path: Path):
    content = file_path.read_text(encoding="utf-8")

    user_prompt = (
        f"ALVO DA AUDITORIA: Arquivo '{file_path.name}'\n\n"
        f"<document>\n{content}\n</document>"
    )

    payload = {
        "model": "judge",
        "messages": [{"role": "user", "content": user_prompt}],
        "stream": False,
        "options": {"temperature": 0.2},
    }

    response = requests.post(OLLAMA_API_URL, json=payload, timeout=120)
    response.raise_for_status()

    res_data = response.json()
    raw_output = res_data.get("message", {}).get("content", "").strip()

    suggestions = [
        line.strip()
        for line in raw_output.splitlines()
        if re.match(r"^[\*\-\d\.]+\s+", line.strip())
    ]

    if not suggestions and raw_output:
        suggestions = [raw_output]

    return suggestions

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    evaluations = {}

    for md_file in glob(os.path.join(OUTPUT_DIR, "*.md")):
        logging.info(f"ANALYZING {md_file}...")
        suggestions = evaluate_markdown(Path(md_file))
        issue_count = len(suggestions)

        evaluations[md_file] = {
            "suggestions": suggestions,
            "total_issues": issue_count
        }

    output_path = Path("llm_eval.json")
    output_path.write_text(json.dumps(evaluations, indent=2, ensure_ascii=False), encoding="utf-8")
    logging.info(f"\nASSESMENT COMPLETE. REPORT SAVED AT: {output_path}")