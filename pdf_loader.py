import hashlib
from pathlib import Path
from llama_index.core import (
    SimpleDirectoryReader, 
    VectorStoreIndex, 
    Settings,
    StorageContext
)
from llama_index.vector_stores.pinecone import PineconeVectorStore

def get_file_hash(file_path):
    """Generate a hash of the file contents"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def load_pdf(pdf_path, pinecone_index):
    """Load and index a PDF file into Pinecone"""
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")
    
    file_hash = get_file_hash(pdf_path)
    print(f"\n=== Processing PDF Document: {pdf_path} ===")
    print(f"Document hash: {file_hash}")
    
    # Create vector store with namespace based on file hash
    vector_store = PineconeVectorStore(
        namespace="disclosures",
        pinecone_index=pinecone_index
    )
    
    # Check if vectors exist for this document by querying with metadata filter
    existing_vectors = pinecone_index.query(
        vector=[0] * 1536,  # dummy vector of correct dimension
        top_k=1,
        filter={
            "file_path": str(pdf_path)
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
        print("\n=== Loading and indexing new PDF Document ===")
        documents = SimpleDirectoryReader(input_files=[pdf_path]).load_data()
        
        # Debug information about loaded documents
        print(f"\nFound {len(documents)} document(s)")
        for i, doc in enumerate(documents):
            # Add file identifier to metadata
            doc.metadata.update({
                "file_hash": file_hash,
                "file_path": str(pdf_path)
            })
            print(f"\nDocument {i+1}:")
            print(f"Length: {len(doc.text)} characters")
            print(f"First 200 characters: {doc.text[:200]}...")
            print(f"Metadata: {doc.metadata}")
        
        print("\n=== Creating Vector Index in Pinecone ===")
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        
        # Create vector index - this will upsert to Pinecone
        index = VectorStoreIndex.from_documents(
            documents,
            storage_context=storage_context,
            show_progress=True
        )
    
    # Debug information about the index
    print(f"\nIndex Stats:")
    print(f"Number of nodes: {len(index.docstore.docs)}")
    print(f"Embedding model: {Settings.embed_model}")
    print(f"LLM model: {Settings.llm}")
    
    return index.as_query_engine()
