#!/usr/bin/env bash
set -e

SERVICE_NAME=promoradar-relatorio.service
SERVICE_FILE="systemd/$SERVICE_NAME"
TARGET="/etc/systemd/system/$SERVICE_NAME"

if [ "$EUID" -ne 0 ]; then
  echo "Execute com sudo: sudo $0"
  exit 1
fi

if [ ! -f "$SERVICE_FILE" ]; then
  echo "Arquivo $SERVICE_FILE não encontrado"
  exit 1
fi

cp "$SERVICE_FILE" "$TARGET"
chmod 644 "$TARGET"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

echo "Serviço instalado e iniciado. Verifique status com: systemctl status $SERVICE_NAME"
