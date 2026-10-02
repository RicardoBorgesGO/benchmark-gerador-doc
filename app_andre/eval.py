import os
import nltk
import logging

from config import *
from glob import glob
from bert_score import score
from nltk.translate.meteor_score import meteor_score

nltk.download("wordnet", quiet=True)
nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

def evaluate_documentation(generated_text, reference_text):
    """Calculates METEOR and BERTScore metrics comparing generated docs against a reference README."""
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


def evaluate_repository_run(generated_doc_dir, readme_path):
    if not os.path.exists(readme_path):
        logging.warning(f"Reference README not found at [{readme_path}]. Skipping evaluation.")
        return {}

    with open(readme_path, "r", encoding="utf-8") as f:
        reference_readme = f.read()

    combined_generated_docs = ""
    for file_path in glob(os.path.join(generated_doc_dir, "*.md")):
        with open(file_path, "r", encoding="utf-8") as f:
            combined_generated_docs += f.read() + "\n\n"

    logging.info("Calculating METEOR and BERTScore metrics...")
    metrics = evaluate_documentation(combined_generated_docs, reference_readme)
    
    logging.info(f"-> METEOR Score: {metrics['meteor']}")
    logging.info(f"-> BERTScore F1: {metrics['bert_f1']}")

    return metrics


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    results = evaluate_repository_run(OUTPUT_DIR, "./README.md")
    logging.info("╔" + "═" * 58 + "╗")
    logging.info("║" + " SEMANTIC EVALUATION RESULTS ".center(58) + "║")
    logging.info("╠" + "═" * 58 + "╣")
    for metric, val in results.items():
        val_str = f"{val:.4f}" if isinstance(val, float) else str(val)
        logging.info(f"║  • {metric:<35} : {val_str:>16}║")
    logging.info("╚" + "═" * 58 + "╝")