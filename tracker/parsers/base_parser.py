import requests
from bs4 import BeautifulSoup
from django.core.cache import cache
import time

class BaseParser:
    def __init__(self, url: str):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_html(self, url):
        """Get HTML with caching to prevent excessive requests"""
        cache_key = f"html:{url}"
        html = cache.get(cache_key)
        
        if not html:
            try:
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                html = response.text
                cache.set(cache_key, html, timeout=3600)  # Cache for 1 hour
                time.sleep(1)  # Rate limiting
            except requests.RequestException as e:
                raise Exception(f"Failed to fetch URL: {str(e)}")
        
        return html
    
    def parse_price(self, price_text):
        """Parse price from text, removing currency symbols and converting to float"""
        if not price_text:
            return None
        
        # Remove currency symbols and spaces, replace comma with dot
        price_clean = ''.join(c for c in price_text if c.isdigit() or c in ',.')
        price_clean = price_clean.replace(',', '.')
        
        try:
            return float(price_clean)
        except (ValueError, TypeError):
            return None