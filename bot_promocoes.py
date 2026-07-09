
import asyncio
import random
import html
import os
import time
import shutil
import sys
import logging
import tempfile
import json
from io import BytesIO
from urllib.request import urlopen

from PIL import Image

from dotenv import load_dotenv
from aiohttp import web, ClientSession

from telegram import Bot
from telegram.constants import ParseMode

from aliexpress_api import AliexpressApi, models

from agente_ia import analisar_produto
from pontuacao import calcular_pontuacao
from memoria import (
    criar_banco,
    produto_existe,
    salvar_produto,
    incrementar_metricas,
)


load_dotenv()

# configurar logging básico (nível configurável via LOG_LEVEL)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
numeric_level = getattr(logging, LOG_LEVEL, logging.INFO)
logging.basicConfig(level=numeric_level, format="%(asctime)s %(levelname)s: %(message)s")


# ==========================

# modos de busca: vendas (top sellers) e popularidade/pesquisas
SEARCH_SORTS = [
    "VOLUME_DESC",      # produtos mais vendidos
    "POPULARITY_DESC",  # produtos mais populares / mais procurados (caso API suporte)
]

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

CHAT_ID = os.getenv("CHAT_ID", "").strip()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()


ALI_KEY = os.getenv("ALI_KEY", "").strip()

ALI_SECRET = os.getenv("ALI_SECRET", "").strip()

TRACKING_ID = os.getenv(
    "TRACKING_ID",
    ""
).strip()

# valores configuráveis
INTERVALO = int(os.getenv("INTERVALO", "300"))
LOGO = os.getenv("LOGO", "").strip()
WEB_SERVER_ENABLED = os.getenv("WEB_SERVER_ENABLED", "1").strip().lower() in {"1", "true", "yes", "sim", "on"}
WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST", "0.0.0.0").strip() or "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv("PORT", os.getenv("WEB_SERVER_PORT", "8080")))
ML_CODE_FILE = os.getenv("ML_CODE_FILE", "mercadolivre_code.jsonl").strip() or "mercadolivre_code.jsonl"
ML_TOKEN_FILE = os.getenv("ML_TOKEN_FILE", "mercadolivre_token.json").strip() or "mercadolivre_token.json"
ML_APP_ID = os.getenv("ML_APP_ID", "").strip()
ML_CLIENT_SECRET = os.getenv("ML_CLIENT_SECRET", "").strip()
ML_REDIRECT_URI = os.getenv("ML_REDIRECT_URI", "").strip()
ML_OAUTH_TOKEN_URL = "https://api.mercadolibre.com/oauth/token"

# inicializar cliente da AliExpress (tentar assinaturas comuns)
try:
    manager = AliexpressApi(api_key=ALI_KEY, api_secret=ALI_SECRET, language="PT", currency="BRL")
except TypeError:
    try:
        manager = AliexpressApi(ALI_KEY, ALI_SECRET, "PT", "BRL")
    except Exception as e:
        logging.warning("Falha ao inicializar AliexpressApi: %s", e)
        manager = None
except Exception as e:
    logging.warning("Falha ao inicializar AliexpressApi: %s", e)
    manager = None

# ==========================
# BUSCAS
# ==========================


termos = [

    "mouse gamer",

    "teclado mecanico",

    "fone bluetooth",

    "headset gamer",

    "ssd nvme",

    "memoria ram ddr4",

    "memoria ram ddr5",

    "carregador turbo",

    "controle bluetooth",

    "fita led rgb",

    "lampada inteligente",

    "camera wifi",

    "air fryer",

    "cafeteira"

]



# ==========================
# NICHO
# ==========================


def pertence_nicho(produto):

    nome = produto.product_title.lower()


    palavras = [

        "mouse",
        "teclado",
        "fone",
        "headset",
        "ssd",
        "nvme",
        "ram",
        "memoria",
        "carregador",
        "controle",
        "led",
        "smart",
        "wifi",
        "camera",
        "air fryer",
        "cafeteira"

    ]


    return any(

        palavra in nome

        for palavra in palavras

    )



# ==========================
# PREÇO E DESCONTO
# ==========================


def calcular_desconto(produto):

    atual = float(

        str(

            getattr(

                produto,

                "target_sale_price",

                0

            )

        ).replace(",", ".")

    )


    antigo = float(

        str(

            getattr(

                produto,

                "original_price",

                0

            )

        ).replace(",", ".")

    )


    if antigo <= atual:

        antigo = atual * 1.4


    desconto = int(

        ((antigo - atual) / antigo) * 100

    )


    desconto = max(

        1,

        min(desconto, 95)

    )


    return antigo, atual, desconto


