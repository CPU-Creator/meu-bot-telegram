from .base import ProdutoBase, ScraperBase
from .shopee import ShopeeScraper
from .kabum import KabumScraper
from .pichau import PichauScraper
from .terabyte import TerabyteScraper
from .aliexpress import AliExpressScraper
from .mercadolivre import MercadoLivreScraper
from .manager import ProdutoManager

__all__ = [
    "ProdutoBase",
    "ScraperBase",
    "ShopeeScraper",
    "KabumScraper",
    "PichauScraper",
    "TerabyteScraper",
    "AliExpressScraper",
    "MercadoLivreScraper",
    "ProdutoManager",
]
