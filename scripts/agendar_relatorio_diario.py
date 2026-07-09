#!/usr/bin/env python3
import os
import time
import datetime
import logging
from memoria import obter_metricas
from telegram import Bot


LOG = logging.getLogger("agendar_relatorio")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def enviar_relatorio(bot: Bot, dest: str, date: str = None, termo: str = None, origem: str = None):
    from scripts.relatorio_metricas import format_relatorio  # reutiliza formatação

    rows = obter_metricas(data=date, termo=termo, origem=origem)
    texto = format_relatorio(rows)
    texto = texto[:4000]
    bot.send_message(chat_id=dest, text=texto)


def chat_eh_promoradar(bot: Bot, dest: str) -> bool:
    try:
        chat = bot.get_chat(dest)
        title = getattr(chat, "title", "") or getattr(chat, "username", "") or ""
        return "promoradar" in title.lower()
    except Exception:
        return False


def proximo_timestamp(hora_min_str: str) -> float:
    now = datetime.datetime.now()
    h, m = map(int, hora_min_str.split(":"))
    alvo = now.replace(hour=h, minute=m, second=0, microsecond=0)
    if alvo <= now:
        alvo = alvo + datetime.timedelta(days=1)
    return alvo.timestamp()


def main():
    hora = os.getenv("DAILY_REPORT_HOUR", "09:00")
    target = os.getenv("REPORT_TARGET", "admin")  # admin ou chat

    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        LOG.error("BOT_TOKEN não definido")
        return 2

    bot = Bot(token=bot_token)

    dest = os.getenv("ADMIN_CHAT_ID") if target == "admin" else os.getenv("CHAT_ID")
    if not dest:
        LOG.error("Destino não configurado (ADMIN_CHAT_ID ou CHAT_ID)")
        return 2

    LOG.info("Agendador iniciado: horário=%s target=%s dest=%s", hora, target, dest)

    while True:
        ts = proximo_timestamp(hora)
        segundos = max(0, ts - time.time())
        LOG.info("Próximo envio em %s (em %ds)", datetime.datetime.fromtimestamp(ts).isoformat(), int(segundos))
        time.sleep(segundos)

        try:
            if chat_eh_promoradar(bot, dest):
                LOG.warning("Destino identificado como PromoRadar — pulando envio para evitar canal.")
            else:
                LOG.info("Enviando relatório para %s", dest)
                enviar_relatorio(bot, dest)
                LOG.info("Envio concluído")
        except Exception as e:
            LOG.exception("Falha ao enviar relatório: %s", e)


if __name__ == "__main__":
    main()
