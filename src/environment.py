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
    Settings.llm = OpenAI(model="gpt-4o", temperature=0.2)
    
    # Initialize Pinecone
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index_name = os.getenv("PINECONE_INDEX_NAME")
    
    return pc.Index(index_name)
