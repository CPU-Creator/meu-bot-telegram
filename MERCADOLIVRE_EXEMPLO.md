# Guia: Publicar Produtos do Mercado Livre com Link de Afiliado

Este guia mostra como configurar o bot para buscar produtos do Mercado Livre em nichos específicos e publicar no Telegram com seu link de afiliado.

## 1. Configuração Básica do Mercado Livre

Adicione ao seu `.env`:

```bash
# Habilitar Mercado Livre como fonte de produtos
ENABLE_MERCADOLIVRE=1

# Opcional: desabilitar AliExpress se quiser usar só ML
ENABLE_ALIEXPRESS=0

# Termos de busca (estes serão usados nas buscas)
TERMOS_BUSCA=mouse gamer,teclado mecanico,fone bluetooth,headset gamer,ssd nvme,memoria ram

# Palavras que definem seu nicho (só produtos com essas palavras serão publicados)
NICHO_PALAVRAS=mouse,teclado,fone,headset,ssd,ram,memoria

# Mercado Livre - Site ID (MLB = Brasil)
ML_SITE_ID=MLB

# Quantos produtos buscar por termo (máx 50)
ML_SEARCH_LIMIT=20
```

## 2. Configurar Link de Afiliado

O bot pode transformar a URL original do produto em um link seu, usando `ML_AFFILIATE_URL_TEMPLATE`.

### Opção A: Usar um encurtador ou redirect seu

Se você tiver um serviço que redireciona (ex: seu próprio domínio):

```bash
ML_AFFILIATE_URL_TEMPLATE=https://seu-dominio.com/r?destino={url_encoded}
```

O bot vai converter para algo como:
```
https://seu-dominio.com/r?destino=https%3A%2F%2Fwww.mercadolivre.com.br%2Fmouse-gamer-rgb-16000-dpi%2Fp%2FMLC123456
```

### Opção B: Adicionar parâmetro UTM (mais simples)

Se o Mercado Livre suporta UTM ou você quer rastrear cliques:

```bash
ML_AFFILIATE_URL_TEMPLATE={url}?utm_source=telegram&utm_medium=bot&utm_campaign=nichos
```

Resultado:
```
https://www.mercadolivre.com.br/mouse-gamer-rgb-16000-dpi/p/MLC123456?utm_source=telegram&utm_medium=bot&utm_campaign=nichos
```

### Opção C: Usar apenas a URL original (sem afiliado)

```bash
ML_AFFILIATE_URL_TEMPLATE={url}
```

## 3. Placeholders Disponíveis

Dentro do template você pode usar:

| Placeholder | Valor | Exemplo |
|-------------|-------|---------|
| `{url}` | URL original do produto | `https://mercadolivre.com.br/...` |
| `{url_encoded}` | URL encoded (para usar em query strings) | `https%3A%2F%2Fmercadolivre.com.br%2F...` |
| `{item_id}` | ID do item no Mercado Livre | `MLC123456` |
| `{term}` | Termo da busca | `mouse gamer` |
| `{term_encoded}` | Termo encoded | `mouse%20gamer` |

Exemplos avançados:

```bash
# Template com item_id
ML_AFFILIATE_URL_TEMPLATE=https://seu-dominio.com/ml/{item_id}

# Template com termo e URL
ML_AFFILIATE_URL_TEMPLATE=https://seu-dominio.com/r?termo={term_encoded}&url={url_encoded}
```

## 4. Fluxo de Funcionamento

1. **Busca**: A cada ciclo, o bot seleciona um termo aleatório de `TERMOS_BUSCA` e busca no Mercado Livre
2. **Filtro de Nicho**: Verifica se o título do produto contém alguma palavra de `NICHO_PALAVRAS`
3. **Validação**: Se passou no filtro, calcula score e faz análise com IA
4. **Transformação de Link**: Aplica o template `ML_AFFILIATE_URL_TEMPLATE` à URL original
5. **Publicação**: Envia para Telegram com a imagem, título, preço e link transformado

## 5. Exemplo de Configuração Completa

```bash
# Bot Telegram
BOT_TOKEN=seu_token_aqui
CHAT_ID=seu_chat_id_aqui

# Fontes
ENABLE_MERCADOLIVRE=1
ENABLE_ALIEXPRESS=0

# Busca
TERMOS_BUSCA=mouse gamer,teclado mecanico,fone bluetooth,headset gamer,ssd nvme,memoria ram ddr4

# Nicho (só esses produtos serão publicados)
NICHO_PALAVRAS=mouse,teclado,fone,headset,ssd,ram,memoria

# Mercado Livre
ML_SITE_ID=MLB
ML_SEARCH_LIMIT=20
ML_AFFILIATE_URL_TEMPLATE=https://seu-dominio.com/r?url={url_encoded}

# Outros
INTERVALO=300
OPENAI_API_KEY=seu_api_key_opcional
```

## 6. Testando Localmente

```bash
# Ativar ambiente
source .venv/bin/activate

# Criar .env a partir do exemplo
cp .env.example .env

# Editar .env com suas credenciais
nano .env

# Rodar o bot
python bot_promocoes.py
```

Você verá no terminal:
- ✅ Produtos encontrados no Mercado Livre
- ✅ Produtos filtrados por nicho
- ✅ Mensagens publicadas no Telegram com links transformados

## 7. Deploy no Railway

Se usar Railway (recomendado):

1. Conecte seu repositório GitHub
2. Configure as variáveis de ambiente via painel do Railway
3. O bot vai rodar continuamente
4. Você pode ver os logs em tempo real

Veja [DEPLOY.md](DEPLOY.md) para instruções completas.

## 8. Troubleshooting

**Problema**: Nenhum produto está sendo publicado
- Verifique se `ENABLE_MERCADOLIVRE=1`
- Confira se `NICHO_PALAVRAS` contém palavras que existem nos produtos
- Verifique os logs: `docker compose logs -f`

**Problema**: Produtos encontrados mas link de afiliado está quebrado
- Teste o template diretamente: `echo "https://seu-dominio.com/r?url=$(python3 -c "from urllib.parse import quote; print(quote('https://mercadolivre.com.br/...'))")"`
- Verifique se o seu serviço de redirect está respondendo

**Problema**: OAuth do Mercado Livre não está funcionando
- Certifique-se de ter `ML_APP_ID`, `ML_CLIENT_SECRET` e `ML_REDIRECT_URI` configurados
- Confirme que a URL de callback no painel ML é exatamente igual a `ML_REDIRECT_URI`

