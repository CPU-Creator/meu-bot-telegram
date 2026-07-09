# 🚀 SEU BOT ESTÁ PRONTO PARA DEPLOY

## ⚠️ AVISO DE SEGURANÇA IMPORTANTE

Seu arquivo `.env` local contém credenciais sensíveis:
- ✓ BOT_TOKEN (Telegram)
- ✓ OPENAI_API_KEY
- ✓ ALI_KEY e ALI_SECRET

**AÇÕES RECOMENDADAS:**

1. **Regenerar credenciais por segurança:**
   - BOT_TOKEN: Entre em @BotFather e gere novo token
   - OPENAI_API_KEY: Entre em https://platform.openai.com/api-keys e regenere
   - ALI_KEY/ALI_SECRET: Regenere em sua conta AliExpress

2. **Nunca committar .env:**
   - ✓ Já está em `.gitignore` (protegido)
   - O arquivo `.env.production` é um template seguro para copiar

3. **No Railway/Servidor:**
   - Configure variáveis de ambiente via painel (não em arquivo)
   - Use secrets seguros da plataforma

---

## 📋 CONFIGURAÇÃO ATUAL (Nicho: TECNOLOGIA)

```
BOT_TOKEN:              ✓ Configurado
CHAT_ID:                -1004496554566
ENABLE_MERCADOLIVRE:    1 (ATIVADO)
ENABLE_ALIEXPRESS:      0 (desativado)

NICHOS:
  mouse, teclado, tablet, game, pc, ssd, hd, fone,
  celular, periféricos, controle, gabinete, placa,
  processador, processadores, pad

TERMOS DE BUSCA:
  mouse game, teclado mecânico, tablet, vídeo game, PC,
  ssd, HD, fone de ouvido, celular, periféricos game,
  controles game, gabinete, placa mãe, processadores,
  mouse pad

LINK DE AFILIADO:
  {url}?utm_source=telegram&utm_campaign=bot
```

---

## 🎯 PRÓXIMOS PASSOS

### OPÇÃO A: Testar Localmente (RECOMENDADO PRIMEIRO)

```bash
# 1. Ativar ambiente Python
source .venv/bin/activate

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Rodar bot (teste de 1-2 minutos)
timeout 120 python bot_promocoes.py

# 4. Verificar logs
# - Bot deve buscar produtos do Mercado Livre
# - Filtrar por nicho (tecnologia)
# - Tentar publicar no Telegram
```

### OPÇÃO B: Deploy no Railway (RECOMENDADO PARA PRODUÇÃO)

```bash
# 1. Acesse https://railway.app
# 2. Novo Projeto > Connect GitHub > CPU-Creator/meu-bot-telegram
# 3. Adicione variáveis no painel (copie de .env):
#    - BOT_TOKEN
#    - CHAT_ID
#    - ENABLE_MERCADOLIVRE
#    - TERMOS_BUSCA
#    - NICHO_PALAVRAS
#    - ML_AFFILIATE_URL_TEMPLATE
# 4. Deploy automático em cada push!
```

### OPÇÃO C: Docker Local

```bash
docker-compose up -d
docker-compose logs -f
```

---

## 📊 VERIFICAÇÃO RÁPIDA

### 1. Bot consegue se conectar ao Telegram?
- Vai mostrar: `Telegram Bot iniciado!`

### 2. Bot consegue buscar do Mercado Livre?
- Vai mostrar: `[telemetry] termo='X' coletados=N`

### 3. Bot filtra por nicho?
- Vai mostrar: `Score: X.X` (produtos aprovados)

### 4. Bot publica mensagens?
- Vai aparecer uma mensagem no seu grupo/canal do Telegram

---

## 🔗 RECURSOS DISPONÍVEIS

- `/health` - Healthcheck do bot
- `/mercadolivre/callback` - OAuth callback (se configurar)
- Logs contínuos com telemetria
- Banco de dados SQLite (`promocoes.db`)

---

## 📞 SUPORTE

- **README.md**: Visão geral do projeto
- **MERCADOLIVRE_EXEMPLO.md**: Guia detalhado de nichos
- **DEPLOY.md**: Todas as opções de deploy
- **setup.sh**: Script de setup automático

---

## ✅ RESUMO

Seu bot está **100% pronto** com:
- ✓ Mercado Livre habilitado
- ✓ Nicho Tecnologia configurado  
- ✓ 15 termos de busca definidos
- ✓ Link de afiliado com UTM
- ✓ Docker/Railway preparado
- ✓ Testes validados

**Próximo passo:** Escolha sua opção de deploy acima e execute!

---

**Data:** 2026-07-09  
**Status:** 🟢 PRONTO PARA DEPLOY
