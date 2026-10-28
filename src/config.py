OLLAMA_API_URL = "http://localhost:11434"
OUTPUT_DIR = "autodoc"
CSV_REPORT_FILE = "generation_metrics.csv"
TOKENIZATION_REPORT_FILE = "tokenization_data.csv"
IGNORABLE_FOLDERS = ['node_modules', '.git', '__pycache__', 'env', 'venv', 'dist', 'build', 'test', 'tests']
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
    "https://github.com/epidemian/snake",
    "https://github.com/marcft/tic-tac-toe",
    "https://github.com/scotch-io/node-todo",
    "https://github.com/expressjs/body-parser",
    "https://github.com/sindresorhus/is-online",
    "https://github.com/busyloop/lolcat",
    "https://github.com/psf/requests",
    "https://github.com/tartley/colorama",
    "https://github.com/Spu7Nix/obamify",
    "https://github.com/chubin/cheat.sh",
    "https://github.com/thaddeush/SlidingPuzzle",

]

OLLAMA_MODELS = [
    # 4-5GB size
    "qwen2.5-coder:7b",
    "deepseek-coder:6.7b",
    "qwen2.5:7b",  

    # 13-19GB size
    "qwen2.5-coder:14b",
    "deepseek-coder-v2:16b",
    "codellama:34b",
    "gemma4:12b",
    "qwen3.6:27b",
]

JUDGE_MODEL = "gemma4:12b"

MODEL_ARCHITECTURES = {
    "qwen2.5:7b": {
        "parameters_b": 7.6,  
        "quant_bits": 4.5,    
        "context_length": 32768,
        "embedding_length": 3584,
        "num_layers": 28,     
    },
    "codellama:7b": {
        "parameters_b": 7.0,
        "quant_bits": 4.0,    
        "context_length": 16384,
        "embedding_length": 4096,
        "num_layers": 32,     
    },
    "deepseek-coder:6.7b": {
        "parameters_b": 7.0,  
        "quant_bits": 4.0,    
        "context_length": 16384,
        "embedding_length": 4096,
        "num_layers": 28,     
    },
    "qwen2.5-coder:7b": {
        "parameters_b": 7.6,
        "quant_bits": 4.5,    
        "context_length": 32768,
        "embedding_length": 3584,
        "num_layers": 28,
    },
}