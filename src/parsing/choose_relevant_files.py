from typing import List
import sys

from llama_index.core.prompts import PromptTemplate

from src.utils.directory_info import get_directory_info
from src.environment import get_open_ai_model
from src.utils.files import resolve_path

def format_files_as_csv(file_info: List[tuple]) -> str:
    """Convert file info tuples to CSV string format."""
    csv_lines = []
    for name, ext, size in file_info:
        csv_lines.append(f"{name},{ext},{size}")
    return "\n".join(csv_lines)

def analyze_directory(directory_path: str) -> str:
    """
    Analyze files in directory and return AI recommendations for relevant files.
    
    Args:
        directory_path (str): Path to directory containing files to analyze
        
    Returns:
        str: AI analysis results
    """
    # Get file information using directory_info utility
    file_info = get_directory_info(directory_path)
    
    # Convert file info to CSV string
    file_list_csv = format_files_as_csv(file_info)
    
    # Load and format prompt template
    prompt_path = resolve_path("prompts/choose_relevant_files.md")
    with open(prompt_path, 'r') as f:
        prompt_text = f.read()
    
    prompt = PromptTemplate(prompt_text)
    
    # Format prompt with file list
    formatted_prompt = prompt.format(fileList=file_list_csv)
    
    # Get OpenAI model and generate response
    llm = get_open_ai_model()
    response = llm.complete(formatted_prompt)
    
    return response.text

def main():
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "."  # Current directory if no argument provided
        
    try:
        result = analyze_directory(directory)
        print(result)
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
