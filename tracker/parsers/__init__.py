# tracker/parsers/__init__.py
from .creamshop import CreamshopParser
from .base_parser import BaseParser

def get_parser(url: str) -> BaseParser:
    """Factory function to get appropriate parser based on URL"""
    if "creamshop.ru" in url:
        return CreamshopParser(url)
    else:
        raise ValueError(f"Unsupported store URL: {url}")