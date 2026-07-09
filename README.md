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
