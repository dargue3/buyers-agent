import os
from firecrawl import FirecrawlApp
from src.chat.chat_engine import chat_loop
from llama_index.core import VectorStoreIndex
from llama_index.readers.web import FireCrawlWebReader
from src.vector_stores.local_storage import save_vector_store, load_vector_store

app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))

def scrape_and_index_site(base_url: str, namespace: str = "website_docs"):
    """Scrape a website and save it to the local vector store"""
    firecrawl_reader = FireCrawlWebReader(
        mode="crawl",
        api_key=os.getenv("FIRECRAWL_API_KEY"),
        params={
            "maxDepth": 3,  # Increase depth to crawl deeper
            "allowBackwardLinks": True,
            "includePaths": ["/hc/en-us/*"],  # Focus on help center paths
            "limit": 100  # Limit total pages to avoid too many requests
        }
    )

    documents = firecrawl_reader.load_data(url=base_url)

    print(f"Scraped {len(documents)} documents")

    index = VectorStoreIndex.from_documents(documents)
    save_vector_store(index, namespace=namespace)
    
    return index

def chat_with_saved_site(namespace: str = "website_docs"):
    """Load saved website index and start chat"""
    index = load_vector_store(namespace=namespace)
    chat_loop(index.as_query_engine())

if __name__ == "__main__":
    URL = "https://help.docebo.com/hc/en-us/sections/4407577387026-Docebo-Flow"

    chat_with_saved_site("docebo")
    
    # index = scrape_and_index_site(URL, "docebo")
    # chat_loop(index.as_query_engine())
