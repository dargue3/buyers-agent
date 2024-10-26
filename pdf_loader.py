from pathlib import Path
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.vector_stores.pinecone import PineconeVectorStore

def load_pdf(pdf_path, pinecone_index):
    """Load and index a PDF file into Pinecone"""
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")
    
    print("\n=== Loading PDF Document ===")
    documents = SimpleDirectoryReader(input_files=[pdf_path]).load_data()
    
    # Debug information about loaded documents
    print(f"\nFound {len(documents)} document(s)")
    for i, doc in enumerate(documents):
        print(f"\nDocument {i+1}:")
        print(f"Length: {len(doc.text)} characters")
        print(f"First 200 characters: {doc.text[:200]}...")
        print(f"Metadata: {doc.metadata}")
    
    print("\n=== Creating Vector Index in Pinecone ===")
    
    # Create vector store
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    
    # Create vector index
    index = VectorStoreIndex.from_documents(
        documents,
        vector_store=vector_store,
        show_progress=True
    )
    
    # Debug information about the index
    print(f"\nIndex Stats:")
    print(f"Number of nodes: {len(index.docstore.docs)}")
    print(f"Embedding model: {Settings.embed_model}")
    print(f"LLM model: {Settings.llm}")
    
    return index.as_query_engine()
