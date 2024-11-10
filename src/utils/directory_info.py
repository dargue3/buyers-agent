from pathlib import Path
import os
from datetime import datetime
import csv
import sys
from typing import List

def print_directory_info(files: List[str]) -> None:
    """
    Print information about files in the given directory.
    
    Args:
        files (List[str]): List of filenames to analyze
    """
    # Print header
    print("Filename\tExtension\tSize (MB)")
    print()  # Empty line for spacing
    
    # Print info for each file
    for file in files:
        # Get file information
        name = Path(file).name
        extension = Path(file).suffix if Path(file).suffix else "(no ext)"
        size_mb = os.path.getsize(file) / (1024 * 1024)  # Convert to MB
        
        # Print info as tab-separated values
        print(f"{name}\t{extension}\t{size_mb:.2f}")

def collect_directory_info(directory_path: str) -> None:
    """
    Print information about files in the given directory in CSV format.
    Sizes are in MB and dotfiles are ignored.
    
    Args:
        directory_path (str): Path to the directory to analyze
    """
    # Convert string path to Path object
    dir_path = Path(directory_path)
    
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: {directory_path} is not a valid directory")
        return

    # Get only files in the current directory (no recursion), excluding dotfiles
    files = [f for f in dir_path.iterdir() if not f.name.startswith('.')]
    
    # Print header as CSV
    writer = csv.writer(sys.stdout)
    writer.writerow(['Filename', 'Extension', 'Size (MB)'])
    writer.writerow([])  # Empty row for spacing
    
    # Print info for each file
    for file_path in sorted(files):
        if file_path.is_file():  # Only process files, not directories
            # Get file information
            name = file_path.name
            extension = file_path.suffix if file_path.suffix else "(no ext)"
            size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
            
            # Write CSV row
            writer.writerow([name, extension, f"{size_mb:.2f}"])
            writer.writerow([])  # Empty row for spacing

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."  # Current directory if no argument provided
        
    collect_directory_info(directory)
