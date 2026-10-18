import os
import time
import stat
import shutil
import logging
import csv
import requests
from git import Repo
from config import OLLAMA_API_URL, OUTPUT_DIR, FILE_TO_MODEL, IGNORABLE_FOLDERS, VALID_FILE_EXTENSIONS
from prompts import SYSTEM_PROMPTS

CSV_REPORT_FILE = "generation_metrics.csv"

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

def init_csv_report():
    if not os.path.exists(CSV_REPORT_FILE):
        with open(CSV_REPORT_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["repository", "document", "model", "prompt_tokens", "output_tokens", "generation_time_seconds"])

def append_csv_metric(repo_url, doc_name, model_name, prompt_tokens, eval_tokens, elapsed_time):
    with open(CSV_REPORT_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([repo_url, doc_name, model_name, prompt_tokens, eval_tokens, f"{elapsed_time:.2f}"])

def run_pipeline(repository_urls):
    init_csv_report()
    chat_api_url = OLLAMA_API_URL.replace("/api/generate", "/api/chat")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for repo_url in repository_urls:
        logging.info("=" * 60)
        logging.info(f"PROCESSING REPOSITORY: {repo_url}")
        logging.info("=" * 60)
        
        total_start_time = time.perf_counter()
        
        repo_folder = download_github_repository(repo_url)
        if not os.path.exists(repo_folder):
            logging.error(f"Skipping repository {repo_url} due to cloning failure.")
            continue
            
        repository_code, stats = scan_repository(repo_folder)

        repo_name = repo_url.split("/")[-1].replace(".git", "")
        repo_output_dir = os.path.join(OUTPUT_DIR, repo_name)
        os.makedirs(repo_output_dir, exist_ok=True)

        for output_file, model_name in FILE_TO_MODEL:
            if output_file not in SYSTEM_PROMPTS:
                logging.warning(f"Prompt not found in SYSTEM_PROMPTS for: {output_file}")
                continue

            file_output_path = os.path.join(repo_output_dir, output_file)
            system_prompt = SYSTEM_PROMPTS[output_file]

            logging.info(f"Generating [{output_file}] with model [{model_name}]...")
            start_time = time.perf_counter()
            
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

            payload = {
                "model": "qwen3.6:27b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                "stream": False,
            }
            
            try:
                response = requests.post(chat_api_url, json=payload, timeout=600)
                
                if response.status_code == 200:
                    res_data = response.json()
                    generated_content = res_data.get("message", {}).get("content", "")
                    
                    prompt_tokens = res_data.get("prompt_eval_count", 0)
                    eval_tokens = res_data.get("eval_count", 0)
                    elapsed_time = time.perf_counter() - start_time

                    with open(file_output_path, "w", encoding="utf-8") as f:
                        f.write(generated_content)
                    
                    append_csv_metric(repo_url, output_file, model_name, prompt_tokens, eval_tokens, elapsed_time)
                    
                    logging.info(
                        f"SUCCESS: Saved to [{file_output_path}] ({elapsed_time:.2f}s) | "
                        f"Tokens In: {prompt_tokens} | Tokens Out: {eval_tokens}"
                    )
                else:
                    logging.error(f"API error for model [{model_name}]: Status {response.status_code} - {response.text}")
                    
            except requests.exceptions.Timeout:
                logging.error(f"Timeout while generating document [{output_file}] with model [{model_name}].")
            except Exception as e:
                logging.error(f"Connection or execution failure for model [{model_name}]: {e}")

        shutil.rmtree(repo_folder, onexc=remove_readonly)
        total_elapsed = time.perf_counter() - total_start_time
        logging.info(f"Repository {repo_url} fully processed in {total_elapsed:.2f} seconds.\n")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    repositories_to_test = [
        "https://github.com/tartley/colorama",
        "https://github.com/chubin/cheat.sh",
    ]
    
    run_pipeline(repositories_to_test)