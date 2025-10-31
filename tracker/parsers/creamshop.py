# tracker/parsers/creamshop.py
from bs4 import BeautifulSoup
from tracker.parsers.base_parser import BaseParser
import re

class CreamshopParser(BaseParser):
    def parse_price(self) -> float:
        html = self.get_html(self.url)  # ← ИСПРАВЛЕНО
        soup = BeautifulSoup(html, 'html.parser')
        price_element = soup.find('span', class_='detail__price')
        if not price_element:
            raise ValueError("Price element not found on page")
        price_text = price_element.get_text(strip=True)
        price_clean = re.sub(r'[^\d\s]', '', price_text)  # убираем всё кроме цифр и пробелов
        price_clean = price_clean.replace(' ', '')         # "10 699" → "10699"
        try:
            return float(price_clean)
        except ValueError as e:
            raise ValueError(f"Could not parse price from '{price_text}': {e}")

    def get_data(self) -> dict:
        html = self.get_html(self.url)  # ← ИСПРАВЛЕНО
        soup = BeautifulSoup(html, 'html.parser')

        title_elem = soup.find('h1', class_='detail__title')
        title = title_elem.get_text(strip=True) if title_elem else "Unknown title"

        return {
            'price': self.parse_price(),
            'title': title,
            'brand': 'Anteater',
            'in_stock': True,
        }