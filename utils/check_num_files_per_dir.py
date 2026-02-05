import os
from pathlib import Path
import utils.config as config

BASE_PATH = config.path_projects.joinpath("Dataset-Nb/Docker_kaggle_env/JunoBench/benchmark")

def check_folders_exceed_limit(dir_path):
    MAX_FILES_PER_DIR = 10_000      # Hugging Face Git directory limit
    def count_files_in_dir(dir_path):
        return sum(
            1 for entry in os.scandir(dir_path)
            if entry.is_file()
        )

    print(f"🔍 Scanning for directories with more than {MAX_FILES_PER_DIR} files...\n")

    over_limit = []

    for root, dirs, files in os.walk(BASE_PATH):
        file_count = count_files_in_dir(root)
        if file_count > MAX_FILES_PER_DIR:
            over_limit.append((root, file_count))
            print(f"⚠️  {root} has {file_count} files")

    if not over_limit:
        print("✅ All directories are within the file limit.")
    else:
        print(f"\n🚨 Found {len(over_limit)} directories exceeding the limit.")


def list_unique_extensions(folder_path):
    extensions = set()
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            ext = Path(file).suffix
            if ext:  # skip files without extension
                extensions.add(ext.lower())
    return sorted(extensions)


unique_exts = list_unique_extensions(BASE_PATH)
print("Unique file extensions found:")
for ext in unique_exts:
    print(ext)
