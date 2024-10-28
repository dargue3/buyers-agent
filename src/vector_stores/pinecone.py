from ..environment import get_pinecone_index
from llama_index.core import StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore

DEFAULT_NAMESPACE = "disclosures"
EMBEDDING_DIM = 1536

def get_pinecone(namespace=DEFAULT_NAMESPACE):
    """Get Pinecone vector store and storage context"""
    index = get_pinecone_index()
    vector_store = PineconeVectorStore(
        pinecone_index=index,
        namespace=namespace,
    )
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return vector_store, storage_context

def check_file_hash_exists(file_hash, namespace=DEFAULT_NAMESPACE):
    """Check if document with given hash exists in Pinecone"""
    index = get_pinecone_index()
    
    # Query with zero vector since we only care about metadata
    existing_vectors = index.query(
        vector=[0] * EMBEDDING_DIM,
        top_k=1,
        namespace=namespace,
        filter={
            "file_hash": {"$eq": file_hash}
        },
        include_metadata=True
    )
    
    return len(existing_vectors.matches) > 0
