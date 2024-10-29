from typing import List, Set
from urllib.parse import urljoin, urlparse
from llama_index.core.agent import ReActAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI
from llama_index.core.prompts import PromptTemplate
from bs4 import BeautifulSoup
import logging
from src.environment import get_open_ai_model
from src.scrapers.website import scrape_page, scrape_and_index_site

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_links(html_content: str, base_url: str) -> List[str]:
    """Extract and normalize all links from HTML content."""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = []
    
    for a_tag in soup.find_all('a', href=True):
        href = a_tag.get('href')
        if href and not href.startswith(('#', 'mailto:', 'tel:')):
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
    
    return links

def is_same_domain(url1: str, url2: str) -> bool:
    """Check if two URLs belong to the same domain."""
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc
    return domain1 == domain2

class IntelligentCrawler:
    def __init__(
            self,
            topic: str,
            base_url: str,
            max_pages: int = 20,
            namespace: str = "intelligent_crawl",
        ):
        if not base_url:
            raise ValueError("Please provide a base URL to start crawling.")
        if not topic:
            raise ValueError("Please provide a topic for the intelligent crawler prompt.")
        
        self.base_url = base_url
        self.namespace = namespace
        self.max_pages = max_pages
        self.visited_urls: Set[str] = set()
        self.llm = OpenAI(model=get_open_ai_model())
        self.setup_agent()

    def setup_agent(self):
        """Set up the ReAct agent with tools for analyzing content relevance."""
        tools = [
            FunctionTool.from_defaults(
                fn=self.analyze_page_relevance,
                name="analyze_page_relevance",
                description="Analyzes a page's content and its links to determine which are most relevant to follow"
            )
        ]

        system_prompt_template = PromptTemplate("""
        You are an intelligent web crawler that analyzes page content 
        and decides which links to follow. Your goal is to build a comprehensive knowledge 
        base about the topic while staying focused on relevant content. Consider:
        1. Is the linked content likely to contain valuable information?
        2. Is it closely related to the main topic?
        3. Avoid administrative, login, or policy pages.
        4. Prioritize documentation, guides, and substantive content.
        The topic: {topic}
        """)
        
        self.agent = ReActAgent.from_tools(
            tools,
            llm=self.llm,
            verbose=True,
            system_prompt=system_prompt_template.format(topic=self.topic)
        )

    def analyze_page_relevance(self, content: str, links: List[str]) -> List[str]:
        """
        Analyze page content and links to determine which links to follow.
        Returns a list of relevant URLs to crawl next.
        """
        # Create formatted list of links
        link_list = "\n".join([f"{i}: {link}" for i, link in enumerate(links)])
        
        analysis_prompt_template = PromptTemplate("""
        Based on the following page content and list of links, determine which links 
        are most relevant to follow for building a knowledge base. Return only the indices 
        of relevant links, separated by commas.

        Content snippet: {content_snippet}...

        Available links:
        {link_list}

        Return format example: 0,2,5 for selecting links at indices 0, 2, and 5
        """)
        
        prompt = analysis_prompt_template.format(
            content_snippet=content[:1000],
            link_list=link_list
        )
        
        response = self.llm.complete(prompt)
        try:
            selected_indices = [int(i.strip()) for i in response.text.split(',')]
            return [links[i] for i in selected_indices if i < len(links)]
        except Exception as e:
            logger.error(f"Error parsing agent response: {e}")
            return []

    def crawl(self) -> None:
        """
        Start the intelligent crawling process from the base URL.
        """
        urls_to_visit = [self.base_url]
        
        while urls_to_visit and len(self.visited_urls) < self.max_pages:
            current_url = urls_to_visit.pop(0)
            
            if current_url in self.visited_urls:
                continue
                
            try:
                logger.info(f"Crawling: {current_url}")
                content = scrape_page(current_url)
                self.visited_urls.add(current_url)
                
                # Extract all links from the page
                all_links = extract_links(content, current_url)
                # Filter for same-domain links
                domain_links = [link for link in all_links if is_same_domain(link, self.base_url)]
                
                # Use agent to decide which links to follow
                relevant_links = self.analyze_page_relevance(content, domain_links)
                
                # Add new relevant links to visit
                urls_to_visit.extend([
                    url for url in relevant_links 
                    if url not in self.visited_urls
                ])
                
            except Exception as e:
                logger.error(f"Error processing {current_url}: {e}")
                continue
        
        # Index all visited pages
        scrape_and_index_site(
            self.base_url,
            namespace=self.namespace,
            additional_urls=list(self.visited_urls)[1:],  # Skip base_url as it's handled by default
        )

def intelligent_crawl_and_chat(base_url: str, topic: str, namespace: str = "scrapers") -> None:
    """
    Convenience function to crawl a site intelligently and start chatting.
    """
    crawler = IntelligentCrawler(base_url=base_url, namespace=namespace, topic=topic)
    crawler.crawl()
    # Start chat with the indexed content
    from src.scrapers.website import chat_with_saved_site
    chat_with_saved_site(namespace)

if __name__ == "__main__":
    # Example usage
    TEST_URL = "https://help.docebo.com/hc/en-us/sections/4407577387026-Docebo-Flow"
    intelligent_crawl_and_chat(TEST_URL, max_pages=5)
