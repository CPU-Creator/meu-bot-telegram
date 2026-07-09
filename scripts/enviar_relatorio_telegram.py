#!/usr/bin/env python3
import os
import sys
import argparse
import logging
from telegram import Bot
from memoria import obter_metricas

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def format_relatorio(rows):
    if not rows:
        return "Nenhuma métrica encontrada."
    out = []
    header = f"{'date':<12} {'termo':<30} {'origem':<16} {'coletados':>10} {'publicados':>10}"
    out.append(header)
    out.append('-' * len(header))
    for date, termo, origem, coletados, publicados in rows:
        out.append(f"{date:<12} {termo[:30]:<30} {origem:<16} {coletados:>10} {publicados:>10}")
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description='Enviar relatório de métricas por Telegram')
    parser.add_argument('--date', help='Data no formato YYYY-MM-DD (padrão: hoje)')
    parser.add_argument('--termo', help='Filtrar por termo')
    parser.add_argument('--origem', help='Filtrar por origem (VOLUME_DESC|POPULARITY_DESC)')
    parser.add_argument('--target', choices=['admin', 'chat'], default='admin', help='Destino: admin (ADMIN_CHAT_ID) ou chat (CHAT_ID)')
    args = parser.parse_args()

    bot_token = os.getenv('BOT_TOKEN')
    if not bot_token:
        logging.error('BOT_TOKEN não definido no ambiente')
        return 2

    bot = Bot(token=bot_token)

    if args.target == 'admin':
        dest = os.getenv('ADMIN_CHAT_ID')
    else:
        dest = os.getenv('CHAT_ID')

    if not dest:
        logging.error('Destino não configurado (defina ADMIN_CHAT_ID ou CHAT_ID conforme --target)')
        return 2

    # verificar se o chat tem título que indique o canal PromoRadar
    try:
        chat = bot.get_chat(dest)
        title = getattr(chat, 'title', '') or getattr(chat, 'username', '') or ''
        if 'promoradar' in title.lower():
            logging.error('Abortando: destino é o canal PromoRadar. Não será enviado para lá.')
            return 3
    except Exception as e:
        logging.error('Falha ao obter informações do chat: %s', e)
        return 2

    rows = obter_metricas(data=args.date, termo=args.termo, origem=args.origem)
    texto = format_relatorio(rows)

    # limitar tamanho
    texto = texto[:4000]

    try:
        bot.send_message(chat_id=dest, text=texto)
        logging.info('Relatório enviado com sucesso.')
        return 0
    except Exception as e:
        logging.error('Falha ao enviar relatório: %s', e)
        return 1


if __name__ == '__main__':
    sys.exit(main())
