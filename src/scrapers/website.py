from src.chat.chat_engine import chat_loop
from llama_index.core import VectorStoreIndex, download_loader
from llama_index.readers.web import WholeSiteReader
from src.vector_stores.local_storage import save_vector_store, load_vector_store

def scrape_and_index_site(prefix_url: str, base_url: str, namespace: str = "website_docs"):
    """Scrape a website and save it to the local vector store"""
    # Initialize the scraper with a prefix URL and maximum depth
    scraper = WholeSiteReader(
        prefix=prefix_url,
        max_depth=10,
    )

    # Start scraping from a base URL
    documents = scraper.load_data(base_url=base_url)

    print(f"Scraped {len(documents)} documents")
    if documents:
        print(f"First document sample: {documents[0]}")

    # Create and save the index
    index = VectorStoreIndex.from_documents(documents)
    save_vector_store(index, namespace=namespace)
    
    return index

def chat_with_saved_site(namespace: str = "website_docs"):
    """Load saved website index and start chat"""
    index = load_vector_store(namespace=namespace)
    chat_loop(index.as_query_engine())

if __name__ == "__main__":
    # Example usage
    PREFIX_URL = "https://help.docebo.com/hc/en-us"
    BASE_URL = "https://help.docebo.com/hc/en-us/sections/4407577387026-Docebo-Flow"
    
    # Scrape and save
    index = scrape_and_index_site(PREFIX_URL, BASE_URL)
    
    # Start chat interface
    chat_loop(index.as_query_engine())
