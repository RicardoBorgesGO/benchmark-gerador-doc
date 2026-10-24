import os
import stat
import shutil
import logging
import pandas as pd
from git import Repo
from config import *
from transformers import AutoTokenizer

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

def calculate_required_vram(model_name, input_tokens, gpu_overhead_gb=1.0):   
    cfg = MODEL_ARCHITECTURES[model_name]
    
    # 1. Model weights memory (in GB)
    # Formula: (Parameters in billions * bits) / 8
    weight_vram = (cfg["parameters_b"] * cfg["quant_bits"]) / 8.0
    
    # 2. KV Cache memory (in GB)
    # KV Cache size = 2 * num_layers * hidden_size * seq_len * bytes_per_element
    # Assuming FP16 (2 bytes per element). Factor 2 accounts for Key and Value.
    kv_elements = 2 * cfg["num_layers"] * cfg["embedding_length"] * input_tokens
    kv_cache_vram = (kv_elements * 2) / (1024 ** 3)  # Convert bytes to GB
    total_vram = weight_vram + kv_cache_vram + gpu_overhead_gb
    
    return round(total_vram, 2)

if not os.path.exists(TOKENIZATION_REPORT_FILE):
    df = pd.DataFrame({}, columns=["model", "repository", "num_tokens", "selected_files", "vram_required_gb"])
    df.to_csv(TOKENIZATION_REPORT_FILE, index=False)

for repo_url in REPOSITORIES:
    repo_folder = download_github_repository(repo_url)
    for model in OLLAMA_MODELS:
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

        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")
        prompt_tokens = tokenizer.encode(user_content)
        vram_required_gb = calculate_required_vram(model, len(prompt_tokens))
        append_csv_metric(model, repo_url, len(prompt_tokens), stats["selected_files"], round(vram_required_gb, 2))
    shutil.rmtree(repo_folder, onexc=remove_readonly)