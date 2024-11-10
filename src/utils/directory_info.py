from pathlib import Path
import os
from datetime import datetime

def print_directory_info(directory_path: str) -> None:
    """
    Print information about all files in the given directory.
    
    Args:
        directory_path (str): Path to the directory to analyze
    """
    # Convert string path to Path object
    dir_path = Path(directory_path)
    
    if not dir_path.exists() or not dir_path.is_dir():
        print(f"Error: {directory_path} is not a valid directory")
        return

    # Get all files in directory
    files = list(dir_path.rglob("*"))
    
    # Print header
    print(f"\nDirectory contents for: {dir_path.absolute()}\n")
    print(f"{'Filename':<40} {'Extension':<10} {'Size (bytes)':<12} {'Last Modified':<20}")
    print("-" * 82)
    
    # Print info for each file
    for file_path in sorted(files):
        if file_path.is_file():  # Only process files, not directories
            # Get file information
            name = file_path.name
            extension = file_path.suffix if file_path.suffix else "(no ext)"
            size = os.path.getsize(file_path)
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            mod_time_str = mod_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Print formatted line
            print(f"{name:<40} {extension:<10} {size:<12} {mod_time_str:<20}")

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."  # Current directory if no argument provided
        
    print_directory_info(directory)
