import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import re
import asyncio
import logging
from typing import List, Optional
import httpx
import inspect
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from scrapper.models.models import NewsArticle
from concurrent_log_handler import ConcurrentRotatingFileHandler
from datetime import datetime
from scrapper.config.config import INDIAN_NEWS_SOURCES, INTERNATIONAL_NEWS_SOURCES, MIXED_NEWS_SOURCES

def setup_logging():
    logger = logging.getLogger("scraper_log") # create logger
    if not logger.hasHandlers(): # check if handlers already exist
        logger.setLevel(logging.INFO) # set log level

        # create log directory if it doesn't exist
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)

        # create a file handler
        file_handler = ConcurrentRotatingFileHandler(
            os.path.join(log_dir, "scraper.log"), 
            maxBytes=10000, # 10KB 
            backupCount=500
        )
        file_handler.setLevel(logging.INFO) # The lock file .__scraper.lock is created here by ConcurrentRotatingFileHandler

        #  create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # create a formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(pathname)s - %(filename)s - %(lineno)d" , datefmt="%Y-%m-%d %H:%M:%S")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        #  add the handlers to the logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    return logger

logger = setup_logging()    

class NewsScraperService:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    async def fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch a web page with error handling"""
        try:
            async with httpx.AsyncClient(headers=self.headers, timeout=timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?;:()\'""]', '', text)
        return text[:500]  # Limit length
    
    def get_absolute_url(self, base_url: str, relative_url: str) -> str:
        """Convert relative URL to absolute URL"""
        if not relative_url:
            return ""
        if relative_url.startswith(('http://', 'https://')):
            return relative_url
        return urljoin(base_url, relative_url)
    
    async def scrape_source(self, source: dict) -> List[NewsArticle]:
        """Scrape news from a single source"""
        articles = []
        try:
            html = await self.fetch_page(source["url"])
            if not html:
                return articles
            
            soup = BeautifulSoup(html, 'html.parser')
            selectors = source["selectors"]
            
            # Find article elements
            article_elements = soup.select(selectors["articles"])
            logger.info(f"Found {len(article_elements)} potential articles from {source['name']}")
            
            for element in article_elements[:10]:  # Limit to 10 articles per source
                try:
                    # Extract title
                    title_elem = element.select_one(selectors["title"])
                    if not title_elem:
                        continue
                    
                    title = self.clean_text(title_elem.get_text())
                    if len(title) < 10:  # Skip very short titles
                        continue
                    
                    # Extract link
                    link_elem = element.select_one(selectors["link"]) or element.find('a')
                    if not link_elem or not link_elem.get('href'):
                        continue
                    
                    url = self.get_absolute_url(source["url"], link_elem['href'])
                    
                    # Extract summary
                    summary = ""
                    if "summary" in selectors:
                        summary_elem = element.select_one(selectors["summary"])
                        if summary_elem:
                            summary = self.clean_text(summary_elem.get_text())
                    
                    # If no summary found, use title as fallback
                    if not summary:
                        summary = title[:200] + "..." if len(title) > 200 else title
                    
                    # Extract image if available
                    image_url = ""
                    img_elem = element.find('img')
                    if img_elem and img_elem.get('src'):
                        image_url = self.get_absolute_url(source["url"], img_elem['src'])

                    article = NewsArticle(
                        title=title,
                        summary=summary,
                        url=url,
                        published_at=datetime.now().isoformat(),
                        source=source["name"],
                        category= "Indian" if source in INDIAN_NEWS_SOURCES else "International",
                        image_url=image_url if image_url else None
                    )
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error parsing article from {source['name']}: {str(e)}")
                    continue
            
            logger.info(f"Successfully scraped {len(articles)} articles from {source['name']}")
            
        except Exception as e:
            logger.error(f"Error scraping {source['name']}: {str(e)}")
        
        return articles
    
    async def scrape_all_sources(self) -> List[NewsArticle]:
        """Scrape news from all configured sources"""
        tasks = [self.scrape_source(source) for source in MIXED_NEWS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping source {MIXED_NEWS_SOURCES[i]['name']}: {str(result)}")
            else:
                all_articles.extend(result)
        
        # Remove duplicates based on title similarity
        unique_articles = []
        seen_titles = set()
        
        for article in all_articles:
            # Create a normalized version of title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', article.title.lower())
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_articles.append(article)
        
        return unique_articles
    
    async def scrape_indian_sources(self) -> List[NewsArticle]:
        """Scrape news from Indian sources only"""
        tasks = [self.scrape_source(source) for source in INDIAN_NEWS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        indian_articles = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping source {INDIAN_NEWS_SOURCES[i]['name']}: {str(result)}")
            else:
                indian_articles.extend(result)
        
        # Remove duplicates based on title similarity
        unique_articles = []
        seen_titles = set()
        
        for article in indian_articles:
            # Create a normalized version of title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', article.title.lower())
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_articles.append(article)
        
        return unique_articles
    
    async def scrape_international_sources(self) -> List[NewsArticle]:
        """Scrape news from International sources only"""
        tasks = [self.scrape_source(source) for source in INTERNATIONAL_NEWS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        international_articles = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping source {INTERNATIONAL_NEWS_SOURCES[i]['name']}: {str(result)}")
            else:
                international_articles.extend(result)
        
        # Remove duplicates based on title similarity
        unique_articles = []
        seen_titles = set()
        
        for article in international_articles:
            # Create a normalized version of title for comparison
            normalized_title = re.sub(r'[^\w\s]', '', article.title.lower())
            if normalized_title not in seen_titles:
                seen_titles.add(normalized_title)
                unique_articles.append(article)
        
        return unique_articles