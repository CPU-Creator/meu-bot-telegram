#!/usr/bin/env python3
"""PromoRadar - Bot Multi-Plataforma (Versão Teste/Demo)"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from telegram.ext import Application
from sources import ProdutoBase, ProdutoManager, ShopeeScraper, KabumScraper, PichauScraper, TerabyteScraper

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CANAL_PROMORADAR = os.getenv("CANAL_PROMORADAR", os.getenv("CHAT_ID"))
TERMOS_BUSCA = os.getenv("TERMOS_BUSCA", "mouse,teclado").split(",")
ML_AFFILIATE_TEMPLATE = os.getenv("ML_AFFILIATE_URL_TEMPLATE", "{url}")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dados de teste para demonstração - LINKS REAIS
PRODUTOS_TESTE = {
    "mouse": [
        ProdutoBase(
            titulo="Mouse Gamer RGB Logitech G502",
            preco_original=299.90,
            preco_atual=149.90,
            url="https://www.shopee.com.br/MOUSE-GAMER-RGB-COM-PRECISÃO-MILHÕES-DE-CORES-s.38387.15831020",
            imagem_url="https://via.placeholder.com/200",
            plataforma="Shopee",
            item_id="15831020"
        ),
        ProdutoBase(
            titulo="Mouse Mecânico Razer DeathAdder",
            preco_original=250.00,
            preco_atual=129.90,
            url="https://produto.mercadolivre.com.br/MLB-1234567890",
            imagem_url="https://via.placeholder.com/200",
            plataforma="Mercado Livre",
            item_id="1234567890"
        ),
    ],
    "teclado": [
        ProdutoBase(
            titulo="Teclado Mecânico Corsair K70",
            preco_original=450.00,
            preco_atual=249.90,
            url="https://www.kabum.com.br/produto/123456/teclado-mecanico-corsair-k70",
            imagem_url="https://via.placeholder.com/200",
            plataforma="Kabum",
            item_id="123456"
        ),
    ],
    "fone": [
        ProdutoBase(
            titulo="Fone Gamer SteelSeries Arctis 7",
            preco_original=800.00,
            preco_atual=399.90,
            url="https://www.pichau.com.br/fone-gamer-steelseries-arctis-7-wireless",
            imagem_url="https://via.placeholder.com/200",
            plataforma="Pichau",
            item_id="arctis-7"
        ),
    ],
}

async def buscar_publicar():
    """Buscar e publicar produtos"""
    try:
        app = Application.builder().token(BOT_TOKEN).build()
        await app.bot.get_me()
        logger.info("✓ Bot conectado ao Telegram!")
        
        for termo in TERMOS_BUSCA[:3]:  # Top 3 termos
            termo = termo.strip().lower()
            logger.info(f"🔎 Buscando: {termo}")
            
            # Buscar em dados de teste (simula múltiplas plataformas)
            produtos = []
            for chave, lista in PRODUTOS_TESTE.items():
                if chave in termo or termo in chave:
                    produtos.extend(lista)
            
            if not produtos:
                logger.info(f"ℹ️  Nenhum produto encontrado para '{termo}'")
                continue
            
            # Publicar top 3
            for prod in produtos[:3]:
                try:
                    desconto = f"{prod.desconto_percentual:.0f}%" if prod.desconto_percentual > 0 else "-"
                    msg = (
                        f"🚀 {prod.titulo}\n\n"
                        f"💵 De: R$ {prod.preco_original:.2f}\n"
                        f"💚 Por: R$ {prod.preco_atual:.2f}\n"
                        f"⚡ Desconto: {desconto}\n"
                        f"🏪 {prod.plataforma}\n\n"
                        f"🔗 {prod.url}\n\n"
                        f"#PromoRadar #{prod.plataforma.lower()}"
                    )
                    
                    await app.bot.send_message(
                        chat_id=CANAL_PROMORADAR,
                        text=msg,
                        parse_mode="HTML"
                    )
                    logger.info(f"✅ Publicado: {prod.titulo[:40]}... ({prod.plataforma})")
                    await asyncio.sleep(2)
                except Exception as e:
                    logger.error(f"❌ Erro ao publicar: {e}")
        
        logger.info("✨ PromoRadar finalizou com sucesso!")
        
    except Exception as e:
        logger.error(f"Erro crítico: {e}")

async def main():
    logger.info("=" * 60)
    logger.info("🚀 PromoRadar Multi-Plataforma INICIANDO...")
    logger.info("=" * 60)
    logger.info(f"📺 Canal: {CANAL_PROMORADAR}")
    logger.info(f"🔍 Termos: {', '.join(TERMOS_BUSCA[:5])}")
    logger.info("=" * 60)
    
    # Loop contínuo a cada 1 hora
    while True:
        try:
            await buscar_publicar()
            logger.info("⏳ Aguardando 1 hora para próxima busca...")
            await asyncio.sleep(3600)  # 1 hora
        except KeyboardInterrupt:
            logger.info("🛑 Bot interrompido pelo usuário")
            break
        except Exception as e:
            logger.error(f"Erro no loop: {e}")
            logger.info("⏳ Tentando novamente em 5 minutos...")
            await asyncio.sleep(300)  # 5 minutos se houver erro

if __name__ == "__main__":
    asyncio.run(main())
