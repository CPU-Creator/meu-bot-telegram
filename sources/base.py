"""Base classes for all scrapers"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProdutoBase:
    """Estrutura padronizada de produto"""
    titulo: str
    preco_original: float
    preco_atual: float
    url: str
    imagem_url: str
    plataforma: str
    item_id: str
    descricao: str = ""
    desconto_percentual: float = 0.0
    
    def __post_init__(self):
        if self.preco_original > 0:
            self.desconto_percentual = ((self.preco_original - self.preco_atual) / self.preco_original) * 100
        
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ScraperBase(ABC):
    """Classe base para todos os scrapers"""
    
    def __init__(self, plataforma: str, affiliate_template: str = "", timeout: int = 10):
        self.plataforma = plataforma
        self.affiliate_template = affiliate_template
        self.timeout = timeout
        self.session = None
        
    @abstractmethod
    async def buscar(self, termo: str, limite: int = 20) -> List[ProdutoBase]:
        """Buscar produtos por termo"""
        pass
    
    def aplicar_affiliate_link(self, url: str, titulo: str = "", item_id: str = "") -> str:
        """Aplicar template de link de afiliado"""
        if not self.affiliate_template:
            return url
            
        try:
            from urllib.parse import quote
            url_encoded = quote(url, safe=':/?#[]@!$&\'()*+,;=')
            titulo_encoded = quote(titulo, safe='')
            
            link = self.affiliate_template.format(
                url=url,
                url_encoded=url_encoded,
                item_id=item_id,
                term=titulo,
                term_encoded=titulo_encoded,
            )
            return link
        except Exception as e:
            logger.warning(f"Erro ao aplicar affiliate link: {e}")
            return url
    
    async def close(self):
        """Fechar conexões"""
        if self.session:
            await self.session.close()
