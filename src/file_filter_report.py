import os
import stat
import shutil
from git import Repo
from config import REPOSITORIES, VALID_FILE_EXTENSIONS, IGNORABLE_FOLDERS

def remove_readonly(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def download_github_repository(github_url):
    destination_folder = github_url.split("/")[-1].replace(".git", "")
    if os.path.exists(destination_folder):
        shutil.rmtree(destination_folder, onexc=remove_readonly)
    
    os.makedirs(destination_folder, exist_ok=True)
    try:
        Repo.clone_from(github_url, destination_folder)
    except Exception as e:
        print(f"Failed to clone {github_url}: {e}")
    return destination_folder

def scan_repository(path):
    selected_files = 0
    for root, _, files in os.walk(path):
        if any(folder in IGNORABLE_FOLDERS or folder.startswith('.') for folder in root.split(os.sep)):
            continue
        for file in files:
            if file.endswith(VALID_FILE_EXTENSIONS):
                selected_files += 1
    return selected_files

for repo_url in REPOSITORIES:
    repo_folder = download_github_repository(repo_url)
    selected_count = scan_repository(repo_folder)
    print(f"Repository: {repo_url} | Filtered Files: {selected_count}")
    shutil.rmtree(repo_folder, onexc=remove_readonly)