def _texto_nao_vazio(valor):

    if valor is None:

        return None


    if isinstance(valor, str):

        texto = valor.strip()

        return texto or None


    return valor


def _coletar_atributos_objeto(valor):

    dados = []


    if hasattr(valor, "__dict__"):

        try:

            dados.append(vars(valor))

        except Exception:

            pass


    if hasattr(valor, "items"):

        try:

            dados.append(dict(valor))

        except Exception:

            pass


    return dados


def _extrair_campo_textual(valor, nomes_chave):

    if isinstance(valor, dict):

        for chave in nomes_chave:

            texto = _texto_nao_vazio(valor.get(chave))

            if texto:

                return texto


    for dados in _coletar_atributos_objeto(valor):

        if not isinstance(dados, dict):

            continue


        for chave in nomes_chave:

            if chave in dados:

                texto = _texto_nao_vazio(dados.get(chave))

                if texto:

                    return texto


    return None


def _formatar_cupom(produto):

    chaves_cupom = (

        "coupon_code",

        "coupon",

        "discount_coupon",

        "coupon_info",

        "promotion_code",

        "couponList",

        "coupon_list",

        "couponData",

        "coupon_data",

        "promo_code",

        "promotionCode",

        "couponCode",

    )


    for key in chaves_cupom:

        if not hasattr(produto, key):

            continue


        val = getattr(produto, key)

        if isinstance(val, dict):

            code = (
                val.get("code")
                or val.get("coupon_code")
                or val.get("couponCode")
                or val.get("name")
                or val.get("title")
                or val.get("promo_code")
                or val.get("promotion_code")
            )

            amount = (
                val.get("amount")
                or val.get("discount")
                or val.get("value")
                or val.get("coupon_amount")
                or val.get("discountAmount")
            )

            if not code:

                code = _extrair_campo_textual(val, ("code", "coupon_code", "couponCode", "name", "title", "promo_code", "promotion_code"))

            if not amount:

                amount = _extrair_campo_textual(val, ("amount", "discount", "value", "coupon_amount", "discountAmount"))

            if code and amount:

                return f"{code} ({amount})"


            if code:

                return str(code)


            if amount:

                return str(amount)


        elif isinstance(val, (list, tuple)) and val:

            primeiro = val[0]

            if isinstance(primeiro, dict):

                code = (
                    primeiro.get("code")
                    or primeiro.get("coupon_code")
                    or primeiro.get("couponCode")
                    or primeiro.get("name")
                    or primeiro.get("title")
                    or primeiro.get("promo_code")
                    or primeiro.get("promotion_code")
                )

                amount = (
                    primeiro.get("amount")
                    or primeiro.get("discount")
                    or primeiro.get("value")
                    or primeiro.get("coupon_amount")
                    or primeiro.get("discountAmount")
                )

                if not code:

                    code = _extrair_campo_textual(primeiro, ("code", "coupon_code", "couponCode", "name", "title", "promo_code", "promotion_code"))

                if not amount:

                    amount = _extrair_campo_textual(primeiro, ("amount", "discount", "value", "coupon_amount", "discountAmount"))

                if code and amount:

                    return f"{code} ({amount})"


                if code:

                    return str(code)


                if amount:

                    return str(amount)


            texto = _texto_nao_vazio(primeiro)

            if texto:

                return str(texto)


        elif hasattr(val, "__dict__") or hasattr(val, "items"):

            code = _extrair_campo_textual(val, ("code", "coupon_code", "couponCode", "name", "title", "promo_code", "promotion_code"))

            amount = _extrair_campo_textual(val, ("amount", "discount", "value", "coupon_amount", "discountAmount"))

            if code and amount:

                return f"{code} ({amount})"

            if code:

                return str(code)

            if amount:

                return str(amount)


        else:

            texto = _texto_nao_vazio(val)

            if texto:

                return str(texto)


    return None


