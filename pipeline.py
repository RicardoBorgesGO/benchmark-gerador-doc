import os
import time
import requests

# CONSTANTS
REPO_PATH = r"F:\UFG\M14 - Trabalho de Conclusão de Curso\snake"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OUTPUT_DIR = "autodoc"

# MAPPING: (OUTPUT FILE NAME -> OLLAMA MODEL NAME)
DIATAXIS_STEPS = [
    # ("01_tutorials.md", "doc-diataxis-tutorial"),
    # ("02_how_to_guides.md", "doc-diataxis-howto"),
    # ("03_reference.md", "doc-diataxis-reference"),
    ("04_explanation.md", "doc-diataxis-explanation")
]

def read_repository(path):
    context = []
    valid_extensions = (
        # Main Codebase
        '.py', '.js', '.jsx', '.ts', '.tsx', '.go', '.java', '.cs', '.cpp', '.c', '.h', '.hpp', '.rs', '.php', '.rb',
        
        # Web
        '.html', '.css', '.scss', '.vue', '.svelte',
        
        # Dependencies and config files
        '.json', '.toml', '.yaml', '.yml', '.ini', '.xml', '.gradle', '.properties',
        
        # Automation and Databases
        '.sh', '.ps1', '.bat', '.cmd', '.sql', '.prisma',
    )
    
    for root, dirs, files in os.walk(path):
        if any(banned in root for banned in ['node_modules', '.git', '__pycache__', 'env', 'venv', 'dist', 'build']):
            continue
        for file in files:
            if file.endswith(valid_extensions):
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, path)
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        context.append(f"--- ARQUIVO: {rel_path} ---\n{content}\n")
                except Exception:
                    pass
    return "\n".join(context)

# INITIALIZATION
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("SCANNING REPOSITORY FILES...")
full_code = read_repository(REPO_PATH)
prompt_input = f"Analyze the source code below and generate the corresponding documentation:\n\n{full_code}"
prompt_input = f"Analise o código fonte a seguir e gere a documentação correspondente considerando todos os arquivos:\n\n{full_code}"

print(f"STARTING DOCUMENTATION GENERATION IN DIRECTORY: '{OUTPUT_DIR}'\n")

# EXECUTION LOOP
for output_file, model_name in DIATAXIS_STEPS:
    final_path = os.path.join(OUTPUT_DIR, output_file)
    print(f"PROCESSING [{output_file}] WITH MODEL [{model_name}]...")
    
    start_time = time.perf_counter()
    
    payload = {
        "model": model_name,
        "prompt": prompt_input,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_API_URL, json=payload, timeout=600)
        
        if response.status_code == 200:
            generated_content = response.json().get("response", "")
            
            with open(final_path, "w", encoding="utf-8") as f:
                f.write(generated_content)
            
            elapsed_time = time.perf_counter() - start_time
            print(f"SUCCESS: SAVED TO [{final_path}] ({elapsed_time:.2f} S)\n")
        else:
            print(f"ERROR CALLING MODEL [{model_name}]: STATUS {response.status_code} - {response.text}\n")
            
    except requests.exceptions.Timeout:
        print(f"TIMEOUT EXCEEDED WHILE PROCESSING MODEL [{model_name}]\n")
    except Exception as e:
        print(f"FAILED TO CONNECT TO MODEL [{model_name}]: {e}\n")

print(f"PROCESS COMPLETED. ALL 4 MARKDOWN FILES ARE AVAILABLE IN DIRECTORY: '{OUTPUT_DIR}'")