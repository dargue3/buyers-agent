import os
import requests
from llama_cloud.client import LlamaCloud
from src.utils.files import get_file_hash, ask_user_for_file_path
from src.vector_stores.pinecone import check_file_hash_exists, get_pinecone, get_query_engine_by_file_hash
from llama_parse import LlamaParse
from llama_index.core import (
    Settings,
    VectorStoreIndex, 
    SimpleDirectoryReader,
    Document
)

def get_llama_parser():
    """Get LlamaParse instance with API key"""
    api_key = os.getenv("LLAMA_CLOUD_API_KEY")
    if not api_key:
        raise ValueError("LLAMA_CLOUD_API_KEY environment variable not set")
    return LlamaParse(
        api_key=api_key,
        premium_mode=True,
        result_type="markdown"
    )

def load_pdf_as_query_engine(pdf_path=None):
    """Get or create index for PDF document"""
    if pdf_path is None:
        pdf_path = ask_user_for_file_path()

    file_hash = get_file_hash(pdf_path)
    print(f"\nDocument hash: {file_hash}")

    storage_context = get_pinecone()

    if check_file_hash_exists(file_hash):
        print("\n=== Found existing vectors in Pinecone, loading index ===")
        return get_query_engine_by_file_hash(file_hash)
    
    print(f"\n=== Loading and indexing new PDF Document {pdf_path} ===")
    documents = load_data(pdf_path)
    
    # Add file hash to document metadata
    for doc in documents:
        doc.metadata["file_hash"] = file_hash
    
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context
    )
    
    print(f"\nIndex Stats:")
    print(f"Number of nodes: {len(index.docstore.docs)}")
    print(f"Embedding model: {Settings.embed_model}")
    print(f"LLM model: {Settings.llm}")
    
    return index.as_query_engine()

def load_data(pdf_path):
    """Load and parse PDF document"""
    parser = get_llama_parser()
    file_extractor = {".pdf": parser}
    reader = SimpleDirectoryReader(
        input_files=[pdf_path], 
        file_extractor=file_extractor
    )
    return reader.load_data()

def get_job_results(job_id):
    """Get parsed results from LlamaCloud job ID"""
    
    url = f"https://api.cloud.llamaindex.ai/api/v1/parsing/job/{job_id}/result/markdown"

    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {os.getenv('LLAMA_CLOUD_API_KEY')}"
    }

    response = requests.request("GET", url, headers=headers)
    return response.json().get("markdown")

def load_job_as_query_engine(job_id):
    """Get or create index for LlamaCloud job results"""
    file_hash = job_id  # Use job_id as the unique identifier
    print(f"\nDocument hash/job_id: {file_hash}")

    storage_context, _ = get_pinecone()

    if check_file_hash_exists(file_hash):
        print("\n=== Found existing vectors in Pinecone, loading index ===")
        return get_query_engine_by_file_hash(file_hash)
    
    print(f"\n=== Loading and indexing new content from job {job_id} ===")
    
    # Get markdown content and create Document
    markdown_content = get_job_results(job_id)
    document = Document(
        text=markdown_content,
        metadata={
            "file_hash": file_hash,
            "job_id": job_id,
            "source": "llama_cloud"
        }
    )
    
    index = VectorStoreIndex.from_documents(
        [document],
        storage_context=storage_context
    )
    
    print(f"\nIndex Stats:")
    print(f"Number of nodes: {len(index.docstore.docs)}")
    print(f"Embedding model: {Settings.embed_model}")
    print(f"LLM model: {Settings.llm}")
    
    return index.as_query_engine()
