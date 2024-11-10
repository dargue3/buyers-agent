from rich.console import Console                                                                                                 
from rich.markdown import Markdown  

console = Console()

def pretty_print(message):
    """Pretty print the given message for the CLI"""
    markdown = Markdown(message)                                                                                           
    console.print(markdown) 
