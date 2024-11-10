from pathlib import Path
import os
import csv
import sys
import hashlib
from typing import List, Tuple

def generate_file_id(filename: str) -> str:
    """
    Generate a short, deterministic ID from filename.
    Returns first 6 characters of SHA-1 hash.
    """
    return hashlib.sha1(filename.encode()).hexdigest()[:6]

def get_directory_info(directory_path: str) -> List[Tuple[str, str, str, str]]:
    """
    Collect information about files in the given directory.
    
    Args:
        directory_path (str): Path to the directory to analyze
        
    Returns:
        List[tuple]: List of (filename, extension, size_mb) tuples
    """
    dir_path = Path(directory_path)
    
    if not dir_path.exists() or not dir_path.is_dir():
        raise ValueError(f"Error: {directory_path} is not a valid directory")

    # Get only files in the current directory (no recursion), excluding dotfiles
    files = [f for f in dir_path.iterdir() if not f.name.startswith('.')]
    
    # Collect info for each file
    file_info = []
    for file_path in sorted(files):
        if file_path.is_file():  # Only process files, not directories
            name = file_path.name
            extension = file_path.suffix if file_path.suffix else "(no ext)"
            size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
            file_id = generate_file_id(name)
            file_info.append((file_id, name, extension, f"{size_mb:.1f}MB"))
            
    return file_info

def print_directory_info(file_info: List[tuple]) -> None:
    """
    Print directory information in CSV format.
    
    Args:
        file_info (List[tuple]): List of (filename, extension, size_mb) tuples
    """
    writer = csv.writer(sys.stdout)
    writer.writerow(['ID', 'Filename', 'Extension', 'Size (MB)'])
    writer.writerow([])  # Empty row for spacing
    
    for info in file_info:
        writer.writerow(info)
        writer.writerow([])  # Empty row for spacing

if __name__ == "__main__":
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."  # Current directory if no argument provided
        
    try:
        file_info = get_directory_info(directory)
        print_directory_info(file_info)
    except ValueError as e:
        print(e)
