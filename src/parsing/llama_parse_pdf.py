from ..utils.files import get_file_hash, ask_user_for_file_path
from ..vector_stores.pinecone import check_file_hash_exists, get_pinecone

from llama_parse import LlamaParse
from llama_index.core import (
    Settings,
    VectorStoreIndex, 
    SimpleDirectoryReader,
)

parser = LlamaParse(
    result_type="markdown" 
)

def get_pdf_index():
    pdf_path = ask_user_for_file_path()

    file_hash = get_file_hash(pdf_path)

    vector_store, storage_context = get_pinecone()

    if check_file_hash_exists(file_hash):
        print("\n=== Found existing vectors in Pinecone, loading index ===")
        index = VectorStoreIndex.from_vector_store(
            vector_store=vector_store,
            storage_context=storage_context
        )
    else:
        print(f"\n=== Loading and indexing new PDF Document {pdf_path} ===")
        documents = load_data(pdf_path)
        index = VectorStoreIndex.from_documents(
            documents,
            vector_store=vector_store,
            storage_context=storage_context
        )
        print(f"\nIndex Stats:")
        print(f"Number of nodes: {len(index.docstore.docs)}")
        print(f"Embedding model: {Settings.embed_model}")
        print(f"LLM model: {Settings.llm}")
        print(f"Metadata example: {index.docstore.docs[0].metadata}")
    
    return index

def load_pdf_as_query_engine():
    return get_pdf_index().as_query_engine()

def load_data(pdf_path):
    file_extractor = {".pdf": parser}
    reader = SimpleDirectoryReader(input_files=[pdf_path], file_extractor=file_extractor)
    documents = reader.load_data()
    return documents;