def _formatar_parcelamento(produto):

    for key in ("installments", "installment_info", "pay_installment", "max_installment", "payment_info"):

        if not hasattr(produto, key):

            continue


        val = getattr(produto, key)

        if isinstance(val, dict):

            n = val.get("count") or val.get("max") or val.get("number") or val.get("installment_count")

            v = val.get("value") or val.get("per_installment") or val.get("amount")

            juros = val.get("interest") or val.get("has_interest")

            if n and v:

                status_juros = "com juros" if juros else "sem juros"

                return f"até {n}x de R$ {float(v):.2f} {status_juros}"


            if n:

                return f"até {n}x"


        elif isinstance(val, (list, tuple)) and val:

            primeiro = val[0]

            if isinstance(primeiro, dict):

                n = primeiro.get("count") or primeiro.get("max") or primeiro.get("number") or primeiro.get("installment_count")

                v = primeiro.get("value") or primeiro.get("per_installment") or primeiro.get("amount")

                juros = primeiro.get("interest") or primeiro.get("has_interest")

                if n and v:

                    status_juros = "com juros" if juros else "sem juros"

                    return f"até {n}x de R$ {float(v):.2f} {status_juros}"


                if n:

                    return f"até {n}x"


            texto = _texto_nao_vazio(primeiro)

            if texto:

                return str(texto)


        else:

            texto = _texto_nao_vazio(val)

            if texto:

                return str(texto)


    return None


def _formatar_frete_gratis(produto):

    candidatos = (

        "free_shipping",

        "freeShipping",

        "has_free_shipping",

        "shipping_free",

        "frete_gratis",

        "frete_grátis",

        "ship_free",

        "shipping_fee",

    )


    for key in candidatos:

        if not hasattr(produto, key):

            continue


        val = getattr(produto, key)

        if isinstance(val, bool):

            if val:

                return "Frete grátis"


        elif isinstance(val, dict):

            for nested_key in ("text", "label", "title", "value", "status"):

                nested = _texto_nao_vazio(val.get(nested_key))

                if not nested:

                    continue


                if isinstance(nested, str) and ("frete" in nested.lower() or "free" in nested.lower()):

                    return nested


                if str(nested).lower() in {"true", "yes", "sim", "free", "gratis", "grátis"}:

                    return "Frete grátis"


            if val:

                return "Frete grátis"


        else:

            texto = _texto_nao_vazio(val)

            if isinstance(texto, str) and texto:

                if "frete" in texto.lower() or "free" in texto.lower():

                    return texto


                if texto.lower() in {"1", "true", "yes", "sim", "gratis", "grátis"}:

                    return "Frete grátis"


    return None


def _mesclar_produto_com_detalhes(produto, detalhes):

    if not detalhes:

        return produto


    for chave, valor in vars(detalhes).items():

        atual = getattr(produto, chave, None)

        if atual in (None, "", [], (), {}):

            setattr(produto, chave, valor)


    return produto


def enriquecer_produto_com_detalhes(cliente_api, produto):

    if cliente_api is None:

        return produto


    product_id = getattr(produto, "product_id", None)

    if not product_id:

        return produto


    try:

        detalhes = cliente_api.get_products_details([str(product_id)])

    except Exception as erro:

        logging.debug("Falha ao buscar detalhes do produto %s: %s", product_id, erro)

        return produto


    if not detalhes:

        return produto


    detalhe = detalhes[0]

    if hasattr(detalhe, "__dict__"):

        return _mesclar_produto_com_detalhes(produto, detalhe)


    return produto



# ==========================
# DADOS PARA IA
# ==========================


def preparar_produto(produto):

    antigo, atual, desconto = calcular_desconto(produto)


    cupom = None
    # possíveis campos de cupom (depende da resposta da API)
    for key in ("coupon_code", "coupon", "discount_coupon", "coupon_info"):
        if hasattr(produto, key):
            cupom = getattr(produto, key)
            break

    parcelas = None
    # possíveis campos de parcelamento
    for key in ("installments", "installment_info", "pay_installment", "max_installment"):
        if hasattr(produto, key):
            parcelas = getattr(produto, key)
            break

    return f"""

Produto:

{produto.product_title}

Preço antigo:

R$ {antigo:.2f}

Preço atual:

R$ {atual:.2f}

Desconto:

{desconto}%

Avaliação:

{getattr(produto,'evaluate_rate','N/A')}

Vendas:

{getattr(produto,'lastest_volume','N/A')}

Cupom:

{cupom if cupom else 'N/A'}

Parcelamento:

{parcelas if parcelas else 'N/A'}

"""



# ==========================
# LOGO NA IMAGEM
# ==========================


