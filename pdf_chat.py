import os
from pathlib import Path
from dotenv import load_dotenv
from pinecone import Pinecone
from llama_index.core import SimpleDirectoryReader, Settings, ServiceContext
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core import VectorStoreIndex

def init_environment():
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

def load_pdf(pdf_path, pinecone_index):
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

def chat_with_pdf():
    pinecone_index = init_environment()
    
    # Use default path or get PDF path from user
    default_path = "pdfs/disclosures.pdf"
    pdf_path = input(f"Enter the path to your PDF file (press Enter to use {default_path}): ").strip()
    if not pdf_path:
        pdf_path = default_path
    query_engine = load_pdf(pdf_path, pinecone_index)
    
    print("\nPDF loaded! You can now chat with your document.")
    print("Type 'quit' to exit the chat.")
    
    while True:
        question = input("\nYour question: ")
        if question.lower() in ['quit', 'exit', 'q']:
            break
            
        response = query_engine.query(question)
        print("\nAnswer:", response.response)

if __name__ == "__main__":
    try:
        chat_with_pdf()
    except Exception as e:
        print(f"An error occurred: {e}")
