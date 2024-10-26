import os
from pathlib import Path
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI

def init_environment():
    load_dotenv()
    Settings.llm = OpenAI(model="gpt-4o", temperature=0.2)

def load_pdf(pdf_path):
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")
    
    documents = SimpleDirectoryReader(input_files=[pdf_path]).load_data()
    index = VectorStoreIndex.from_documents(documents)
    return index.as_query_engine()

def chat_with_pdf():
    init_environment()
    
    # Use default path or get PDF path from user
    default_path = "pdfs/disclosures.pdf"
    pdf_path = input(f"Enter the path to your PDF file (press Enter to use {default_path}): ").strip()
    if not pdf_path:
        pdf_path = default_path
    query_engine = load_pdf(pdf_path)
    
    print("\nPDF loaded! You can now chat with your document.")
    print("Type 'quit' to exit the chat.")
    
    while True:
        question = input("\nYour question: ")
        if question.lower() in ['quit', 'exit', 'q']:
            break
            
        response = query_engine.query(question)
        print("\nAnswer:", response.response)

if __name__ == "__main__":
    try:
        chat_with_pdf()
    except Exception as e:
        print(f"An error occurred: {e}")
