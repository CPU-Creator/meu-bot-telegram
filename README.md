# meu-bot-telegram

## Configuração

1. Copie o arquivo .env.example para .env.
2. Preencha as variáveis com suas credenciais.
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Inicie o bot:
   ```bash
   python bot_promocoes.py
   ```

## Captura da API do Mercado Livre (OAuth)

O bot sobe um pequeno servidor HTTP para receber o callback OAuth do Mercado Livre e trocar o `code` pelo token da API automaticamente.

- Endpoint de callback: `/mercadolivre/callback`
- Healthcheck: `/health`

Variáveis relevantes no `.env`:

- `WEB_SERVER_ENABLED` (padrão: `1`)
- `WEB_SERVER_HOST` (padrão: `0.0.0.0`)
- `WEB_SERVER_PORT` (padrão: `8080`)
- `ML_CODE_FILE` (padrão: `mercadolivre_code.jsonl`)
- `ML_TOKEN_FILE` (padrão: `mercadolivre_token.json`)
- `ML_APP_ID`
- `ML_CLIENT_SECRET`
- `ML_REDIRECT_URI`

Exemplo de URL de redirect para configurar no app do Mercado Livre:

```text
http://SEU_DOMINIO_OU_IP:8080/mercadolivre/callback
```

Quando o Mercado Livre redirecionar com `?code=...`, o valor será salvo no arquivo definido em `ML_CODE_FILE`.

Se `ML_APP_ID`, `ML_CLIENT_SECRET` e `ML_REDIRECT_URI` estiverem configurados, o bot também troca esse `code` por token e salva o resultado em `ML_TOKEN_FILE`.

## Testes e validação

- Rodar testes unitários:

```bash
PYTHONPATH=. pytest -q
```

- Testar parsing de cupom/parcelamento com exemplos simulados:

```bash
PYTHONPATH=. python scripts/validate_parsing.py
```

## Deploy

Veja [DEPLOY.md](DEPLOY.md) para opções recomendadas de deploy (Docker e systemd).

Se você estiver usando Railway, consulte a seção específica no [DEPLOY.md](DEPLOY.md) para configurar o serviço web principal e, se quiser, um segundo serviço para o agendador de relatórios.
