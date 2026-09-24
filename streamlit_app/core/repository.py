from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import zipfile
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass
class Repository:
    path: Path
    source: str
    name: str


def _safe_repo_name(source: str) -> str:
    parsed = urlparse(source)
    if parsed.scheme:
        name = Path(parsed.path.rstrip("/")).name
    else:
        name = Path(source).stem
    return name or "repository"


def load_from_github(url: str) -> Repository:
    if not url.startswith(("https://github.com/", "http://github.com/")):
        raise ValueError("Informe uma URL pública do GitHub.")

    temp_dir = Path(tempfile.mkdtemp(prefix="llm_guide_"))
    destination = temp_dir / "repo"

    result = subprocess.run(
        ["git", "clone", "--depth", "1", url, str(destination)],
        capture_output=True,
        text=True,
        timeout=180,
    )

    if result.returncode != 0:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise RuntimeError(result.stderr.strip() or "Falha ao clonar o repositório.")

    return Repository(destination, url, _safe_repo_name(url))


def load_from_zip(uploaded_file) -> Repository:
    temp_dir = Path(tempfile.mkdtemp(prefix="llm_guide_"))
    zip_path = temp_dir / "project.zip"
    zip_path.write_bytes(uploaded_file.getvalue())

    extract_dir = temp_dir / "extracted"
    extract_dir.mkdir()

    with zipfile.ZipFile(zip_path) as zf:
        for member in zf.infolist():
            target = (extract_dir / member.filename).resolve()
            if not str(target).startswith(str(extract_dir.resolve()) + os.sep):
                raise ValueError("ZIP contém caminho inválido.")
        zf.extractall(extract_dir)

    # GitHub ZIPs normalmente possuem uma pasta raiz.
    children = [p for p in extract_dir.iterdir()]
    if len(children) == 1 and children[0].is_dir():
        repo_path = children[0]
    else:
        repo_path = extract_dir

    return Repository(repo_path, uploaded_file.name, _safe_repo_name(uploaded_file.name))
