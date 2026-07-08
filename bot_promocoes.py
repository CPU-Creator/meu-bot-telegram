import asyncio
import random
import logging
import html
import aiohttp
from telegram import Bot
from telegram.constants import ParseMode
from aliexpress_api import AliexpressApi, models

# --- CONFIGURAÇÕES ---
BOT_TOKEN = 'BOT_TOKEN'
CHAT_ID = 'CHAT_ID'
ALI_KEY = 'ALI_KEY'
ALI_SECRET = 'ALI_SECRET'

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self):
        self.aliexpress = AliexpressApi(ALI_KEY, ALI_SECRET, models.Language.PT, models.Currency.BRL, 'default')

    def formatar_mensagem(self, p):
        titulo = html.escape(getattr(p, 'product_title', 'Produto'))[:90]
        preco_atual = float(getattr(p, 'target_sale_price', 0))
        preco_antigo = float(getattr(p, 'original_price', preco_atual * 1.5))
        if preco_antigo <= preco_atual: preco_antigo = preco_atual * 1.3
        desconto = int(((preco_antigo - preco_atual) / preco_antigo) * 100)
        link = getattr(p, 'promotion_link', f"https://pt.aliexpress.com/item/{getattr(p, 'product_id', '')}.html")
        nota = getattr(p, 'nota_validada', 4.5)
        
        return (f"🔥 <b>OFERTA DO DIA</b> 🔥\n\n"
                f"📦 <b>Produto:</b> {titulo}...\n\n"
                f"📉 <b>De:</b> <s>R$ {preco_antigo:.2f}</s>\n"
                f"💰 <b>Por:</b> <b>R$ {preco_atual:.2f} ({desconto}% OFF)</b>\n"
                f"⭐ <b>Avaliação:</b> {nota:.1f}/5.0\n\n"
                f"🛒 <a href='{link}'><b>👉 COMPRAR AGORA 👈</b></a>")

    async def enviar_foto(self, bot, chat_id, p, legenda):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(p.product_main_image_url) as resp:
                    data = await resp.read()
            await bot.send_photo(chat_id=chat_id, photo=data, caption=legenda, parse_mode=ParseMode.HTML)
        except Exception as e:
            logger.error(f"Erro no envio da foto: {e}")

manager = BotManager()

def buscar_oferta_segura(termo):
    try:
        # A busca agora é protegida contra resultados vazios
        produtos = manager.aliexpress.get_products(
            keywords=termo, sort='VOLUME_DESC', target_currency='BRL', target_language='PT'
        )
        
        # VERIFICAÇÃO CRÍTICA: Se não houver 'products' ou a lista for vazia, retorna None
        if not produtos or not hasattr(produtos, 'products') or not produtos.products:
            logger.warning(f"Nenhum produto encontrado para o termo: {termo}")
            return None

        # Filtra apenas o primeiro produto válido
        for p in produtos.products:
            preco = float(getattr(p, 'target_sale_price', 0))
            if preco <= 0.01: continue
            
            try:
                raw_val = str(getattr(p, 'evaluate_rate', '0')).replace('%', '').strip()
                nota = float(raw_val)
                if nota > 5.0: nota /= 20.0
                if nota > 5.0: nota = 5.0
                if nota < 3.0: continue
            except:
                nota = 4.5
            
            p.nota_validada = nota
            return p
            
        return None # Nenhum produto passou nos filtros de preço/nota
        
    except Exception as e:
        logger.warning(f"Erro na busca: {e}")
        return None

async def main():
    bot = Bot(token=BOT_TOKEN)
    termos = [
        'fone ouvido bluetooth', 'smartwatch amazfit', 'carregador gan 65w', 
        'power bank', 'cartao sd', 'pendrive', 'webcam', 'ssd nvme', 
        'memoria ram', 'mouse gamer', 'teclado mecanico', 'suporte monitor', 
        'lampada inteligente', 'interruptor wifi', 'sensor presenca', 
        'controle infravermelho', 'fechadura digital'
    ]
    
    while True:
        termo = random.choice(termos)
        p = await asyncio.to_thread(buscar_oferta_segura, termo)
        
        if p:
            logger.info(f"Sucesso: {termo}")
            msg = manager.formatar_mensagem(p)
            await manager.enviar_foto(bot, CHAT_ID, p, msg)
        
        await asyncio.sleep(900) 

if __name__ == "__main__":
    asyncio.run(main())
