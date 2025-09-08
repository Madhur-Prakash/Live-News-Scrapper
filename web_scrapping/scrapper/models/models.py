from pydantic import BaseModel
from typing import List, Optional

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