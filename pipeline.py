import os
import time
import requests
from config import *

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

os.makedirs(OUTPUT_DIR, exist_ok=True)
print("SCANNING REPOSITORY FILES...")
prompt_input = scan_repository(REPO_PATH)

print(f"STARTING DOCUMENTATION GENERATION IN DIRECTORY: '{OUTPUT_DIR}'\n")
for output_file, model_name in FILE_TO_MODEL:
    file_output_path = os.path.join(OUTPUT_DIR, output_file)
    print(f"GENERATING [{output_file}] WITH MODEL [{model_name}]...")
    start_time = time.perf_counter()
    payload = {"model": model_name, "prompt": prompt_input, "stream": False}
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=600)
        
        if response.status_code == 200:
            generated_content = response.json().get("response", "")
            
            with open(file_output_path, "w", encoding="utf-8") as f:
                f.write(generated_content)
            
            elapsed_time = time.perf_counter() - start_time
            print(f"SUCCESS: SAVED TO [{file_output_path}] ({elapsed_time:.2f} S)\n")
        else:
            print(f"ERROR CALLING MODEL [{model_name}]: STATUS {response.status_code} - {response.text}\n")
            
    except requests.exceptions.Timeout:
        print(f"TIMEOUT WHILE GENERATING WITH MODEL [{model_name}]\n")
    except Exception as e:
        print(f"FAILED TO CONNECT TO MODEL [{model_name}]: {e}\n")

print(f"GENERATION COMPLETED.")