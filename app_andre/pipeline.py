import os
import time
import shutil
import logging
import requests
from git import Repo
from config import *

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
    for root, _, files in os.walk(path):
        if any(folder in root.split(os.sep) for folder in IGNORABLE_FOLDERS):
            continue
        for file in files:
            if file.endswith(VALID_FILE_EXTENSIONS):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, path)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context.append(f"--- {rel_path} ---\n{content}\n")
                except Exception as e:
                    raise RuntimeError(f"Failed to read file {f}: {e}")
    return "\n".join(context)

def post_process(content):
    return content

def generate(repository_path):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    logging.info("SCANNING REPOSITORY FILES...")
    repository_folder = download_github_repository(repository_path)
    prompt_input = scan_repository(repository_folder)

    logging.info(f"STARTING DOCUMENTATION GENERATION IN DIRECTORY: '{OUTPUT_DIR}'\n")
    for output_file, model_name in FILE_TO_MODEL:
        file_output_path = os.path.join(OUTPUT_DIR, output_file)
        logging.info(f"GENERATING [{output_file}] WITH MODEL [{model_name}]...")
        start_time = time.perf_counter()
        payload = {"model": model_name, "prompt": prompt_input, "stream": False}
        
        try:
            response = requests.post(OLLAMA_API_URL, json=payload, timeout=600)
            
            if response.status_code == 200:
                generated_content = response.json().get("response", "")
                with open(file_output_path, "w", encoding="utf-8") as f:
                    f.write(generated_content)
                    logging.info(f"{file_output_path} WRITTEN")
                
                elapsed_time = time.perf_counter() - start_time
                logging.info(f"SUCCESS: SAVED TO [{file_output_path}] ({elapsed_time:.2f} S)\n")
            else:
                logging.info(f"ERROR CALLING MODEL [{model_name}]: STATUS {response.status_code} - {response.text}\n")
                
        except requests.exceptions.Timeout:
            logging.error(f"TIMEOUT WHILE GENERATING WITH MODEL [{model_name}]\n")
        except Exception as e:
            logging.error(f"FAILED TO CONNECT TO MODEL [{model_name}]: {e}\n")

    logging.info(f"GENERATION COMPLETED.")
    shutil.rmtree(repository_folder)