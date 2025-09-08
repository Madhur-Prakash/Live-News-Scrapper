import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from datetime import datetime, timedelta
from scrapper.models.models import NewsArticle, NewsResponse
from scrapper.helper.utils import NewsScraperService
from scrapper.helper.utils import setup_logging

# Configure logging
logger = setup_logging()
news_router = APIRouter()


# In-memory cache (use Redis in production)
all_news_cache = {
    "articles": [],
    "last_updated": None
}

international_news_cache = {
    "articles": [],
    "last_updated": None
}

indian_news_cache = {
    "articles": [],
    "last_updated": None
}

# Create scraper instance
scraper = NewsScraperService()

async def update_all_news_cache():
    """Update the news cache with fresh articles"""
    try:
        articles = await scraper.scrape_all_sources()
        all_news_cache["articles"] = [article.dict() for article in articles]
        all_news_cache["last_updated"] = datetime.now().isoformat()
        logger.info(f"Cache updated with {len(articles)} articles")
    except Exception as e:
        logger.error(f"Error updating news cache: {str(e)}")

async def update_international_news_cache():
    """Update the international news cache with fresh articles"""
    try:
        articles = await scraper.scrape_international_sources()
        international_news_cache["articles"] = [article.dict() for article in articles]
        international_news_cache["last_updated"] = datetime.now().isoformat()
        logger.info(f"International cache updated with {len(articles)} articles")
    except Exception as e:
        logger.error(f"Error updating international news cache: {str(e)}")

async def update_indian_news_cache():
    """Update the Indian news cache with fresh articles"""
    try:
        articles = await scraper.scrape_indian_sources()
        indian_news_cache["articles"] = [article.dict() for article in articles]
        indian_news_cache["last_updated"] = datetime.now().isoformat()
        logger.info(f"Indian cache updated with {len(articles)} articles")
    except Exception as e:
        logger.error(f"Error updating Indian news cache: {str(e)}")


# API Routes
@news_router.get("/", response_model=dict)
async def root():
    """Health check endpoint"""
    return {
        "message": "Live News API is running",
        "status": "healthy",
        "version": "1.0.0"
    }

@news_router.get("/all_news", response_model=NewsResponse)
async def get_news(
    limit: Optional[int] = 20,
    source: Optional[str] = None,
    refresh: bool = False
):
    """
    Get latest news articles, both Indian and International.
    
    - **limit**: Number of articles to return (default: 20, max: 100)
    - **source**: Filter by news source (optional)
    - **refresh**: Force refresh of news cache (default: False)
    """
    try:
        # Refresh cache if requested or if cache is older than 30 minutes
        if (refresh or 
            not all_news_cache["last_updated"] or 
            datetime.now() - datetime.fromisoformat(all_news_cache["last_updated"]) > timedelta(minutes=30)):
            await update_all_news_cache()
        
        articles = all_news_cache["articles"]
        
        # Filter by source if specified
        if source:
            articles = [a for a in articles if a["source"].lower() == source.lower()]
        
        # Apply limit
        limit = min(limit or 20, 100)
        articles = articles[:limit]
        
        return NewsResponse(
            articles=[NewsArticle(**article) for article in articles],
            total=len(articles),
            last_updated=all_news_cache["last_updated"] or datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error getting news: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@news_router.get("/indian_news", response_model=NewsResponse)
async def get_indian_news(
    limit: Optional[int] = 20,
    source: Optional[str] = None,
    refresh: bool = False
):
    """
    Get latest Indian news articles.
    
    - **limit**: Number of articles to return (default: 20, max: 100)
    - **source**: Filter by news source (optional)
    - **refresh**: Force refresh of news cache (default: False)
    """
    try:
        # Refresh cache if requested or if cache is older than 30 minutes
        if (refresh or 
            not indian_news_cache["last_updated"] or 
            datetime.now() - datetime.fromisoformat(indian_news_cache["last_updated"]) > timedelta(minutes=30)):
            await update_indian_news_cache()

        articles = indian_news_cache["articles"]
        
        # Filter by source if specified
        if source:
            articles = [a for a in articles if a["source"].lower() == source.lower()]
        
        # Apply limit
        limit = min(limit or 20, 100)
        articles = articles[:limit]
        
        return NewsResponse(
            articles=[NewsArticle(**article) for article in articles],
            total=len(articles),
            last_updated=indian_news_cache["last_updated"] or datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error getting Indian news: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@news_router.get("/international_news", response_model=NewsResponse)
async def get_international_news(
    limit: Optional[int] = 20,
    source: Optional[str] = None,
    refresh: bool = False
):
    """
    Get latest international news articles.
    
    - **limit**: Number of articles to return (default: 20, max: 100)
    - **source**: Filter by news source (optional)
    - **refresh**: Force refresh of news cache (default: False)
    """
    try:
        # Refresh cache if requested or if cache is older than 30 minutes
        if (refresh or 
            not international_news_cache["last_updated"] or 
            datetime.now() - datetime.fromisoformat(international_news_cache["last_updated"]) > timedelta(minutes=30)):
            await update_international_news_cache()

        articles = international_news_cache["articles"]
        
        # Filter by source if specified
        if source:
            articles = [a for a in articles if a["source"].lower() == source.lower()]
        
        # Apply limit
        limit = min(limit or 20, 100)
        articles = articles[:limit]
        
        return NewsResponse(
            articles=[NewsArticle(**article) for article in articles],
            total=len(articles),
            last_updated=international_news_cache["last_updated"] or datetime.now().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Error getting international news: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")



@news_router.post("/news/refresh")
async def refresh_news(background_tasks: BackgroundTasks):
    """Manually trigger news cache refresh"""
    background_tasks.add_task(update_all_news_cache)
    return {"message": "News refresh initiated"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(news_router, host="0.0.0.0", port=8000)