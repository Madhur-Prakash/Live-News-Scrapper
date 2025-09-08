# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup
import asyncio
from datetime import datetime, timedelta
import re
import logging
from urllib.parse import urljoin, urlparse
import json
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Live News API", description="Fetch latest news from multiple sources", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class NewsArticle(BaseModel):
    title: str
    summary: str
    url: str
    published_at: str
    source: str
    category: Optional[str] = None
    image_url: Optional[str] = None

class NewsResponse(BaseModel):
    articles: List[NewsArticle]
    total: int
    last_updated: str

# In-memory cache (use Redis in production)
news_cache = {
    "articles": [],
    "last_updated": None
}

# News sources configuration
NEWS_SOURCES = [
    {
        "name": "BBC News",
        "url": "https://www.bbc.com/news",
        "selectors": {
            "articles": "article, .media__content, .gs-c-promo",
            "title": "h3, .media__title, .gs-c-promo-heading__title",
            "link": "a",
            "summary": ".media__summary, .gs-c-promo-summary",
        }
    },
    {
        "name": "Reuters",
        "url": "https://www.reuters.com/world/",
        "selectors": {
            "articles": "[data-testid='MediaStoryCard'], .story-card",
            "title": "[data-testid='Heading'], .story-card__headline",
            "link": "a",
            "summary": "[data-testid='Body'], .story-card__summary",
        }
    },
    {
        "name": "CNN",
        "url": "https://edition.cnn.com/",
        "selectors": {
            "articles": ".container__item, .card",
            "title": ".container__headline, .card__headline",
            "link": "a",
            "summary": ".container__summary, .card__summary",
        }
    }
]

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
        tasks = [self.scrape_source(source) for source in NEWS_SOURCES]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_articles = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error scraping source {NEWS_SOURCES[i]['name']}: {str(result)}")
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

# Create scraper instance
scraper = NewsScraperService()

async def update_news_cache():
    """Update the news cache with fresh articles"""
    try:
        articles = await scraper.scrape_all_sources()
        news_cache["articles"] = [article.dict() for article in articles]
        news_cache["last_updated"] = datetime.now().isoformat()
        logger.info(f"Cache updated with {len(articles)} articles")
    except Exception as e:
        logger.error(f"Error updating news cache: {str(e)}")

@app.on_event("startup")
async def startup_event():
    """Initialize the news cache on startup"""
    await update_news_cache()

# API Routes
@app.get("/", response_model=dict)
async def root():
    """Health check endpoint"""
    return {
        "message": "Live News API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/news", response_model=NewsResponse)
async def get_news(
    limit: Optional[int] = 20,
    source: Optional[str] = None,
    refresh: bool = False
):
    """
    Get latest news articles
    
    - **limit**: Number of articles to return (default: 20, max: 100)
    - **source**: Filter by news source (optional)
    - **refresh**: Force refresh of news cache (default: False)
    """
    try:
        # Refresh cache if requested or if cache is older than 30 minutes
        if (refresh or 
            not news_cache["last_updated"] or 
            datetime.now() - datetime.fromisoformat(news_cache["last_updated"]) > timedelta(minutes=30)):
            await update_news_cache()
        
        articles = news_cache["articles"]
        
        # Filter by source if specified
        if source:
            articles = [a for a in articles if a["source"].lower() == source.lower()]
        
        # Apply limit
        limit = min(limit or 20, 100)
        articles = articles[:limit]
        
        return NewsResponse(
            articles=[NewsArticle(**article) for article in articles],
            total=len(articles),
            last_updated=news_cache["last_updated"] or datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error getting news: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/news/sources")
async def get_sources():
    """Get list of available news sources"""
    return {
        "sources": [source["name"] for source in NEWS_SOURCES],
        "total": len(NEWS_SOURCES)
    }

@app.post("/news/refresh")
async def refresh_news(background_tasks: BackgroundTasks):
    """Manually trigger news cache refresh"""
    background_tasks.add_task(update_news_cache)
    return {"message": "News refresh initiated"}

@app.get("/news/stats")
async def get_stats():
    """Get API statistics"""
    return {
        "total_articles": len(news_cache["articles"]),
        "last_updated": news_cache["last_updated"],
        "sources_count": len(NEWS_SOURCES),
        "cache_age_minutes": (
            (datetime.now() - datetime.fromisoformat(news_cache["last_updated"])).total_seconds() / 60
            if news_cache["last_updated"] else None
        )
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)