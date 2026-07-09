#!/usr/bin/env bash
set -euo pipefail

# Script de deploy local usando docker-compose.
# Uso: ./scripts/deploy_docker.sh /caminho/para/projeto

ROOT_DIR=${1:-$(pwd)}
cd "$ROOT_DIR"

if [ ! -f Dockerfile ]; then
  echo "Dockerfile não encontrado em $ROOT_DIR"
  exit 1
fi

if [ ! -f .env ]; then
  echo ".env não encontrado — copie .env.example para .env e preencha as variáveis." 
  exit 2
fi

docker build -t promoradar:latest .

docker-compose pull || true

docker-compose up -d --build

echo "Deploy iniciado. Verifique logs com: docker-compose logs -f"
