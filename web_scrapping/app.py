import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scrapper.src.web_news import news_router, update_all_news_cache

app = FastAPI(title="Live News API", description="Fetch latest news from multiple sources", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize the news cache on startup"""
    await update_all_news_cache()


app.include_router(news_router, tags=["News"])