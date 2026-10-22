import os
import nltk
import stat
import shutil
import logging
import pandas as pd
from git import Repo
from config import *

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def download_github_repository(github_url):
    destination_folder = github_url.split("/")[-1].replace(".git", "")
    if os.path.exists(destination_folder):
        shutil.rmtree(destination_folder, onexc=remove_readonly)
        
    os.makedirs(destination_folder, exist_ok=True)
    try:
        logging.info(f"Cloning {github_url} to {destination_folder}...")
        Repo.clone_from(github_url, destination_folder)
    except Exception as e:
        logging.error(f"Failed to clone repository {github_url}: {e}")
    return destination_folder


def scan_repository(path):
    context = []
    total_files = 0
    selected_files = 0

    for root, _, files in os.walk(path):
        if any(folder in IGNORABLE_FOLDERS or folder.startswith('.') for folder in root.split(os.sep)):
            continue
        for file in files:
            total_files += 1
            if file.endswith(VALID_FILE_EXTENSIONS):
                selected_files += 1
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, path)
                try:
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        context.append(f"--- {rel_path} ---\n{content}\n")
                except Exception as e:
                    logging.warning(f"Failed to read file {full_path}: {e}")

    stats = {
        "total_files": total_files,
        "selected_files": selected_files,
    }

    return "\n".join(context), stats

def append_csv_metric(model_name, repository, num_tokens, selected_files, vram_required_gb):
    new_row = pd.DataFrame([{
        "model": model_name,
        "repository": repository,
        "num_tokens": num_tokens,
        "selected_files": selected_files,
        "vram_required_gb": vram_required_gb,
    }])
    
    if os.path.exists(TOKENIZATION_REPORT_FILE):
        df = pd.read_csv(TOKENIZATION_REPORT_FILE)
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df = new_row
        
    df.to_csv(TOKENIZATION_REPORT_FILE, index=False, encoding="utf-8")

def estimate_context_vram_gb(num_tokens, num_layers=32, hidden_dim=4096, bytes_per_element=2):
    # KV Cache/token: 2 (Key and Value) * layers * hidden_dim * bytes
    bytes_per_token = 2 * num_layers * hidden_dim * bytes_per_element
    total_bytes = num_tokens * bytes_per_token
    return total_bytes / (1024 ** 3)

if not os.path.exists(TOKENIZATION_REPORT_FILE):
    df = pd.DataFrame({}, columns=["model", "repository", "num_tokens", "selected_files", "vram_required_gb"])
    df.to_csv(TOKENIZATION_REPORT_FILE, index=False)

for model in OLLAMA_MODELS:
    for repo_url in REPOSITORIES:
        repo_folder = download_github_repository(repo_url)
        if not os.path.exists(repo_folder):
            logging.error(f"Skipping repository {repo_url} due to cloning failure.")
            continue
        repository_code, stats = scan_repository(repo_folder)
        user_content = (
            "Abaixo está o código-fonte completo do repositório delimitado pelas tags <repository_code>.\n"
            "Analise o código e gere OBRIGATORIAMENTE o documento específico solicitado no seu SYSTEM PROMPT.\n\n"
            f"<repository_code>\n{repository_code}\n</repository_code>\n\n"
            "REGRAS DE EXECUÇÃO:\n"
            "1. Idioma: EXCLUSIVAMENTE Português (Brasil).\n"
            "2. Fonte da Verdade: Use APENAS o código dentro de <repository_code>.\n"
            "3. ADAPTAÇÃO DE DOMÍNIO: Classifique internamente o software em sua categoria (API, Game, Lib, CLI, UI/App ou Plugin) "
            "e use APENAS a terminologia e tipos de exemplos próprios dessa categoria no documento.\n"
            "4. FOCO EXCLUSIVO DO DOCUMENTO: Não gere uma visão geral genérica. Execute ESTRITAMENTE a estrutura, "
            "o propósito e o nível de detalhe definidos no seu SYSTEM PROMPT.\n"
            "5. Formato: Retorne APENAS Markdown puro. Para diagramas Mermaid, use sintaxe `flowchart TB/LR` pura.\n"
            "6. Início Imediato: Comece sua resposta diretamente com o caractere `#` do título principal."
        )

        tokens = nltk.word_tokenize(user_content)
        vram_required_gb = (estimate_context_vram_gb(len(tokens)) + MODEL_TO_VRAM_USAGE_GB[model]) / 10**9
        append_csv_metric(model, repo_url, len(tokens), stats["selected_files"], round(vram_required_gb, 2))
        shutil.rmtree(repo_folder, onexc=remove_readonly)