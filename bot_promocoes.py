import asyncio
import random
import html
import os

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
    salvar_produto
)


load_dotenv()


# ==========================
# CONFIGURAÇÕES
# ==========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

CHAT_ID = os.getenv("CHAT_ID")


ALI_KEY = os.getenv("ALI_KEY")

ALI_SECRET = os.getenv("ALI_SECRET")

TRACKING_ID = os.getenv(
    "TRACKING_ID"
)


LOGO = "logo_promoradar.png"


INTERVALO = 720



# ==========================
# ALIEXPRESS
# ==========================


manager = AliexpressApi(

    ALI_KEY,

    ALI_SECRET,

    models.Language.PT,

    models.Currency.BRL,

    TRACKING_ID

)



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

"""



# ==========================
# LOGO NA IMAGEM
# ==========================


def colocar_logo(imagem):

    if not os.path.exists(LOGO):

        return imagem


    base = Image.open(
        imagem
    ).convert(
        "RGBA"
    )


    logo = Image.open(
        LOGO
    ).convert(
        "RGBA"
    )


    logo.thumbnail(
        (150,150)
    )


    base.paste(

        logo,

        (20,20),

        logo

    )


    arquivo = "produto_promoradar.png"


    base.save(
        arquivo
    )


    return arquivo



# ==========================
# MENSAGEM
# ==========================


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


    return f"""

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



# ==========================
# EXECUÇÃO
# ==========================


async def main():

    criar_banco()


    bot = Bot(
        token=BOT_TOKEN
    )


    while True:


        try:

            termo = random.choice(
                termos
            )


            print(
                f"🔎 Buscando: {termo}"
            )


            resposta = manager.get_products(

                keywords=termo,

                sort="VOLUME_DESC",

                target_currency="BRL",

                target_language="PT",

                tracking_id=TRACKING_ID

            )


            if resposta and resposta.products:


                for produto in resposta.products[:10]:


                    id_produto = produto.product_id


                    if produto_existe(id_produto):

                        continue



                    if not pertence_nicho(produto):

                        continue



                    score = calcular_pontuacao(produto)


                    print(
                        "Score:",
                        score
                    )


                    if score < 60:

                        continue



                    analise = analisar_produto(

                        preparar_produto(produto)

                    )


                    print(
                        analise
                    )



                    if analise["aprovado"]:


                        imagem = colocar_logo(

                            produto.product_main_image_url

                        )


                        mensagem = criar_mensagem(

                            produto,

                            analise["legenda"]

                        )


                        await bot.send_photo(

                            chat_id=CHAT_ID,

                            photo=imagem,

                            caption=mensagem,

                            parse_mode=ParseMode.HTML

                        )


                        salvar_produto(

                            produto.product_id,

                            produto.product_title,

                            produto.target_sale_price,

                            calcular_desconto(produto)[2],

                            analise["score"],

                            1

                        )


                        print(
                            "✅ Publicado"
                        )


                        break



        except Exception as erro:

            print(
                "Erro:",
                erro
            )


        await asyncio.sleep(
            INTERVALO
        )



if __name__ == "__main__":

    asyncio.run(main())