def colocar_logo(imagem):
    if not LOGO:
        return imagem

    try:
        if not os.path.exists(LOGO):
            return imagem

        if isinstance(imagem, str) and imagem.startswith(("http://", "https://")):
            with urlopen(imagem) as resposta:
                base = Image.open(BytesIO(resposta.read())).convert("RGBA")
        else:
            base = Image.open(imagem).convert("RGBA")

        logo = Image.open(LOGO).convert("RGBA")
        logo.thumbnail((150, 150))
        base.paste(logo, (20, 20), logo)
        with tempfile.NamedTemporaryFile(prefix="promoradar_", suffix=".png", delete=False) as temp_file:
            arquivo = temp_file.name
        base.save(arquivo)
        return arquivo
    except Exception as e:
        logging.warning("Aviso: falha ao processar logo na imagem: %s", e)
        return imagem



# ==========================
# MENSAGEM
# ==========================


def formatar_tempo(segundos):
    if segundos <= 0:
        return "agora"

    horas, resto = divmod(int(segundos), 3600)
    minutos, segundos_restantes = divmod(resto, 60)

    partes = []
    if horas:
        partes.append(f"{horas}h")
    if minutos:
        partes.append(f"{minutos}m")
    if segundos_restantes or not partes:
        partes.append(f"{segundos_restantes}s")

    return " ".join(partes)


def imprimir_painel(ciclo, total_publicacoes, total_tentativas, tempo_restante, tempo_decorrido, status, mensagem_log=None):
    largura = 94
    cor_status = "\033[92m"
    if status == "falha":
        cor_status = "\033[91m"
    elif status == "erro":
        cor_status = "\033[93m"
    elif status == "enviando":
        cor_status = "\033[96m"

    reset = "\033[0m"
    barra = int((1 - (tempo_restante / INTERVALO)) * 20) if INTERVALO else 0
    barra = max(0, min(20, barra))
    barra_texto = "█" * barra + "░" * (20 - barra)

    print("\033[2J\033[H", end="")
    print("╔" + "═" * (largura - 2) + "╗")
    print("║" + " PROMORADAR - STATUS DO BOT ".center(largura - 2) + "║")
    print("╠" + "═" * (largura - 2) + "╣")
    print(f"║ {'Ciclo:':<10} {ciclo:<8} {'Publicações:':<12} {total_publicacoes:<6} {'Tentativas:':<10} {total_tentativas:<6} ║")
    print(f"║ {'Próx. publicação:':<18} {formatar_tempo(tempo_restante):<16} {'Últ. envio:':<10} {formatar_tempo(int(tempo_decorrido)):<16} ║")
    print(f"║ {'Status:':<8} {cor_status}{status:<20}{reset} {'Barra:':<8} [{barra_texto}] ║")
    if mensagem_log:
        print(f"║ Log: {mensagem_log[:74]:<80} ║")
    print("╠" + "═" * (largura - 2) + "╣")
    print("║ Últimas mensagens: " + " " * (largura - 20) + "║")
    print("╚" + "═" * (largura - 2) + "╝")


async def enviar_mensagem_segura(bot, chat_id, photo, caption, parse_mode):
    try:
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            parse_mode=parse_mode,
        )
        return True
    except Exception as erro:
        logging.warning("Falha no envio de foto, tentando mensagem de texto: %s", erro)
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=caption,
                parse_mode=parse_mode,
            )
            return True
        except Exception as erro_texto:
            logging.error("Falha ao enviar mensagem de texto: %s", erro_texto)
            return False


