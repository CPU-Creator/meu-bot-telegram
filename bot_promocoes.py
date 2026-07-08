import asyncio, random, logging, html, os
from telegram import Bot
from telegram.constants import ParseMode
from aliexpress_api import AliexpressApi, models

# Configuração de logs para ver erros na Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações via Variáveis de Ambiente
BOT_TOKEN = os.getenv('BOT_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
ALI_KEY = os.getenv('ALI_KEY')
ALI_SECRET = os.getenv('ALI_SECRET')

# Inicialização da API
manager = AliexpressApi(ALI_KEY, ALI_SECRET, models.Language.PT, models.Currency.BRL, 'default')

def formatar_mensagem(p):
    titulo = html.escape(getattr(p, 'product_title', 'Produto'))[:90]
    preco_atual = float(getattr(p, 'target_sale_price', 0))
    preco_antigo = float(getattr(p, 'original_price', preco_atual * 1.5))
    
    # Trava matemática
    if preco_antigo <= preco_atual: preco_antigo = preco_atual * 1.4
    desconto = int(((preco_antigo - preco_atual) / preco_antigo) * 100)
    desconto = max(1, min(desconto, 95))
    
    # Validação segura da nota
    try:
        nota = float(str(getattr(p, 'evaluate_rate', 4.5)).replace('%', ''))
        if nota > 5: nota /= 20
        nota = max(1.0, min(nota, 5.0))
    except: nota = 4.5
    
    link = getattr(p, 'promotion_link', f"https://pt.aliexpress.com/item/{getattr(p, 'product_id', '')}.html")
    
    return (f"🔥 <b>OFERTA DO DIA</b> 🔥\n\n📦 <b>{titulo}</b>\n\n"
            f"📉 De: <s>R$ {preco_antigo:.2f}</s>\n💰 Por: <b>R$ {preco_atual:.2f} ({desconto}% OFF)</b>\n"
            f"⭐ Avaliação: {nota:.1f}/5.0\n\n🛒 <a href='{link}'><b>👉 COMPRAR AGORA 👈</b></a>")

async def main():
    bot = Bot(token=BOT_TOKEN)
    termos = ['fone bluetooth', 'smartwatch', 'ssd nvme', 'mouse gamer', 'power bank']
    
    logger.info("Bot iniciado com sucesso!")
    
    while True:
        try:
            termo = random.choice(termos)
            produtos = manager.get_products(keywords=termo, sort='VOLUME_DESC', target_currency='BRL', target_language='PT')
            
            if produtos and hasattr(produtos, 'products') and produtos.products:
                p = produtos.products[0]
                # Envio direto via URL (mais estável)
                await bot.send_photo(
                    chat_id=CHAT_ID, 
                    photo=p.product_main_image_url, 
                    caption=formatar_mensagem(p), 
                    parse_mode=ParseMode.HTML
                )
                logger.info(f"Oferta enviada: {p.product_title}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar oferta: {e}")
            
        await asyncio.sleep(900) # Aguarda 15 minutos

if __name__ == "__main__":
    asyncio.run(main())
