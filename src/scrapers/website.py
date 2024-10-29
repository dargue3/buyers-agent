from src.chat.chat_engine import chat_loop
from llama_index.core import VectorStoreIndex
from playwright.sync_api import sync_playwright
from llama_index.readers.web import BeautifulSoupWebReader
from src.vector_stores.local_storage import save_vector_store, load_vector_store

def scrape_and_index_site(base_url: str, namespace: str = "website_docs"):
    """Scrape a website and save it to the local vector store"""
    reader = BeautifulSoupWebReader()

    documents = reader.load_data(urls=[base_url])

    print(f"Scraped {len(documents)} documents")

    index = VectorStoreIndex.from_documents(documents)
    save_vector_store(index, namespace=namespace)
    
    return index

def chat_with_saved_site(namespace: str = "website_docs"):
    """Load saved website index and start chat"""
    index = load_vector_store(namespace=namespace)
    chat_loop(index.as_query_engine())


def scrape(url):
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # go to url
        page.goto(url)
        # get HTML
        print(page.content())

if __name__ == "__main__":
    URL = "https://help.docebo.com/hc/en-us/sections/4407577387026-Docebo-Flow"

    # chat_with_saved_site("docebo")
    
    scrape(URL)
    # index = scrape_and_index_site(URL, "docebo")
    # chat_loop(index.as_query_engine())
