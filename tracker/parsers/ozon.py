from .base_parser import BaseParser
from bs4 import BeautifulSoup

def parse_ozon(url):
    """Parse Ozon product page"""
    parser = BaseParser()
    
    try:
        html = parser.get_html(url)
        soup = BeautifulSoup(html, 'html.parser')
        
        # Try to find JSON-LD data first
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            import json
            try:
                data = json.loads(json_ld.string)
                if '@type' in data and data['@type'] == 'Product':
                    return {
                        'title': data.get('name', ''),
                        'price': parser.parse_price(str(data.get('offers', {}).get('price', ''))),
                        'brand': data.get('brand', {}).get('name', ''),
                        'in_stock': data.get('offers', {}).get('availability', '') == 'InStock'
                    }
            except:
                pass
        
        # Fallback to HTML parsing
        title = soup.find('h1')
        title = title.get_text().strip() if title else ''
        
        # Try multiple selectors for price
        price = None
        price_selectors = [
            '[data-testid="price-value"]',
            '.price-value',
            '.current-price',
            '.price_current'
        ]
        
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text().strip()
                price = parser.parse_price(price_text)
                if price:
                    break
        
        # Check stock status
        in_stock = True  # Default assumption
        out_of_stock_indicators = [
            'нет в наличии',
            'out of stock',
            'sold out',
            'распродано'
        ]
        
        page_text = soup.get_text().lower()
        if any(indicator in page_text for indicator in out_of_stock_indicators):
            in_stock = False
        
        return {
            'title': title,
            'price': price,
            'brand': '',  # Could be extracted from breadcrumbs or specific elements
            'in_stock': in_stock
        }
        
    except Exception as e:
        raise Exception(f"Failed to parse Ozon page: {str(e)}")