"""AliExpress adapter"""
import logging
from typing import List
from .base import ScraperBase, ProdutoBase

logger = logging.getLogger(__name__)

class AliExpressScraper(ScraperBase):
    def __init__(self, affiliate_template: str = "", manager=None):
        super().__init__("AliExpress", affiliate_template)
        self.manager = manager
    
    async def buscar(self, termo: str, limite: int = 20) -> List[ProdutoBase]:
        if not self.manager:
            return []
        try:
            items = self.manager.search(termo, limit=limite)
            produtos = []
            for item in items:
                try:
                    prod = ProdutoBase(
                        titulo=item.title,
                        preco_original=float(item.original_price) if hasattr(item, "original_price") else item.sale_price * 1.2,
                        preco_atual=float(item.sale_price),
                        url=item.url,
                        imagem_url=item.image_url if hasattr(item, "image_url") else "",
                        plataforma=self.plataforma,
                        item_id=str(item.id) if hasattr(item, "id") else "",
                    )
                    produtos.append(prod)
                except:
                    pass
            return produtos
        except Exception as e:
            logger.error(f"AliExpress error: {e}")
            return []
