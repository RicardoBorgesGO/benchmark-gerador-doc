REPOSITORIES = {
    "pequeno": [
        "https://github.com/epidemian/snake",
        "https://github.com/marcft/tic-tac-toe",
        "https://github.com/scotch-io/node-todo",
    ],
    "medio": [
        "https://github.com/tartley/colorama",
        "https://github.com/chubin/cheat.sh",
        "https://github.com/psf/requests",
    ],
    "grande": [
        "https://github.com/fastapi/fastapi",
        "https://github.com/gorhill/uBlock",
    ],
}

MODELS = {
    "8gb": ["qwen2.5-coder:7b", "deepseek-coder:6.7b"],
    "24gb": ["qwen2.5-coder:14b"],
}

STRATEGIES = ["baseline", "flat", "rag"]
NUM_CTX_VALUES = [16384]
REPEATS = 3
BASE_SEED = 42
MAX_FILES = 80
EMBED_MODEL = "nomic-embed-text"
TOP_K = 8
JUDGE_MODEL = "llama3.1:8b"
OUTPUT_DIR = "benchmark_results"
