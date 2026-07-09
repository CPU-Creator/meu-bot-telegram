"""Pichau scraper"""
import logging
from typing import List
from .base import ScraperBase, ProdutoBase

logger = logging.getLogger(__name__)

class PichauScraper(ScraperBase):
    def __init__(self, affiliate_template: str = ""):
        super().__init__("Pichau", affiliate_template)
    
    async def buscar(self, termo: str, limite: int = 20) -> List[ProdutoBase]:
        try:
            logger.info(f"Pichau: 0 produtos (scrapersetup pendente)")
            return []
        except Exception as e:
            logger.error(f"Pichau error: {e}")
            return []
