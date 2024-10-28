from pathlib import Path
from llama_index import VectorStoreIndex
from llama_index.storage.storage_context import StorageContext
from llama_index.vector_stores import SimpleVectorStore
from ..utils.files import get_project_root

DEFAULT_VECTOR_DIR = "vector_stores"

def get_storage_path(namespace: str = "default") -> Path:
    """Get the storage directory path for vector stores"""
    vector_dir = get_project_root() / DEFAULT_VECTOR_DIR / namespace
    vector_dir.mkdir(parents=True, exist_ok=True)
    return vector_dir

def save_vector_store(index: VectorStoreIndex, namespace: str = "default") -> None:
    """Save a VectorStoreIndex to the local filesystem"""
    storage_path = get_storage_path(namespace)
    index.storage_context.persist(persist_dir=str(storage_path))

def load_vector_store(namespace: str = "default") -> VectorStoreIndex:
    """Load a VectorStoreIndex from the local filesystem"""
    storage_path = get_storage_path(namespace)
    if not storage_path.exists():
        # Return empty index if no stored data exists
        return VectorStoreIndex([], storage_context=StorageContext.from_defaults(vector_store=SimpleVectorStore()))
    
    storage_context = StorageContext.from_defaults(persist_dir=str(storage_path))
    return VectorStoreIndex([], storage_context=storage_context)
