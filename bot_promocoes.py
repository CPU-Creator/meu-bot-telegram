
import asyncio
import random
import html
import os
import time
import shutil
import sys
import logging

from PIL import Image

from dotenv import load_dotenv

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

# inicializar cliente da AliExpress (tentar assinaturas comuns)
try:
    manager = AliexpressApi(api_key=ALI_KEY, api_secret=ALI_SECRET)
except TypeError:
    try:
        manager = AliexpressApi(ALI_KEY, ALI_SECRET)
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

        base = Image.open(imagem).convert("RGBA")
        logo = Image.open(LOGO).convert("RGBA")
        logo.thumbnail((150, 150))
        base.paste(logo, (20, 20), logo)
        arquivo = "produto_promoradar.png"
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

    # extrair possível cupom legível
    cupom_text = None
    for key in ("coupon_code", "coupon", "discount_coupon", "coupon_info"):
        if hasattr(produto, key):
            val = getattr(produto, key)
            if isinstance(val, dict):
                # tentar extrair código e valor
                code = val.get("code") or val.get("coupon_code") or val.get("name")
                amount = val.get("amount") or val.get("discount")
                if code:
                    cupom_text = f"{code}"
                    if amount:
                        cupom_text += f" (-{amount})"
                    break
            else:
                cupom_text = str(val)
                break

    # extrair parcelamento (tentar formatos comuns)
    parcelas_text = None
    for key in ("installments", "installment_info", "pay_installment", "max_installment"):
        if hasattr(produto, key):
            val = getattr(produto, key)
            if isinstance(val, dict):
                n = val.get("count") or val.get("max") or val.get("number")
                v = val.get("value") or val.get("per_installment")
                juros = val.get("interest") or val.get("has_interest")
                if n and v:
                    parcelas_text = f"até {n}x de R$ {float(v):.2f} {'com juros' if juros else 'sem juros'}"
                    break
            elif isinstance(val, (list, tuple)) and val:
                # lista de opções
                try:
                    opt = val[0]
                    n = getattr(opt, "count", None) or opt.get("count") if isinstance(opt, dict) else None
                    v = getattr(opt, "value", None) or opt.get("value") if isinstance(opt, dict) else None
                    if n and v:
                        parcelas_text = f"até {n}x de R$ {float(v):.2f}"
                        break
                except Exception:
                    pass
            else:
                parcelas_text = str(val)
                break



    msg = f"""

🔥 <b>PROMORADAR</b> 🔥


📦 <b>{titulo}</b>


{legenda}


📉 De:

<s>R$ {antigo:.2f}</s>


💰 Por:

<b>R$ {atual:.2f}</b>


🔥 <b>{desconto}% OFF</b>


🛒 Comprar:

<a href="{link}">
👉 CLIQUE AQUI
</a>

"""

    # anexar cupom e parcelamento visíveis quando disponíveis
    extras = []
    if cupom_text:
        extras.append(f"🎟️ Cupom: {cupom_text}")
    if parcelas_text:
        extras.append(f"💳 Parcelamento: {parcelas_text}")

    if extras:
        msg = msg + "\n" + "\n".join(extras) + "\n\n"

    return msg




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

    if not BOT_TOKEN or not CHAT_ID:
        logging.error("Configuração incompleta: defina BOT_TOKEN e CHAT_ID no arquivo .env antes de iniciar o bot.")
        return

    if manager is None:
        logging.error("AliexpressApi não inicializado. Verifique ALI_KEY/ALI_SECRET e dependências.")
        return

    bot = Bot(
        token=BOT_TOKEN
    )


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



if __name__ == "__main__":

    asyncio.run(main())
