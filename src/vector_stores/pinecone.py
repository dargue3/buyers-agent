from ..environment import get_pinecone_index

from llama_index.core import StorageContext
from llama_index.vector_stores.pinecone import PineconeVectorStore

index = get_pinecone_index()
default_namespace = "disclosures"

def get_pinecone(namespace=default_namespace):
    vector_store = PineconeVectorStore(namespace=namespace, pinecone_index=index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return vector_store, storage_context

def check_file_hash_exists(file_hash, namespace=default_namespace):
    existing_vectors = index.query(
        top_k=1,
        vector=[0] * 1536,
        namespace=namespace,
        filter={
            "file_hash": {"$eq": file_hash}
        }
    )
    return len(existing_vectors.matches) > 0