def criar_mensagem(produto, legenda):

    titulo = html.escape(

        produto.product_title

    )[:100]


    antigo, atual, desconto = calcular_desconto(produto)


    link = getattr(

        produto,

        "promotion_link",

        "#"

    )

    cupom_text = _formatar_cupom(produto)
    parcelas_text = _formatar_parcelamento(produto)
    frete_text = _formatar_frete_gratis(produto)



    msg = f"""🔥 <b>PROMORADAR</b> 🔥
📦 <b>{titulo}</b>

{legenda}

✨ <b>Destaques</b>
💸 <b>Desconto:</b> {desconto}% OFF
🏷️ <b>De:</b> <s>R$ {antigo:.2f}</s>
💰 <b>Por:</b> <b>R$ {atual:.2f}</b>
🛒 <b>Link:</b> <a href="{link}">clique aqui</a>"""

    # anexar cupom e parcelamento visíveis quando disponíveis
    extras = []
    if cupom_text:
        extras.append(f"🎟️ Cupom disponível: <b>{html.escape(str(cupom_text))}</b>")
    else:
        extras.append("🎟️ Cupom: consulte os cupons ativos na página do produto")
    if parcelas_text:
        extras.append(f"💳 Parcelamento: <b>{html.escape(str(parcelas_text))}</b>")
    if frete_text:
        extras.append(f"🚚 <b>Frete:</b> {html.escape(str(frete_text))}")
    else:
        extras.append("🚚 Frete grátis: verifique na página do produto")

    if extras:
        msg = msg + "\n" + "\n".join(extras) + "\n\n"

    return msg


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
        logging.warning(
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
        logging.error("Falha ao salvar code do Mercado Livre: %s", erro)
        return web.Response(status=500, text="Falha ao salvar o code.")

    tem_config_oauth = all([ML_APP_ID, ML_CLIENT_SECRET, ML_REDIRECT_URI])
    if not tem_config_oauth:
        logging.warning(
            "Code capturado, mas faltam variáveis OAuth (ML_APP_ID, ML_CLIENT_SECRET, ML_REDIRECT_URI) para gerar token."
        )
        return web.Response(
            text=(
                "Code recebido e salvo, mas a troca por token não foi feita. "
                "Configure ML_APP_ID, ML_CLIENT_SECRET e ML_REDIRECT_URI no .env."
            )
        )

    try:
        token_data = await trocar_code_por_token(code)
        salvar_token_mercadolivre(token_data)
    except Exception as erro:
        logging.error("Code capturado, mas falhou a troca por token: %s", erro)
        return web.Response(
            status=500,
            text=(
                "Code recebido, mas falhou ao gerar token da API do Mercado Livre. "
                "Confira os logs."
            ),
        )

    logging.info("Token OAuth do Mercado Livre gerado e salvo com sucesso.")
    return web.Response(text="Autorização concluída com sucesso. Token salvo no servidor.")


async def iniciar_servidor_web():
    app = web.Application()
    app.router.add_get("/health", handler_health)
    app.router.add_get("/mercadolivre/callback", handler_ml_callback)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEB_SERVER_HOST, WEB_SERVER_PORT)
    await site.start()

    logging.info(
        "Servidor web ativo em http://%s:%s (callback: /mercadolivre/callback)",
        WEB_SERVER_HOST,
        WEB_SERVER_PORT,
    )
    return runner




# ==========================
# EXECUÇÃO
# ==========================


