import logging
from src.chat.chat_engine import chat_loop

logger = logging.getLogger(__name__)
from llama_index.core import VectorStoreIndex, Document
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from src.vector_stores.local_storage import save_vector_store, load_vector_store
from typing import List, Optional

def extract_content(html: str) -> str:
    """Extract relevant content from HTML, preserving links and main content"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Remove unwanted elements
    for element in soup.find_all(['nav', 'footer', 'header', 'style', 'meta']):
        element.decompose()
    
    # Get body content while preserving links
    body = soup.find('body')
    if not body:
        return ''
    
    # Replace links with their text and URL in parentheses
    for a_tag in body.find_all('a'):
        href = a_tag.get('href', '')
        if href and not href.startswith('#'):  # Skip anchor links
            if not href.startswith(('http://', 'https://')):
                # Make relative URLs absolute
                href = f"https://{href}" if href.startswith('//') else href
            # Preserve link text with URL
            a_tag.replace_with(f"[{a_tag.get_text()}]({href})")
    
    return body.get_text(separator=' ', strip=True)

def scrape_page(url: str, wait_for_selector: Optional[str] = None) -> str:
    """Scrape a single page using Playwright"""
    logger.debug(f"Scraping page: {url}")
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)  # Set to True for production
        try:
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()
            
            page.goto(url, wait_until="networkidle")
            
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector)
            
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
    
    logger.debug(f"Starting scrape of {len(urls)} URLs with namespace: {namespace}")
    documents = []
    for url in urls:
        try:
            content = scrape_page(url, wait_for_selector)
            doc = Document(text=content, metadata={"source": url})
            documents.append(doc)
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")

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
