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

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
            namespace: str = "intelligent_crawl",
        ):
        if not base_url:
            raise ValueError("Please provide a base URL to start crawling.")
        if not topic:
            raise ValueError("Please provide a topic for the intelligent crawler prompt.")
        
        self.topic = topic
        self.max_pages = 50
        self.base_url = base_url
        self.namespace = namespace
        self.llm = get_open_ai_model()
        self.visited_urls: Set[str] = set()
        
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

        system_prompt_template = PromptTemplate(""" \
            You are an intelligent web crawler that analyzes page content 
            and decides which links to follow. Your goal is to build a comprehensive knowledge 
            base about the topic while staying focused on relevant content.
            You're collecting information to help users understand the topic better.
            Consider:
            1. Is the linked content likely to contain valuable information?
            2. Is it related to the main topic?
            3. Avoid administrative, login, or policy pages.
            4. Prioritize documentation, guides, and substantive content.
            The user's topic: {topic}
            """
        )
        
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
        # First clean the content using BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        cleaned_content = soup.get_text(separator=' ', strip=True)
        
        # Create formatted list of links with their visible text where possible
        link_entries = []
        for i, link in enumerate(links):
            # Try to find the link in the original HTML to get its text
            link_tag = soup.find('a', href=lambda x: x and link.endswith(x))
            link_text = link_tag.get_text(strip=True) if link_tag else "No description"
            link_entries.append(f"{i}: [{link_text}] {link}")
        
        link_list = "\n".join(link_entries)
        
        analysis_prompt_template = PromptTemplate(""" \
            You are analyzing a webpage about {topic} to decide which links to follow next.
            
            Current page content summary:
            {content_snippet}
            
            Available links (format: [link text] URL):
            {link_list}
            
            Instructions:
            1. Choose links that seem most relevant to learning about {topic}
            2. Prefer links to documentation, guides, and detailed content
            3. Avoid links to login pages, policies, or administrative sections
            4. Select 3-5 most promising links
            
            Return ONLY the indices of chosen links, comma-separated without spaces.
            Example return format: 0,2,5
            
            Your selection:
            """
        )
        
        prompt = analysis_prompt_template.format(
            topic=self.topic,
            content_snippet=cleaned_content[:500],  # Use less content but cleaned
            link_list=link_list
        )

        response = self.llm.complete(prompt)

        logger.info(f"Agent response: {response.text}")

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
                logger.debug(f"Starting crawl of URL: {current_url}")
                content = scrape_page(current_url)
                self.visited_urls.add(current_url)
                
                # Extract all links from the page
                all_links = extract_links(content, current_url)
                # Filter for same-domain links
                domain_links = [link for link in all_links if is_same_domain(link, self.base_url)]
                
                # Use agent to decide which links to follow
                relevant_links = self.analyze_page_relevance(content, domain_links)
                
                # Add new relevant links to visit
                new_urls = [url for url in relevant_links if url not in self.visited_urls]
                urls_to_visit.extend(new_urls)
                
                logger.info(f"Page analysis for {current_url}:")
                logger.info(f"- Found {len(domain_links)} total links")
                logger.info(f"- Selected {len(relevant_links)} relevant links: {relevant_links}")
                logger.info(f"- Added {len(new_urls)} new URLs to queue: {new_urls}")
                logger.info(f"- Current queue size: {len(urls_to_visit)}")
                logger.info(f"- Visited {len(self.visited_urls)} pages so far")
                
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
    crawler = IntelligentCrawler(base_url=base_url, topic=topic, namespace=namespace)
    crawler.crawl()
    # Start chat with the indexed content
    from src.scrapers.website import chat_with_saved_site
    chat_with_saved_site(namespace)

if __name__ == "__main__":
    # Example usage
    TEST_URL = "https://help.docebo.com/hc/en-us/sections/4407577387026-Docebo-Flow"
    intelligent_crawl_and_chat(TEST_URL, topic="How much effort is required to implement Docebo on my own website?")