async def main():

    criar_banco()
    ciclo = 0
    ultima_publicacao = time.time()
    total_publicacoes = 0
    total_tentativas = 0
    ultima_status = "aguardando"
    historico = []

    runner = None
    if WEB_SERVER_ENABLED:
        try:
            runner = await iniciar_servidor_web()
        except Exception as erro:
            logging.error("Falha ao iniciar servidor web: %s", erro)
            return

    if not BOT_TOKEN or not CHAT_ID or manager is None:
        if WEB_SERVER_ENABLED:
            logging.warning(
                "Servidor OAuth ativo. Loop de promoções desativado porque BOT_TOKEN/CHAT_ID/ALI_KEY/ALI_SECRET não estão completos."
            )
            try:
                while True:
                    await asyncio.sleep(3600)
            finally:
                if runner is not None:
                    await runner.cleanup()
            return

        if not BOT_TOKEN or not CHAT_ID:
            logging.error("Configuração incompleta: defina BOT_TOKEN e CHAT_ID no arquivo .env antes de iniciar o bot.")
        if manager is None:
            logging.error("AliexpressApi não inicializado. Verifique ALI_KEY/ALI_SECRET e dependências.")
        return

    bot = Bot(
        token=BOT_TOKEN
    )

    try:
        while True:


            try:

                ciclo += 1
                total_tentativas += 1
                tempo_decorrido = time.time() - ultima_publicacao
                tempo_restante = max(0, INTERVALO - tempo_decorrido)

                imprimir_painel(
                    ciclo,
                    total_publicacoes,
                    total_tentativas,
                    tempo_restante,
                    tempo_decorrido,
                    ultima_status,
                    historico[-1] if historico else None,
                )


                termo = random.choice(termos)

                historico.append(f"Buscando: {termo}")
                if len(historico) > 5:
                    historico.pop(0)
                logging.info("🔎 Buscando: %s", termo)

                # coletar resultados de diferentes ordenações (vendas e popularidade)
                coletados = []
                for sort_mode in SEARCH_SORTS:
                    try:
                        if manager is None:
                            raise RuntimeError("Aliexpress manager não inicializado")
                        resposta = manager.get_products(
                            keywords=termo,
                            sort=sort_mode,
                            target_currency="BRL",
                            target_language="PT",
                            tracking_id=TRACKING_ID,
                        )
                    except Exception as e:
                        logging.warning("Aviso: falha na busca com sort=%s: %s", sort_mode, e)
                        resposta = None

                    if resposta and getattr(resposta, "products", None):
                        # guardar tuplas (produto, origem)
                        coletados.extend([(p, sort_mode) for p in resposta.products[:15]])

                # telemetria: contagem por modo
                contador_sort = {}
                for _, origem in coletados:
                    contador_sort[origem] = contador_sort.get(origem, 0) + 1
                logging.info("[telemetry] termo='%s' coletados=%d por_sort=%s", termo, len(coletados), contador_sort)
                # atualizar métricas agregadas
                for origem, count in contador_sort.items():
                    try:
                        incrementar_metricas(termo=termo, origem=origem, coletados_inc=count)
                    except Exception as e:
                        logging.warning("[telemetry] falha ao incrementar metricas: %s", e)

                # deduplicar por product_id mantendo ordem (priorizando VOLUME_DESC primeiro)
                vistos = set()
                produtos_unicos = []
                origem_map = {}
                for p, origem in coletados:
                    pid = getattr(p, "product_id", None)
                    if not pid or pid in vistos:
                        continue
                    vistos.add(pid)
                    produtos_unicos.append(p)
                    origem_map[getattr(p, "product_id")] = origem

                if produtos_unicos:

                    for produto in produtos_unicos[:30]:
                        # determinar contexto de busca para adaptar legenda
                        contexto_produto = origem_map.get(getattr(produto, "product_id"), "VOLUME_DESC")

                        produto = enriquecer_produto_com_detalhes(manager, produto)


                        id_produto = produto.product_id


                        if produto_existe(id_produto):

                            continue



                        if not pertence_nicho(produto):

                            continue



                        score = calcular_pontuacao(produto)


                        logging.info("Score: %s", score)


                        if score < 60:

                            continue



                        analise = analisar_produto(
                            preparar_produto(produto),
                            contexto=contexto_produto,
                        )


                        logging.debug("Analise: %s", analise)



                        if analise["aprovado"]:


                            imagem = colocar_logo(

                                produto.product_main_image_url

                            )


                            mensagem = criar_mensagem(

                                produto,

                                analise["legenda"]

                            )


                            ultima_status = "enviando"
                            enviado = await enviar_mensagem_segura(
                                bot,
                                CHAT_ID,
                                imagem,
                                mensagem,
                                ParseMode.HTML,
                            )

                            if not enviado:
                                ultima_status = "falha"
                                historico.append("Falha no envio")
                                if len(historico) > 5:
                                    historico.pop(0)
                                logging.warning("⚠️ Não foi possível enviar a promoção.")
                                continue

                            # salvar com telemetria: origem (sort_mode), termo e timestamp
                            salvar_produto(
                                produto.product_id,
                                produto.product_title,
                                produto.target_sale_price,
                                calcular_desconto(produto)[2],
                                analise["score"],
                                1,
                                origem=contexto_produto,
                                termo=termo,
                                busca_ts=int(time.time()),
                            )
                            try:
                                incrementar_metricas(termo=termo, origem=contexto_produto, publicados_inc=1)
                            except Exception as e:
                                logging.warning("[telemetry] falha ao incrementar metricas publicadas: %s", e)


                            ultima_publicacao = time.time()
                            total_publicacoes += 1
                            ultima_status = "publicado"
                            historico.append("Publicado com sucesso")
                            if len(historico) > 5:
                                historico.pop(0)
                            logging.info("✅ Publicado")
                            logging.info("[console] publicação feita, próxima em %s", formatar_tempo(INTERVALO))

                            break



            except Exception as erro:
                ultima_status = "erro"
                historico.append(f"Erro: {erro}")
                if len(historico) > 5:
                    historico.pop(0)
                logging.error("Erro: %s", erro)


            await asyncio.sleep(
                INTERVALO
            )
    finally:
        if runner is not None:
            await runner.cleanup()



if __name__ == "__main__":

    asyncio.run(main())
