"""Product manager for multiple sources"""
import logging
import asyncio
from typing import List, Dict
from .base import ProdutoBase, ScraperBase

logger = logging.getLogger(__name__)

class ProdutoManager:
    def __init__(self):
        self.scrapers: Dict[str, ScraperBase] = {}
        self.publicados = set()
    
    def registrar(self, chave: str, scraper: ScraperBase):
        self.scrapers[chave] = scraper
        logger.info(f"Scraper: {chave}")
    
    async def buscar_todos(self, termo: str, limite: int = 20) -> List[ProdutoBase]:
        logger.info(f"Buscando '{termo}' em {len(self.scrapers)} fontes...")
        tasks = [s.buscar(termo, limite) for s in self.scrapers.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        todos = []
        for r in results:
            if isinstance(r, list):
                todos.extend(r)
        logger.info(f"Total: {len(todos)} produtos")
        return todos
    
    async def close_all(self):
        for s in self.scrapers.values():
            await s.close()
