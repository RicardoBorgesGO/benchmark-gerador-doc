REPO_PATH = r"F:\UFG\M14 - Trabalho de Conclusão de Curso\snake"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OUTPUT_DIR = "autodoc"
FILE_TO_MODEL = [
    # ("01_tutorials.md", "doc-diataxis-tutorial"),
    # ("02_how_to_guides.md", "doc-diataxis-howto"),
    # ("03_reference.md", "doc-diataxis-reference"),
    # ("04_explanation.md", "doc-diataxis-explanation"),
    ("C4_architecture_level1.md", "doc-c4-level1"),  
    ("C4_architecture_level2.md", "doc-c4-level2"),  
    ("C4_architecture_level3.md", "doc-c4-level3")  
]
IGNORABLE_FOLDERS = ['node_modules', '.git', '__pycache__', 'env', 'venv', 'dist', 'build']
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