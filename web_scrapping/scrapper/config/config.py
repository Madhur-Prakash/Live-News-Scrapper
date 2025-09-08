# International News sources configuration
INTERNATIONAL_NEWS_SOURCES = [
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

# Indian news sources configuration
INDIAN_NEWS_SOURCES = [
    {
        "name": "Hindustan Times",
        "url": "https://www.hindustantimes.com/",
        "selectors": {
           "articles": "div[data-vars-storyid]",  
            "title": "h3, h2",  
            "link": "a",  
            "summary": "p"  

        }
    },
    {
        "name": "The Times of India",
        "url": "https://timesofindia.indiatimes.com/",
        "selectors": {
            "articles": "div.list8, div.w_tle",  
            "title": "a",  
            "link": "a",  
            "summary": "p"  
        }
    },
    {
        "name": "The Indian Express",
        "url": "https://indianexpress.com/latest-news/",
        "selectors": {
            "articles": "div.articles",  
            "title": "h2 a",  
            "link": "a",  
            "summary": "p"  
        }
    },
    {
        "name": "News18",
        "url": "https://www.news18.com/news/",
        "selectors": {
            "articles": "div.blog-list-blog",  
            "title": "h2 a",  
            "link": "a",  
            "summary": "p"  
        }
    }
]


MIXED_NEWS_SOURCES = [
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
        "name": "Hindustan Times",
        "url": "https://www.hindustantimes.com/",
        "selectors": {
           "articles": "div[data-vars-storyid]",  
            "title": "h3, h2",  
            "link": "a",  
            "summary": "p"  

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
        "name": "The Indian Express",
        "url": "https://indianexpress.com/latest-news/",
        "selectors": {
            "articles": "div.articles",  
            "title": "h2 a",  
            "link": "a",  
            "summary": "p"  
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
    },
    {
        "name": "The Times of India",
        "url": "https://timesofindia.indiatimes.com/",
        "selectors": {
            "articles": "div.list8, div.w_tle",
            "title": "a",
            "link": "a",
            "summary": "p"
        }
    }
]