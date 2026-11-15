OLLAMA_API_URL = "http://localhost:11434"
OUTPUT_DIR = "autodoc"
CSV_REPORT_FILE = "generation_metrics.csv"
TOKENIZATION_REPORT_FILE = "tokenization_data.csv"
IGNORABLE_FOLDERS = ['node_modules', '.git', '__pycache__', 'doc', 'docs', 'env', 'venv', 'dist', 'build', 'test', 'tests']
VALID_FILE_EXTENSIONS = (
    # Main Codebase
    '.py', '.js', '.jsx', '.ts', '.tsx', '.go', '.java', '.cs', '.cpp', '.c', '.h', '.hpp', '.rs', '.php', '.rb',
    
    # Web
    '.html', '.css', '.scss', '.vue', '.svelte',
    
    # Dependencies and config files
    '.json', '.toml', '.yaml', '.yml', '.ini', '.xml', '.gradle', '.properties',
    
    # Automation and Databases
    '.sh', '.ps1', '.bat', '.cmd', '.sql', '.prisma'
)

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

    # Extra Large Repositories (Discarded)
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