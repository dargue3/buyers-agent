from pathlib import Path
import os
from datetime import datetime
import csv
import sys

def print_directory_info(directory_path: str) -> None:
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
    writer.writerow(['Filename', 'Extension', 'Size (MB)', 'Last Modified'])
    writer.writerow([])  # Empty row for spacing
    
    # Print info for each file
    for file_path in sorted(files):
        if file_path.is_file():  # Only process files, not directories
            # Get file information
            name = file_path.name
            extension = file_path.suffix if file_path.suffix else "(no ext)"
            size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
            mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            mod_time_str = mod_time.strftime("%Y-%m-%d %H:%M:%S")
            
            # Write CSV row
            writer.writerow([name, extension, f"{size_mb:.2f}", mod_time_str])
            writer.writerow([])  # Empty row for spacing

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."  # Current directory if no argument provided
        
    print_directory_info(directory)
