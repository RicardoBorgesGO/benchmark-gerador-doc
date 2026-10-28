import os
import json
import logging
import requests
from config import *
from prompts import *
from glob import glob
from pathlib import Path
from json_repair import repair_json

def parse_llm_json(raw_output):
    try:
        clean_output = raw_output.replace("```json", "").replace("```", "").strip()
        clean_output = clean_output.replace('\u00a0', ' ')
        clean_output = clean_output.replace(r"\'", "'")

        return dict(json.loads(clean_output))
    except Exception as e:
        try:
            repaired = repair_json(clean_output, return_objects=True)
            if isinstance(repaired, dict):
                return repaired
            return dict(repaired)
        except Exception as e:
            print(f"Failed to repair JSON: {e}")

def evaluate_markdown(file_path, readme_content):
    try:
        content = file_path.read_text(encoding="utf-8")

        user_prompt = (
            f"<readme>'{readme_content}'</readme>'\n\n"
            f"<doc_instructions>{SYSTEM_PROMPTS[file_path.name]}<doc_instructions>"
            f"<target_file>'{file_path.name}</target_file>'\n\n"
            f"<document>\n{content}\n</document>"
        )

        payload = {
            "model": JUDGE_MODEL,
            "messages": [{"role": "system", "content": EVAL_PROMPTS["judge_score"]},
                        {"role": "user", "content": user_prompt}],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9,
                "num_ctx": 16384  
            }
        }

        response = requests.post(f"{OLLAMA_API_URL}/api/chat", json=payload, timeout=120)
        response.raise_for_status()
        res_data = response.json()
        raw_output = res_data.get("message", {})["content"].strip()

        return parse_llm_json(raw_output)
    except:
        breakpoint()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    evaluations = {}
    for model_folder in os.listdir("autodoc"):
        for repository in os.listdir(os.path.join("autodoc", model_folder)):
            if os.path.exists(os.path.join("autodoc", model_folder, repository, "llm_eval.json")):
                continue
            md_files = glob(os.path.join("autodoc", model_folder, repository, "*.md"))
            readme_content = Path(md_files[-1]).read_text(encoding="utf-8")
            for md_file in md_files[:-1]:
                logging.info(f"ANALYZING {md_file}...")
                suggestions = evaluate_markdown(Path(md_file), readme_content)
                evaluations[Path(md_file).name] = suggestions

            output_path = Path(os.path.join("autodoc", model_folder, repository, "llm_eval.json"))
            output_path.write_text(json.dumps(evaluations, indent=2, ensure_ascii=False), encoding="utf-8")
            logging.info(f"\nASSESMENT COMPLETE. REPORT SAVED AT: {output_path}")