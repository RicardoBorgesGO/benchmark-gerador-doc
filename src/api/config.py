OLLAMA_API_URL = "https://myapi.com/api/chat"
OUTPUT_DIR = "autodoc"
CSV_REPORT_FILE = "generation_metrics.csv"
TOKENIZATION_REPORT_FILE = "tokenization_data.csv"
FILE_TO_MODEL = [
    ("01_tutorials.md", "doc-diataxis-tutorial"),
    ("02_how_to_guide.md", "doc-diataxis-howto"),
    ("03_reference.md", "doc-diataxis-reference"),
    ("04_explanation.md", "doc-diataxis-explanation"),
    ("C4_architecture_level1.md", "doc-c4-level1"),  
    ("C4_architecture_level2.md", "doc-c4-level2"),  
    ("C4_architecture_level3.md", "doc-c4-level3")
]
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

# EXPERIMENT DATA
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
    "https://github.com/habitrpg/habitica",
    "https://github.com/fastapi/fastapi",
    "https://github.com/gorhill/uBlock",
    "https://github.com/zsviczian/obsidian-excalidraw-plugin",
    "https://github.com/jesseduffield/lazygit",
]

OLLAMA_MODELS = [
    "qwen3.6:27b",
]

MODEL_TO_VRAM_USAGE_GB = {
    "qwen3.6:27b": 19_000_000_000,
}