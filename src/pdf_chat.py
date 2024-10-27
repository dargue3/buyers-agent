from .environment import init_environment
from .parsing.llama_parse_pdf import load_pdf_as_query_engine
from .chat.chat_engine import chat_loop

def chat_with_pdf():
    init_environment()
    query_engine = load_pdf_as_query_engine()
    chat_loop(query_engine)

if __name__ == "__main__":
    try:
        chat_with_pdf()
    except Exception as e:
        print(f"An error occurred: {e}")
