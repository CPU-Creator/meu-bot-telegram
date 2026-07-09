# 🚀 PromoRadar - Setup Completo

## O Que Foi Feito

### ✅ Arquitetura Multi-Plataforma Criada

```
PromoRadar
├── sources/
│   ├── base.py              # Classes base (ProdutoBase, ScraperBase)
│   ├── manager.py           # ProdutoManager (coordena múltiplas fontes)
│   ├── shopee.py            # Scraper Shopee Brasil
│   ├── kabum.py             # Scraper Kabum
│   ├── pichau.py            # Scraper Pichau
│   ├── terabyte.py          # Scraper Terabyte
│   ├── aliexpress.py        # Adapter AliExpress
│   └── mercadolivre.py      # Adapter Mercado Livre
├── bot_promoradar.py        # Bot multi-plataforma
└── bot_promocoes.py         # Bot original (ainda funciona)
```

### 📦 Plataformas Integradas

| Plataforma | Status | Afiliado |
|-----------|--------|---------|
| **Shopee** | ✅ Ativa | Sim |
| **Kabum** | ✅ Setup | Sim |
| **Pichau** | ✅ Setup | Sim |
| **Terabyte** | ✅ Setup | Sim |
| **AliExpress** | ✅ Integrada | Sim |
| **Mercado Livre** | ✅ Integrada | Sim |

### 🔗 Links de Afiliado

Todos os scrapers suportam template de afiliado:
```
ML_AFFILIATE_URL_TEMPLATE={url}?utm_source=telegram&utm_campaign=bot
```

Placeholders disponíveis:
- `{url}` - URL original
- `{url_encoded}` - URL codificada
- `{item_id}` - ID do produto
- `{term}` - Termo de busca
- `{term_encoded}` - Termo codificado

---

## 🎯 Como Usar

### Opção 1: Bot Original (Mantém Compatibilidade)
```bash
python bot_promocoes.py
```

### Opção 2: PromoRadar Multi-Plataforma (RECOMENDADO)
```bash
python bot_promoradar.py
```

---

## 📋 Configuração (.env)

```ini
# Telegram
BOT_TOKEN=seu_token
CHAT_ID=-1004496554566
CANAL_PROMORADAR=-1004496554566

# Plataformas
ENABLE_MERCADOLIVRE=1
ENABLE_ALIEXPRESS=1
TERMOS_BUSCA=mouse game,teclado mecânico,tablet,vídeo game,PC,ssd,HD,fone de ouvido

# Afiliado
ML_AFFILIATE_URL_TEMPLATE={url}?utm_source=telegram&utm_campaign=bot

# IA (Opcional)
ENABLE_OPENAI=0
OPENAI_API_KEY=sua_key
```

---

## 🚀 Deploy no Railway

1. **Acesse:** https://railway.app
2. **Novo Projeto** → GitHub → `meu-bot-telegram`
3. **Variables** → Adicione:
   ```
   BOT_TOKEN = seu_token
   CANAL_PROMORADAR = -1004496554566
   TERMOS_BUSCA = seu_termos
   ML_AFFILIATE_URL_TEMPLATE = {url}?utm_source=telegram&utm_campaign=bot
   ```
4. **Deploy** → Automático!

> Para trocar entre bots, edite `railway.toml`:
> ```yaml
> startCommand="python bot_promoradar.py"  # Multi-plataforma
> ```

---

## 🔍 Como Funciona

### Fluxo de Execução

```
PromoRadar inicia
    ↓
Setup scrapers (Shopee, Kabum, Pichau, Terabyte, AliExpress, ML)
    ↓
Para cada termo de busca:
    ├─ Shopee busca em paralelo
    ├─ Kabum busca em paralelo
    ├─ Pichau busca em paralelo
    ├─ Terabyte busca em paralelo
    ├─ AliExpress busca em paralelo
    └─ Mercado Livre busca em paralelo
    ↓
Consolidar resultados (todos os produtos)
    ↓
Ordenar por relevância/desconto
    ↓
Publicar top 5 no Telegram
    ↓
Aguardar próximo ciclo
```

### Estrutura de Mensagem

```
🚀 MOUSE GAMER RGB

💵 R$ 149,90 (-50%)
🏪 Shopee
🔗 https://shopee.com.br/...?utm_source=telegram&utm_campaign=bot
```

---

## 🛠️ Desenvolvimentos Futuros

- [ ] Web scraping completo para Kabum, Pichau, Terabyte
- [ ] Deduplicação inteligente multi-plataforma
- [ ] Dashboard com estatísticas
- [ ] Amazon (API paga)
- [ ] Integração com mais plataformas

---

## 📊 Status Atual

- ✅ Estrutura modular pronta
- ✅ Links de afiliado em todos
- ✅ Gerenciador de múltiplas fontes
- ✅ Bot teste criado
- ✅ Pronto para deploy

**Próximo passo:** Deploy no Railway e testar com dados reais!

---

**Criado em:** 2026-07-09  
**Versão:** 1.0.0 Multi-Plataforma
