import asyncio, random, logging, html, aiohttp, os
from telegram import Bot
from telegram.constants import ParseMode
# from aliexpress_api import AliexpressApi, models  # removed: package no longer installed

# Configurações usando Variáveis de Ambiente (para funcionar na nuvem)
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
ALI_KEY = os.getenv('ALI_KEY')
ALI_SECRET = os.getenv('ALI_SECRET')

# manager = AliexpressApi(ALI_KEY, ALI_SECRET, models.Language.PT, models.Currency.BRL, 'default')  # removed: aliexpress_api not installed

def formatar_mensagem(p):
    titulo = html.escape(getattr(p, 'product_title', 'Produto'))[:90]
    preco_atual = float(getattr(p, 'target_sale_price', 0))
    preco_antigo = float(getattr(p, 'original_price', preco_atual * 1.5))
    
    # Trava matemática: se o preço antigo for menor que o atual, corrigimos
    if preco_antigo <= preco_atual: preco_antigo = preco_atual * 1.4
    
    # Cálculo seguro de desconto (trava entre 0 e 95%)
    desconto = int(((preco_antigo - preco_atual) / preco_antigo) * 100)
    desconto = max(1, min(desconto, 95))
    
    # Trava de nota: garante que fique entre 1.0 e 5.0
    nota = float(getattr(p, 'nota_validada', 4.5))
    nota = max(1.0, min(nota, 5.0))
    
    link = getattr(p, 'promotion_link', f"https://pt.aliexpress.com/item/{getattr(p, 'product_id', '')}.html")
    
    return (f"🔥 <b>OFERTA DO DIA</b> 🔥\n\n📦 <b>{titulo}</b>\n\n"
            f"📉 De: <s>R$ {preco_antigo:.2f}</s>\n💰 Por: <b>R$ {preco_atual:.2f} ({desconto}% OFF)</b>\n"
            f"⭐ Avaliação: {nota:.1f}/5.0\n\n🛒 <a href='{link}'><b>👉 COMPRAR AGORA 👈</b></a>")

async def main():
    bot = Bot(token=BOT_TOKEN)
    termos = ['fone bluetooth', 'smartwatch', 'ssd nvme', 'mouse gamer', 'power bank']
    while True:
        # manager.get_products and dependent block removed: aliexpress_api not installed
        # termo = random.choice(termos)
        # produtos = manager.get_products(keywords=termo, sort='VOLUME_DESC', target_currency='BRL', target_language='PT')
        #
        # if produtos and hasattr(produtos, 'products') and produtos.products:
        #     p = produtos.products[0]
        #     # Normalização da nota antes de passar para a mensagem
        #     try:
        #         n = float(str(getattr(p, 'evaluate_rate', 4.5)).replace('%', ''))
        #         p.nota_validada = n/20 if n > 5 else n
        #     except: p.nota_validada = 4.5
        #
        #     # Envio
        #     try:
        #         async with aiohttp.ClientSession() as session:
        #             async with session.get(p.product_main_image_url) as resp:
        #                 await bot.send_photo(CHAT_ID, photo=await resp.read(), caption=formatar_mensagem(p), parse_mode=ParseMode.HTML)
        #     except: pass
        await asyncio.sleep(900)

if __name__ == "__main__":
    asyncio.run(main())
