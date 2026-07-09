"""Shopee scraper"""
import logging
import aiohttp
from typing import List
from .base import ScraperBase, ProdutoBase

logger = logging.getLogger(__name__)


class ShopeeScraper(ScraperBase):
    """Scraper Shopee Brasil"""
    
    def __init__(self, affiliate_template: str = ""):
        super().__init__("Shopee", affiliate_template)
        
    async def buscar(self, termo: str, limite: int = 20) -> List[ProdutoBase]:
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"https://shopee.com.br/api/v4/search/search_items"
            params = {"keyword": termo, "limit": min(limite, 50)}
            headers = {"User-Agent": "Mozilla/5.0"}
            
            async with self.session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                produtos = []
                
                for item in data.get("items", [])[:limite]:
                    try:
                        preco = item.get("price", 0) / 100000
                        prod = ProdutoBase(
                            titulo=item.get("name", ""),
                            preco_original=preco * 1.2,
                            preco_atual=preco,
                            url=f"https://shopee.com.br/{item.get('itemid')}",
                            imagem_url=item.get("image", ""),
                            plataforma=self.plataforma,
                            item_id=str(item.get("itemid", "")),
                        )
                        produtos.append(prod)
                    except:
                        pass
                
                return produtos
        except Exception as e:
            logger.error(f"Shopee error: {e}")
            return []
