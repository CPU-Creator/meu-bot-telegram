#!/usr/bin/env bash
set -e

SERVICE_NAME=promoradar-relatorio.service
SERVICE_FILE="systemd/$SERVICE_NAME"
TARGET="/etc/systemd/system/$SERVICE_NAME"

usage() {
  echo "Uso: sudo $0 /caminho/absoluto/do/repositorio usuario_do_servico"
}

if [ "$EUID" -ne 0 ]; then
  echo "Execute com sudo: sudo $0"
  exit 1
fi

if [ "$#" -ne 2 ]; then
  usage
  exit 1
fi

REPO_DIR="$1"
SERVICE_USER="$2"

if [ ! -f "$SERVICE_FILE" ]; then
  echo "Arquivo $SERVICE_FILE não encontrado"
  exit 1
fi

if [ ! -d "$REPO_DIR" ]; then
  echo "Diretório do repositório não encontrado: $REPO_DIR"
  exit 1
fi

sed \
  -e "s|__PROMORADAR_WORKDIR__|$REPO_DIR|g" \
  -e "s|__PROMORADAR_USER__|$SERVICE_USER|g" \
  "$SERVICE_FILE" > "$TARGET"
chmod 644 "$TARGET"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

echo "Serviço instalado e iniciado. Verifique status com: systemctl status $SERVICE_NAME"
