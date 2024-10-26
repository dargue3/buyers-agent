from environment import init_environment
from pdf_loader import load_pdf
from chat_engine import chat_loop

def chat_with_pdf():
    pinecone_index = init_environment()
    
    # Use default path or get PDF path from user
    default_path = "pdfs/disclosures.pdf"
    pdf_path = input(f"Enter the path to your PDF file (press Enter to use {default_path}): ").strip()
    if not pdf_path:
        pdf_path = default_path
        
    query_engine = load_pdf(pdf_path, pinecone_index)
    chat_loop(query_engine)

if __name__ == "__main__":
    try:
        chat_with_pdf()
    except Exception as e:
        print(f"An error occurred: {e}")
