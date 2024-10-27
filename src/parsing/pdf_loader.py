import hashlib
from pathlib import Path
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import (
    SimpleDirectoryReader, 
    VectorStoreIndex, 
    Settings,
    StorageContext
)

def get_query_engine_from_pinecone(index, namespace="disclosures"):
    """Get a query engine from a Pinecone index"""
    vectore_store = PineconeVectorStore(namespace,pinecone_index=index)
    storage_context = StorageContext.from_defaults(vector_store=vectore_store)
    index = VectorStoreIndex.from_vector_store(vectore_store, storage_context=storage_context)
    return index.as_query_engine()

def get_file_hash(file_path):
    """Generate a hash of the file contents"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def load_pdf_as_query_engine(pdf_path, pinecone_index):
    """Load and index a PDF file into Pinecone"""
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")
    
    file_hash = get_file_hash(pdf_path)
    print(f"Document hash: {file_hash}")
    
    # Create vector store with namespace based on file hash
    vector_store = PineconeVectorStore(
        namespace="disclosures",
        pinecone_index=pinecone_index
    )
    
    # Check if vectors exist for this document by querying with metadata filter
    existing_vectors = pinecone_index.query(
        namespace="disclosures",
        vector=[0] * 1536,  # dummy vector of correct dimension
        top_k=1,
        filter={
            "file_hash": {"$eq": file_hash}
        }
    )
    
    if existing_vectors.matches:
        print("\n=== Found existing vectors in Pinecone, loading index ===")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_vector_store(
            vector_store,
            storage_context=storage_context
        )
    else:
        print(f"\n=== Loading and indexing new PDF Document {pdf_path} ===")
        documents = SimpleDirectoryReader(input_files=[pdf_path]).load_data()
        
        print(f"\nFound {len(documents)} document(s)")
        
        print("\n=== Creating Vector Index in Pinecone ===")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # upsert the documents into the index into pinecone
        index = VectorStoreIndex.from_documents(
            documents,
            vector_store=vector_store,
            storage_context=storage_context
        )
        
        # Debug information about the index
        print(f"\nIndex Stats:")
        print(f"Number of nodes: {len(index.docstore.docs)}")
        print(f"Embedding model: {Settings.embed_model}")
        print(f"LLM model: {Settings.llm}")
    
    
    return index.as_query_engine()
