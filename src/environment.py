import os
import warnings
import urllib3
warnings.filterwarnings("ignore", category=urllib3.exceptions.NotOpenSSLWarning)
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from pinecone import Pinecone

def init_environment():
    """Initialize environment variables and Pinecone connection"""
    load_dotenv()
    setup_llama_index()
    return get_pinecone_index()

def setup_llama_index():
    """Setup Llama Index"""
    Settings.llm = get_open_ai_model()

def get_open_ai_model():
    """Get OpenAI instance"""
    return OpenAI(model="gpt-4o", temperature=0.2)

def get_pinecone_index():
    """Get Pinecone index"""
    return Pinecone(api_key=os.getenv("PINECONE_API_KEY")).Index(os.getenv("PINECONE_INDEX_NAME"))

def create_openai_scorer(scorer_class):
    """Create an OpenAI scorer with environment variables"""
    return scorer_class(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE")
    )
