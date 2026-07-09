#!/usr/bin/env python3
"""PromoRadar - Bot de produtos eletrônicos de múltiplas plataformas"""
import os
import logging
import asyncio
from dotenv import load_dotenv
from telegram.ext import Application
from sources import (
    ProdutoManager,
    ShopeeScraper,
    KabumScraper,
    PichauScraper,
    TerabyteScraper,
    AliExpressScraper,
    MercadoLivreScraper,
)

load_dotenv()

# Setup
BOT_TOKEN = os.getenv("BOT_TOKEN")
CANAL_PROMORADAR = os.getenv("CANAL_PROMORADAR", os.getenv("CHAT_ID"))
TERMOS_BUSCA = os.getenv("TERMOS_BUSCA", "mouse,teclado").split(",")
ML_AFFILIATE_TEMPLATE = os.getenv("ML_AFFILIATE_URL_TEMPLATE", "{url}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Manager
manager = ProdutoManager()

async def setup_scrapers():
    """Registrar scrapers"""
    manager.registrar("shopee", ShopeeScraper(ML_AFFILIATE_TEMPLATE))
    manager.registrar("kabum", KabumScraper(ML_AFFILIATE_TEMPLATE))
    manager.registrar("pichau", PichauScraper(ML_AFFILIATE_TEMPLATE))
    manager.registrar("terabyte", TerabyteScraper(ML_AFFILIATE_TEMPLATE))
    logger.info("✓ Scrapers registrados")

async def buscar_publicar():
    """Buscar e publicar"""
    app = Application.builder().token(BOT_TOKEN).build()
    await app.bot.get_me()
    
    for termo in TERMOS_BUSCA:
        termo = termo.strip()
        logger.info(f"🔎 Buscando: {termo}")
        produtos = await manager.buscar_todos(termo, limite=10)
        
        for prod in produtos[:5]:  # Top 5
            try:
                msg = f"🚀 {prod.titulo}\n💵 R$ {prod.preco_atual:.2f} (-{prod.desconto_percentual:.0f}%)\n🏪 {prod.plataforma}\n\n{prod.url}"
                await app.bot.send_message(CANAL_PROMORADAR, msg)
                logger.info(f"✓ Publicado: {prod.titulo}")
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Erro: {e}")
    
    await manager.close_all()

async def main():
    logger.info("PromoRadar iniciando...")
    await setup_scrapers()
    await buscar_publicar()
    logger.info("PromoRadar finalizou")

if __name__ == "__main__":
    asyncio.run(main())
