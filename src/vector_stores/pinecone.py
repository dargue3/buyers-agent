from ..environment import get_pinecone_index

from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore

index = get_pinecone_index()
default_namespace = "disclosures"

def get_query_engine_from_pinecone(namespace=default_namespace):
    """Get a query engine from a Pinecone index"""
    vector_store = PineconeVectorStore(pinecone_index=index, namespace=namespace)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_vector_store(vector_store, storage_context=storage_context)
    return index.as_query_engine()

def get_pinecone_vector_store(namespace=default_namespace):
    return PineconeVectorStore(
        namespace=namespace,
        pinecone_index=index
    )

def check_file_hash_exists(file_hash, namespace=default_namespace):
    existing_vectors = index.query(
        top_k=1,
        vector=[0] * 1536,
        namespace=namespace,
        filter={
            "file_hash": {"$eq": file_hash}
        }
    )
    return existing_vectors.matches.length > 0