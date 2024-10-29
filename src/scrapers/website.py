from src.chat.chat_engine import chat_loop
from llama_index.core import VectorStoreIndex, Document
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from src.vector_stores.local_storage import save_vector_store, load_vector_store
from typing import List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_content(html: str) -> str:
    """Extract relevant content from HTML, focusing on body and script tags"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove unwanted elements
    for element in soup.find_all(['nav', 'footer', 'header', 'style', 'meta', 'link']):
        element.decompose()
    
    # Get body content
    body = soup.find('body')
    body_text = body.get_text(separator=' ', strip=True) if body else ''
    
    # Get script content (might contain important JS data)
    scripts = soup.find_all('script')
    script_text = ' '.join(script.string for script in scripts if script.string)
    
    return f"{body_text}\n\nEmbedded Scripts:\n{script_text}"

def scrape_page(url: str, wait_for_selector: Optional[str] = None) -> str:
    """Scrape a single page using Playwright"""
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)  # Set to True for production
        try:
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            
            logger.info(f"Navigating to {url}")
            page.goto(url, wait_until="networkidle")
            
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector)
            
            # Wait for dynamic content to load
            page.wait_for_timeout(2000)  # 2 second delay
            
            content = page.content()
            return extract_content(content)
        finally:
            browser.close()

def scrape_and_index_site(base_url: str, namespace: str = "website_docs", 
                         additional_urls: List[str] = None,
                         wait_for_selector: Optional[str] = None) -> VectorStoreIndex:
    """
    Scrape website(s) and save to the local vector store
    
    Args:
        base_url: Main URL to scrape
        namespace: Namespace for vector store
        additional_urls: Optional list of additional URLs to scrape
        wait_for_selector: Optional CSS selector to wait for before scraping
    """
    urls = [base_url]
    if additional_urls:
        urls.extend(additional_urls)
    
    documents = []
    for url in urls:
        try:
            content = scrape_page(url, wait_for_selector)
            doc = Document(text=content, metadata={"source": url})
            documents.append(doc)
            logger.info(f"Successfully scraped {url}")
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
    
    logger.info(f"Scraped {len(documents)} documents")
    
    index = VectorStoreIndex.from_documents(documents)
    save_vector_store(index, namespace=namespace)
    
    return index

def chat_with_saved_site(namespace: str = "website_docs"):
    """Load saved website index and start chat"""
    index = load_vector_store(namespace=namespace)
    query_engine = index.as_query_engine(
        similarity_top_k=3,  # Adjust number of similar chunks to consider
        response_mode="compact"  # For more concise responses
    )
    chat_loop(query_engine)

if __name__ == "__main__":
    URL = "https://help.docebo.com/hc/en-us/sections/4407577387026-Docebo-Flow"
    
    # Example usage:
    index = scrape_and_index_site(
        URL,
        namespace="docebo",
        additional_urls=[
            # Add any additional URLs here
        ],
        wait_for_selector="body"  # Wait for body to load
    )
    chat_loop(index.as_query_engine())
