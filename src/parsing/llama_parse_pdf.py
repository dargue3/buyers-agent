import os
from src.utils.files import get_file_hash, ask_user_for_file_path
from src.vector_stores.pinecone import check_file_hash_exists, get_pinecone, get_query_engine_by_file_hash
from llama_parse import LlamaParse
from llama_index.core import (
    Settings,
    VectorStoreIndex, 
    SimpleDirectoryReader,
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
