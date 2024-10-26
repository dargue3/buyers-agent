import os
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
    
    # Get or create the Pinecone index
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,
            metric="cosine"
        )
    
    return pc.Index(index_name)
