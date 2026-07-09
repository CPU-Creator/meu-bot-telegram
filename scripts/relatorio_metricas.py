#!/usr/bin/env python3
import argparse
import sys
import logging
from memoria import obter_metricas

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def main():
    parser = argparse.ArgumentParser(description="Relatório de métricas de buscas")
    parser.add_argument("--date", help="Data no formato YYYY-MM-DD (padrão: hoje)")
    parser.add_argument("--termo", help="Filtrar por termo")
    parser.add_argument("--origem", help="Filtrar por origem (VOLUME_DESC|POPULARITY_DESC)")
    args = parser.parse_args()

    rows = obter_metricas(data=args.date, termo=args.termo, origem=args.origem)
    if not rows:
        logging.info("Nenhuma métrica encontrada para os filtros fornecidos.")
        return 0

    logging.info("%s", f"{'date':<12} {'termo':<30} {'origem':<16} {'coletados':>10} {'publicados':>10}")
    logging.info("%s", "-" * 80)
    for date, termo, origem, coletados, publicados in rows:
        logging.info("%s", f"{date:<12} {termo[:30]:<30} {origem:<16} {coletados:>10} {publicados:>10}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
