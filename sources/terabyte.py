"""Terabyte scraper"""
import logging
from typing import List
from .base import ScraperBase, ProdutoBase

logger = logging.getLogger(__name__)

class TerabyteScraper(ScraperBase):
    def __init__(self, affiliate_template: str = ""):
        super().__init__("Terabyte", affiliate_template)
    
    async def buscar(self, termo: str, limite: int = 20) -> List[ProdutoBase]:
        try:
            logger.info(f"Terabyte: 0 produtos (scraper setup pendente)")
            return []
        except Exception as e:
            logger.error(f"Terabyte error: {e}")
            return []
