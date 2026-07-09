# 🚀 PROMORADAR - ATIVA NO RAILWAY

## ✅ Você Já Mudou Para: `python bot_promoradar.py`

---

## 🎯 PRÓXIMO PASSO: REDEPLOY

### **Opção 1: Auto-Deploy (Recomendado)**

Como você mudou o arquivo `railway.toml` localmente:

1. **Git commit:**
   ```bash
   cd /workspaces/meu-bot-telegram
   git add railway.toml
   git commit -m "config: atualizar bot para promoradar"
   git push origin main
   ```

2. **Railway vai detectar automaticamente:**
   - GitHub integrado
   - Novo commit → rebuild
   - Novo bot rodando em 2 min

3. **Monitorar:**
   - Railway → Seu projeto
   - Deployments → Ver logs
   - ✅ Pronto!

---

### **Opção 2: Manual (Se quiser controlar)**

1. **Acesse:** https://railway.app

2. **Seu projeto:** `meu-bot-telegram`

3. **Settings → Build & Deploy**

4. **Start Command:**
   ```
   Atual: python bot_promoradar.py
   ```
   (Já está correto!)

5. **Clique:** `Redeploy`

6. **Aguarde:** ~2 minutos

---

### **Opção 3: Usar Versão Demo PRIMEIRO**

Se quiser testar sem risco:

1. **Settings → Build & Deploy**

2. **Start Command:**
   ```
   python bot_promoradar_demo.py
   ```

3. **Redeploy**

4. **Resultado:**
   - ✅ Produtos de teste aparecem
   - ✅ Bot funciona garantido
   - ✅ Prova o conceito

---

## 📊 STATUS CURRENT

```
Repositório: GitHub CPU-Creator/meu-bot-telegram
Branch: main
Bots Disponíveis:
  ✅ bot_promoradar_demo.py (RECOMENDADO - FUNCIONA 100%)
  🚀 bot_promoradar.py (Multi-plataforma real)
  📦 bot_promocoes.py (Original - compatível)

Railway:
  Comando Atual: python bot_promoradar.py
  Status: Pronto para redeploy
  Trigger: Próximo push do GitHub
```

---

## 🔍 COMO MONITORAR

### **Em Tempo Real:**

1. Railway → Seu projeto
2. Deployments (menu esquerdo)
3. Deploy mais recente
4. **View Logs** (botão azul)

**Você verá:**
```
INFO:__main__:🚀 PromoRadar iniciando...
INFO:__main__:📺 Canal: -1004496554566
INFO:__main__:🔎 Buscando: mouse game
INFO:__main__:✅ Publicado: Mouse Gamer RGB
INFO:__main__:✨ PromoRadar finalizou com sucesso!
```

---

## ⚡ ACIONADOR DE REDEPLOY

### **Opção 1: Via GitHub (Automático)**
```bash
git push origin main
# Railway detecta em ~30s
# Começa rebuild em ~1 min
```

### **Opção 2: Via Railway (Manual)**
```
Railway.app → Redeploy (botão na página do projeto)
```

### **Opção 3: Via Webhook (Avançado)**
```
Settings → Webhooks (se quiser trigger custom)
```

---

## 📋 CHECKLIST FINAL

- ✅ Bot criado (3 versões)
- ✅ GitHub atualizado
- ✅ Railway configurado
- ✅ .env pronto
- ✅ Dockerfile suporta ambos
- ✅ Documentação completa
- ⏳ **Aguardando redeploy**

---

## 🎉 O QUE VAI ACONTECER

### **Quando o bot rodar:**

```
Seu Telegram
    ↓
[Mensagem 1] 🚀 Mouse Gamer RGB
             💵 R$ 149,90 (-50%)
             🏪 Shopee
    ↓
[Mensagem 2] 🚀 Teclado Corsair K70
             💵 R$ 249,90 (-45%)
             🏪 Kabum
    ↓
[Mensagem 3] 🚀 Fone SteelSeries
             💵 R$ 399,90 (-50%)
             🏪 Pichau
```

---

## 🚀 COMANDO FINAL

**Para ativar agora no Railway:**

```bash
# 1. Ir para seu projeto Railway
# 2. Settings → Build & Deploy
# 3. Clique em "Redeploy" (ou push no GitHub)
# 4. Aguarde 2 minutos
# 5. Pronto! 🎉
```

---

**Status:** 🟢 **PRONTO PARA RODAR**

**Próximo passo:** Vá ao Railway e clique REDEPLOY!

---

*Criado em: 2026-07-09*  
*Version: 1.0.0 - Multi-Plataforma*
