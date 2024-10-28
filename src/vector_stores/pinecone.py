from src.environment import get_pinecone_index
from llama_index.core import StorageContext, VectorStoreIndex
from llama_index.vector_stores.pinecone import PineconeVectorStore
from llama_index.core.vector_stores.types import MetadataFilters, ExactMatchFilter

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
    return storage_context, vector_store

def delete_docs_by_file_hash(file_hash, namespace=DEFAULT_NAMESPACE):
    index = get_pinecone_index()
    result = index.delete(
        namespace=namespace,
        filter={
            "file_hash": {"$eq": file_hash}
        }
    )
    print(result)

def check_file_hash_exists(file_hash, namespace=DEFAULT_NAMESPACE):
    """Check if document with given hash exists in Pinecone"""
    index = get_pinecone_index()
    
    # Query with zero vector since we only care about metadata
    existing_vectors = index.query(
        vector=[0] * EMBEDDING_DIM,
        top_k=1,
        namespace=namespace,
        include_metadata=True,
        filter={
            "file_hash": {"$eq": file_hash}
        },
    )
    
    return len(existing_vectors.matches) > 0

def get_query_engine_by_file_hash(file_hash, namespace=DEFAULT_NAMESPACE):
    """Get query engine that only searches documents with matching file_hash"""
    storage_context, vector_store = get_pinecone(namespace)
    
    # Create index from vector store
    index = VectorStoreIndex.from_vector_store(
        vector_store=vector_store,
        storage_context=storage_context
    )

    filters = MetadataFilters(filters=[ExactMatchFilter(key="file_hash", value=file_hash)])
    
    return index.as_query_engine(filters=filters)
