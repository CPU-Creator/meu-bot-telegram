#!/usr/bin/env python3
"""PromoRadar - Bot de produtos eletrônicos de múltiplas plataformas"""
import os
import json
import time
import logging
import asyncio
from aiohttp import web, ClientSession
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
INTERVALO = int(os.getenv("INTERVALO", "3600"))
WEB_SERVER_ENABLED = os.getenv("WEB_SERVER_ENABLED", "1").strip().lower() in {"1", "true", "yes", "sim", "on"}
WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST", "0.0.0.0").strip() or "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv("PORT", os.getenv("WEB_SERVER_PORT", "8080")))
ML_CODE_FILE = os.getenv("ML_CODE_FILE", "mercadolivre_code.jsonl").strip() or "mercadolivre_code.jsonl"
ML_TOKEN_FILE = os.getenv("ML_TOKEN_FILE", "mercadolivre_token.json").strip() or "mercadolivre_token.json"
ML_APP_ID = os.getenv("ML_APP_ID", "").strip()
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET", "").strip()
ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI", "").strip()
ML_OAUTH_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

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


def salvar_code_mercadolivre(code, state=None):
    payload = {
        "timestamp": int(time.time()),
        "code": code,
        "state": state,
    }

    with open(ML_CODE_FILE, "a", encoding="utf-8") as arquivo:
        arquivo.write(json.dumps(payload, ensure_ascii=False) + "\n")


def salvar_token_mercadolivre(token_data):
    payload = {
        "timestamp": int(time.time()),
        "token_data": token_data,
    }

    with open(ML_TOKEN_FILE, "w", encoding="utf-8") as arquivo:
        json.dump(payload, arquivo, ensure_ascii=False, indent=2)


async def trocar_code_por_token(code):
    dados = {
        "grant_type": "authorization_code",
        "client_id": ML_APP_ID,
        "client_secret": ML_CLIENT_SECRET,
        "code": code,
        "redirect_uri": ML_REDIRECT_URI,
    }

    async with ClientSession() as session:
        async with session.post(ML_OAUTH_TOKEN_URL, data=dados, timeout=30) as resposta:
            texto = await resposta.text()
            try:
                payload = await resposta.json(content_type=None)
            except Exception:
                payload = {"raw": texto}

            if resposta.status >= 400:
                raise RuntimeError(f"Falha OAuth Mercado Livre ({resposta.status}): {payload}")

            return payload


async def handler_health(_request):
    return web.json_response({"status": "ok"})


async def handler_ml_callback(request):
    code = request.query.get("code", "").strip()
    state = request.query.get("state", "").strip() or None
    error = request.query.get("error", "").strip()
    error_description = request.query.get("error_description", "").strip()

    if error:
        logger.warning(
            "Retorno de autorização do Mercado Livre com erro: error=%s description=%s state=%s",
            error,
            error_description,
            state,
        )
        return web.Response(
            status=400,
            text="Autorização negada ou inválida. Confira os logs para detalhes.",
        )

    if not code:
        return web.Response(
            status=400,
            text="Parâmetro 'code' não encontrado na URL.",
        )

    try:
        salvar_code_mercadolivre(code, state)
    except Exception as erro:
        logger.error("Falha ao salvar code do Mercado Livre: %s", erro)
        return web.Response(status=500, text="Falha ao salvar o code.")

    faltando_oauth = []
    if not ML_APP_ID:
        faltando_oauth.append("ML_APP_ID")
    if not ML_CLIENT_SECRET:
        faltando_oauth.append("ML_CLIENT_SECRET")
    if not ML_REDIRECT_URI:
        faltando_oauth.append("ML_REDIRECT_URI")

    if faltando_oauth:
        faltando_str = ", ".join(faltando_oauth)
        logger.warning(
            "Code capturado, mas faltam variáveis OAuth para gerar token: %s",
            faltando_str,
        )
        return web.Response(
            text=(
                "Code recebido e salvo, mas a troca por token não foi feita. "
                f"Variáveis ausentes: {faltando_str}. "
                "Configure no .env (local) ou nas variáveis de ambiente do deploy e tente novamente."
            )
        )

    try:
        token_data = await trocar_code_por_token(code)
        salvar_token_mercadolivre(token_data)
    except Exception as erro:
        logger.error("Code capturado, mas falhou a troca por token: %s", erro)
        return web.Response(
            status=500,
            text=(
                "Code recebido, mas falhou ao gerar token da API do Mercado Livre. "
                "Confira os logs."
            ),
        )

    logger.info("Token OAuth do Mercado Livre gerado e salvo com sucesso.")
    return web.Response(text="Autorização concluída com sucesso. Token salvo no servidor.")


async def handler_ml_webhook_notification(request):
    try:
        payload = await request.json(content_type=None)
    except Exception:
        payload = None

    if payload is None:
        try:
            payload = await request.text()
        except Exception:
            payload = ""

    logger.info("Webhook Mercado Livre recebido: %s", payload)
    return web.json_response({"status": "ok"})


async def iniciar_servidor_web():
    app = web.Application()
    app.router.add_get("/health", handler_health)
    app.router.add_get("/mercadolivre/callback", handler_ml_callback)
    app.router.add_get("/webhook", handler_ml_callback)
    app.router.add_post("/webhook", handler_ml_webhook_notification)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEB_SERVER_HOST, WEB_SERVER_PORT)
    await site.start()

    logger.info(
        "Servidor web ativo em http://%s:%s (callbacks: /mercadolivre/callback e /webhook)",
        WEB_SERVER_HOST,
        WEB_SERVER_PORT,
    )
    return runner

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
    
    logger.info("Ciclo de busca finalizado")


async def executar_ciclos_publicacao():
    while True:
        try:
            await buscar_publicar()
        except Exception as erro:
            logger.error("Erro no ciclo de publicação: %s", erro)

        logger.info("Aguardando %s segundos para o próximo ciclo", INTERVALO)
        await asyncio.sleep(INTERVALO)

async def main():
    logger.info("PromoRadar iniciando...")
    runner = None

    try:
        await setup_scrapers()

        if WEB_SERVER_ENABLED:
            runner = await iniciar_servidor_web()

        if BOT_TOKEN and CANAL_PROMORADAR:
            await executar_ciclos_publicacao()

        if runner:
            logger.info("Servidor web em execução sem ciclo de publicação configurado.")
            await asyncio.Event().wait()

        raise RuntimeError("Defina BOT_TOKEN e CANAL_PROMORADAR para publicar ou habilite WEB_SERVER_ENABLED para callbacks.")
    finally:
        await manager.close_all()
        if runner:
            await runner.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
