import os
import glob
import nltk
import logging
import pandas as pd

from bert_score import score
from nltk.translate.meteor_score import meteor_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

nltk.download("wordnet", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

def evaluate_documentation(generated_text, reference_text):
    generated_tokens = nltk.word_tokenize(generated_text)
    reference_tokens = nltk.word_tokenize(reference_text)

    # METEOR 
    meteor_val = meteor_score([reference_tokens], generated_tokens)

    # BERTScore
    P, R, F1 = score(
        cands=[generated_text],
        refs=[reference_text],
        model_type="bert-base-multilingual-cased",
        verbose=False
    )

    return {
        "meteor": round(float(meteor_val), 4),
        "bert_precision": round(float(P.mean().item()), 4),
        "bert_recall": round(float(R.mean().item()), 4),
        "bert_f1": round(float(F1.mean().item()), 4),
    }


def evaluate_all_runs(autodoc_dir="autodoc", translated_readme_dir="translated_readme", output_csv="evaluation_results.csv"):
    results = []

    if not os.path.exists(autodoc_dir):
        logging.error(f"Base directory [{autodoc_dir}] not found.")
        return []

    for model_name in os.listdir(autodoc_dir):
        model_path = os.path.join(autodoc_dir, model_name)
        if not os.path.isdir(model_path):
            continue

        for repo_name in os.listdir(model_path):
            repo_path = os.path.join(model_path, repo_name)
            if not os.path.isdir(repo_path):
                continue

            logging.info(f"Processing - Model: {model_name} | Repository: {repo_name}")

            # Concatenates all generated markdown files for this set
            combined_generated_docs = ""
            md_files = glob.glob(os.path.join(repo_path, "*.md"))
            
            if not md_files:
                logging.warning(f"No markdown files found in [{repo_path}]. Skipping.")
                continue

            for file_path in md_files:
                with open(file_path, "r", encoding="utf-8") as f:
                    combined_generated_docs += f.read() + "\n\n"

            # Defines the path of the corresponding ground truth README
            readme_path = os.path.join("..", translated_readme_dir, f"{repo_name}.md")
            if not os.path.exists(readme_path):
                logging.warning(f"Ground truth not found at [{readme_path}]. Skipping.")
                continue

            with open(readme_path, "r", encoding="utf-8") as f:
                reference_readme = f.read()

            logging.info("Calculating METEOR and BERTScore...")
            metrics = evaluate_documentation(combined_generated_docs, reference_readme)
            
            logging.info(f"-> METEOR Score: {metrics['meteor']}")
            logging.info(f"-> BERTScore F1: {metrics['bert_f1']}")

            run_result = {
                "model": model_name,
                "repository": repo_name,
                **metrics
            }
            results.append(run_result)

    if results:
        df = pd.DataFrame(results)
        df.to_csv(output_csv, index=False, encoding="utf-8")
        logging.info(f"Results successfully saved to [{output_csv}]")
    else:
        logging.warning("No results generated to save to CSV.")

    return results

results = evaluate_all_runs()