import os
import time
import glob
import stat
import shutil
import logging
import requests
from git import Repo
from config import *

def remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def download_github_repository(github_url):
    destination_folder = github_url.split("/")[-1]
    os.makedirs(destination_folder, exist_ok=True)
    try:
        logging.info(f"Cloning {github_url} to {destination_folder}...")
        Repo.clone_from(github_url, destination_folder)
    except Exception as e:
        logging.info(f"Failed to clone repository: {e}")
    return destination_folder

def scan_repository(path):
    context = []
    total_files = 0
    selected_files = 0

    for root, _, files in os.walk(path):
        # If a folder is in ignorables list or starts with "."
        if any(folder in IGNORABLE_FOLDERS or (folder.startswith('.')) for folder in root.split(os.sep)):
            continue
        for file in files:
            total_files += 1
            if file.endswith(VALID_FILE_EXTENSIONS):
                selected_files += 1
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, path)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context.append(f"--- {rel_path} ---\n{content}\n")
                except Exception as e:
                    raise RuntimeError(f"Failed to read file {f}: {e}")

    stats = {
        "total_files": total_files,
        "selected_files": selected_files,
    }

    return "\n".join(context), stats

def generate(repository_path):
    total_start_time = time.perf_counter()
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # for f in glob.glob(f"{OUTPUT_DIR}/*.md"): os.remove(f)
    logging.info("SCANNING REPOSITORY FILES...")
    repository_folder = download_github_repository(repository_path)
    repository_code, stats = scan_repository(repository_folder)

    total_prompt_tokens = 0
    total_generated_tokens = 0

    chat_api_url = OLLAMA_API_URL.replace("/api/generate", "/api/chat")

    logging.info(f"STARTING DOCUMENTATION GENERATION IN DIRECTORY: '{OUTPUT_DIR}'\n")
    for output_file, model_name in FILE_TO_MODEL:
        file_output_path = os.path.join(OUTPUT_DIR, output_file)
        logging.info(f"GENERATING [{output_file}] WITH MODEL [{model_name}]...")
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
            "model": model_name,
            "messages": [
                {
                    "role": "user",
                    "content": user_content
                }
            ],
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_ctx": 16384  
            }
        }
        
        try:
            response = requests.post(chat_api_url, json=payload, timeout=600)
            
            if response.status_code == 200:
                res_data = response.json()
                
                generated_content = res_data.get("message", {}).get("content", "")
                
                prompt_tokens = res_data.get("prompt_eval_count", 0)
                eval_tokens = res_data.get("eval_count", 0)
                
                total_prompt_tokens += prompt_tokens
                total_generated_tokens += eval_tokens

                with open(file_output_path, "w", encoding="utf-8") as f:
                    f.write(generated_content)
                    logging.info(f"{file_output_path} WRITTEN")
                
                elapsed_time = time.perf_counter() - start_time
                logging.info(
                    f"SUCCESS: SAVED TO [{file_output_path}] ({elapsed_time:.2f} seconds) | "
                    f"Prompt Tokens: {prompt_tokens} | Output Tokens: {eval_tokens}\n"
                )
            else:
                logging.info(f"ERROR CALLING MODEL [{model_name}]: STATUS {response.status_code} - {response.text}\n")
                
        except requests.exceptions.Timeout:
            logging.error(f"TIMEOUT WHILE GENERATING WITH MODEL [{model_name}]\n")
        except Exception as e:
            logging.error(f"FAILED TO CONNECT TO MODEL [{model_name}]: {e}\n")

    logging.info(f"GENERATION COMPLETED.")
    shutil.rmtree(repository_folder, onexc=remove_readonly)
    
    total_elapsed_time = time.perf_counter() - total_start_time
    
    logging.info("=" * 45)
    logging.info("GENERATION STATISTICS")
    logging.info("=" * 45)
    logging.info(f"Total repository files:       {stats['total_files']}")
    logging.info(f"Files selected for prompt:   {stats['selected_files']}")
    logging.info(f"Total prompt tokens read:    {total_prompt_tokens:,}")
    logging.info(f"Total response tokens generated: {total_generated_tokens:,}")
    logging.info(f"Total execution time:        {total_elapsed_time:.2f} seconds")
    logging.info("=" * 45)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    generate("https://github.com/tartley/colorama")