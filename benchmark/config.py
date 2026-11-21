OLLAMA_API_URL = "http://localhost:11434"
OUTPUT_DIR = "autodoc"
CSV_REPORT_FILE = "generation_metrics.csv"
EVALUATION_REPORT_FILE = "evaluation_results.csv"
TRANSLATED_README_DIR = "translated_readme"

###################
# EXPERIMENT DATA #
###################

REPOSITORIES = [
    # Games
    "https://github.com/marcft/tic-tac-toe",
    "https://github.com/epidemian/snake",
    "https://github.com/thaddeush/SlidingPuzzle",

    # Simple Applications
    "https://github.com/scotch-io/node-todo",

    # Libraries
    "https://github.com/tartley/colorama",
    "https://github.com/expressjs/body-parser",
    "https://github.com/psf/requests",

    # Utilitaries
    "https://github.com/sindresorhus/is-online",
    "https://github.com/chubin/cheat.sh",
    "https://github.com/busyloop/lolcat",
    "https://github.com/Spu7Nix/obamify",

    # Extra Large Repositories (use --top-k)
    # "https://github.com/habitrpg/habitica",
    # "https://github.com/fastapi/fastapi",
    # "https://github.com/gorhill/uBlock",
    # "https://github.com/zsviczian/obsidian-excalidraw-plugin",
    # "https://github.com/jesseduffield/lazygit",
]

OLLAMA_MODELS = [
    # 4-5GB size
    "qwen2.5-coder:7b",
    "deepseek-coder:6.7b",
    "qwen2.5:7b",

    # 13-19GB size
    "qwen2.5-coder:14b",
    "deepseek-coder-v2:16b",
    "gemma4:12b",
    "qwen3.6:27b",
]

JUDGE_MODEL = "gemma4:12b"

LANGUAGES = ["pt"]
TOP_K_VALUES = [0]
NUM_CTX_VALUES = [16384]
REPEATS = 1
