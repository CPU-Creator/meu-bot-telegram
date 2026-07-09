# Deploy — meu-bot-telegram

Opções de deploy recomendadas.

1) Usando Docker (recomendado para staging/produção)

- Construir imagem:

```bash
docker build -t promoradar:latest .
```

- Criar arquivo `.env` a partir de `.env.example` e preencher credenciais.

- Rodar com docker-compose:

```bash
docker-compose up -d --build
```

Logs:

```bash
docker-compose logs -f
```

2) Usando systemd (direto no servidor)

- Copie `systemd/promoradar-relatorio.service` e `systemd/promoradar.env.example` para `/etc/systemd/system/` e `/etc/default/` (ou conforme convenção) e ajuste caminhos.
- Certifique-se de ter um ambiente Python com dependências instaladas (virtualenv) e que o `.env` esteja no diretório correto.
- Habilite e inicie o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable promoradar-relatorio.service
sudo systemctl start promoradar-relatorio.service
sudo journalctl -u promoradar-relatorio -f
```

3) Usando Docker Compose + systemd (recomendado quando usar containers)

- Copie o repositório para `/opt/promoradar` (ou outro diretório de sua escolha).
- Copie `systemd/promoradar-docker.service` para `/etc/systemd/system/promoradar-docker.service` e ajuste `WorkingDirectory` e o caminho do `docker-compose.yml` se necessário.
- Crie `/etc/default/promoradar` contendo `COMPOSE_PROJECT_NAME` e outras variáveis opcionais ou deixe vazio.
- Exemplo de comandos:

```bash
sudo cp systemd/promoradar-docker.service /etc/systemd/system/
sudo mkdir -p /opt/promoradar
# copie os arquivos do projeto para /opt/promoradar
sudo cp -r . /opt/promoradar
sudo systemctl daemon-reload
sudo systemctl enable promoradar-docker.service
sudo systemctl start promoradar-docker.service
sudo journalctl -u promoradar-docker -f
```

Também incluí um script utilitário `scripts/deploy_docker.sh` para construir a imagem e iniciar o compose no servidor.

3) Dicas de segurança

- Nunca versionar `.env` com segredos.
- Use um secret manager (AWS Secrets Manager, GitHub Secrets) para CI/CD.
- Habilite backup do `promocoes.db` e monitore logs.

4) CI/CD

- Um workflow básico foi adicionado em `.github/workflows/ci.yml` para rodar testes e o harness.

