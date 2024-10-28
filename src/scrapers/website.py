from src.chat.chat_engine import chat_loop
from llama_index.core import VectorStoreIndex, download_loader

from llama_index.readers.web import WholeSiteReader

# Initialize the scraper with a prefix URL and maximum depth
scraper = WholeSiteReader(
    prefix="https://help.docebo.com/hc/en-us",  # Example prefix
    max_depth=10,
)

# Start scraping from a base URL
documents = scraper.load_data(
    base_url="https://help.docebo.com/hc/en-us/sections/4407577387026-Docebo-Flow"
)  # Example base URL

print(f"scraped {len(documents)} documents")
print(documents[0])

index = VectorStoreIndex.from_documents(documents)

chat_loop(index.as_query_engine())