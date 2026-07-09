#!/bin/bash

# Setup Rápido - meu-bot-telegram
# Este script ajuda a configurar o bot rapidamente para produção

set -e

echo "============================================================"
echo "🚀 SETUP RÁPIDO - MEU-BOT-TELEGRAM"
echo "============================================================"
echo ""

# Verificar se está no diretório certo
if [ ! -f "bot_promocoes.py" ]; then
    echo "❌ Erro: Execute este script na raiz do repositório"
    exit 1
fi

echo "1️⃣ Verificando dependências..."
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker não encontrado. Instale em: https://docs.docker.com/get-docker/"
else
    echo "✅ Docker encontrado"
fi

echo ""
echo "2️⃣ Criando arquivo .env local (se não existir)..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✅ Arquivo .env criado a partir de .env.example"
    echo "   IMPORTANTE: Edite .env e configure BOT_TOKEN e CHAT_ID"
else
    echo "ℹ️  Arquivo .env já existe"
fi

echo ""
echo "3️⃣ Testando imagem Docker..."
if docker image inspect ghcr.io/cpu-creator/meu-bot-telegram:latest > /dev/null 2>&1; then
    echo "✅ Imagem Docker publicada está acessível"
else
    echo "⚠️  Imagem não encontrada localmente, será baixada no primeiro docker run"
fi

echo ""
echo "4️⃣ Validando configuração..."
python3 << 'VALIDATE'
import os
import sys

required = ["BOT_TOKEN", "CHAT_ID"]
env_file = ".env"

try:
    with open(env_file) as f:
        config = {}
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, val = line.split("=", 1)
                config[key.strip()] = val.strip()
    
    missing = [k for k in required if not config.get(k)]
    
    if missing:
        print(f"⚠️  Variáveis não configuradas: {', '.join(missing)}")
        print("   Edite .env e configure essas variáveis antes de rodar")
    else:
        print("✅ Configuração básica OK")
        
except Exception as e:
    print(f"⚠️  Erro ao validar: {e}")

VALIDATE

echo ""
echo "5️⃣ Instruções para deploy:"
echo "============================================================"
echo ""
echo "📌 LOCAL (desenvolvimento):"
echo "   1. Edite .env com BOT_TOKEN e CHAT_ID"
echo "   2. pip install -r requirements.txt"
echo "   3. python bot_promocoes.py"
echo ""
echo "🚀 RAILWAY (recomendado para produção):"
echo "   1. Entre em https://railway.app"
echo "   2. Novo projeto > Connect GitHub > meu-bot-telegram"
echo "   3. Configure as variáveis de ambiente (copie de .env.production)"
echo "   4. Deploy automático em push"
echo ""
echo "🐳 DOCKER COMPOSE:"
echo "   1. Edite .env com credenciais"
echo "   2. docker-compose up -d"
echo ""
echo "============================================================"
echo ""
echo "📖 Documentação:"
echo "   - README.md: Visão geral e configuração"
echo "   - MERCADOLIVRE_EXEMPLO.md: Guia de publicação com nichos"
echo "   - DEPLOY.md: Opções de deploy"
echo ""
echo "✅ Setup concluído!"
echo "============================================================"
