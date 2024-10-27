import hashlib
import os
from pathlib import Path

def get_project_root():
    """Get the absolute path to the project root directory"""
    # Assuming this file is in src/utils/files.py
    return str(Path(__file__).parent.parent.parent)

def resolve_path(relative_path):
    """Resolve a path relative to the project root"""
    return os.path.join(get_project_root(), relative_path)

def get_file_hash(file_path):
    """Generate a hash of the file contents"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()
    
def ask_user_for_file_path():
    default_path = "pdfs/disclosures.pdf"
    pdf_path = input(f"Enter the path to your PDF file (press Enter to use {default_path}): ").strip()
    if not pdf_path:
        pdf_path = default_path
    return resolve_path(pdf_path)
