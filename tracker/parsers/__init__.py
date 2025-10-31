from .ozon import parse_ozon


def get_parser(url):
    """Factory function to get appropriate parser based on URL"""
    if "ozon.ru" in url:
        return parse_ozon
    else:
        raise ValueError("Unsupported store URL")