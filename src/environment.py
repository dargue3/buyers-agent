import os
import warnings
import urllib3
warnings.filterwarnings("ignore", category=urllib3.exceptions.NotOpenSSLWarning)
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from pinecone import Pinecone

load_dotenv()

def init_environment():
    """Initialize environment variables and Pinecone connection"""
    load_dotenv()
    setup_llama_index()
    return get_pinecone_index()

def get_default_pdf_path():
    """Get default PDF path"""
    return "pdfs/connie_home_inspection.pdf"

def setup_llama_index():
    """Setup Llama Index"""
    Settings.llm = get_open_ai_model()
    Settings.embed_model = OpenAIEmbedding()

def get_open_ai_model():
    """Get OpenAI instance"""
    return OpenAI(model="gpt-4o", temperature=0.2)

def get_pinecone_index():
    """Get Pinecone index"""
    return Pinecone(api_key=os.getenv("PINECONE_API_KEY")).Index(os.getenv("PINECONE_INDEX_NAME"))

def get_openai_env_vars():
    """Return the OpenAI environment variables"""
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    return api_key, api_base