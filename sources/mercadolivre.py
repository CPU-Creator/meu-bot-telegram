"""Mercado Livre adapter"""
import logging
from typing import List
from .base import ScraperBase, ProdutoBase

logger = logging.getLogger(__name__)

class MercadoLivreScraper(ScraperBase):
    def __init__(self, affiliate_template: str = "", buscar_func=None):
        super().__init__("Mercado Livre", affiliate_template)
        self.buscar_func = buscar_func
    
    async def buscar(self, termo: str, limite: int = 20) -> List[ProdutoBase]:
        if not self.buscar_func:
            return []
        try:
            items = await self.buscar_func(termo, limite)
            produtos = []
            for item in items:
                try:
                    prod = ProdutoBase(
                        titulo=item.title,
                        preco_original=float(item.original_price) if hasattr(item, "original_price") else item.price * 1.15,
                        preco_atual=float(item.price),
                        url=item.permalink,
                        imagem_url=item.thumbnail if hasattr(item, "thumbnail") else "",
                        plataforma=self.plataforma,
                        item_id=str(item.id),
                        descricao=item.description if hasattr(item, "description") else "",
                    )
                    produtos.append(prod)
                except:
                    pass
            return produtos
        except Exception as e:
            logger.error(f"Mercado Livre error: {e}")
            return []
