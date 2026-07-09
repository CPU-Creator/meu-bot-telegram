# 🚀 FORCE REDEPLOY NO RAILWAY

## O Que Fazer

### **Opção 1: Force Push (Rápido - 1 min)**

```bash
cd /workspaces/meu-bot-telegram
echo "# Força redeploy" >> README.md
git add README.md
git commit -m "chore: force railway redeploy"
git push origin main
```

Railway vai detectar em ~30s e começar rebuild em ~1 min.

---

### **Opção 2: Via Railway Dashboard (Manual)**

1. Vá para: **https://railway.app**

2. Entre no seu projeto: **meu-bot-telegram**

3. Clique em **Deployments** (menu esquerdo)

4. Veja o último deployment

5. Se houver um **"Deploy"** ou **"Redeploy"** azul:
   - ✅ Clique nele!

6. Se não tiver:
   - ✅ Vá em **Settings**
   - ✅ Procure por **"Redeploy"** button
   - ✅ Clique!

---

### **Opção 3: Manual Trigger (Se custom webhook)**

```bash
# Usar Railway CLI (se instalado)
railway deploy --watch
```

---

## ✅ Como Saber que Funcionou

No Railway → Deployments → View Logs:

```
✅ PromoRadar Multi-Plataforma INICIANDO...
✅ Buscando: mouse game
✅ Publicado: Mouse Gamer RGB Logitech G502 (Shopee)
✅ Publicado: Mouse Mecânico Razer DeathAdder (Mercado Livre)
✅ Publicado: Teclado Mecânico Corsair K70 (Kabum)
✨ PromoRadar finalizou com sucesso!
```

---

## 🚨 Se Ainda Não Funcionar

### **Passo 1: Verificar Start Command**

Railway → Settings → Build & Deploy

Deve estar:
```
python bot_promoradar_demo.py
```

---

### **Passo 2: Verificar Variáveis**

Railway → Variables

Deve ter:
```
BOT_TOKEN = seu_token_aqui
CANAL_PROMORADAR = -1004496554566
```

---

### **Passo 3: Verificar Logs de Erro**

Railway → Deployments → View Logs

Procurar por:
- ❌ `Error`
- ❌ `Exception`
- ❌ `Failed`

---

## 💡 Dica Rápida

Se der problema, use o **bot original** que já estava funcionando:

```
Railway → Settings → Build & Deploy
python bot_promocoes.py
```

Depois volte para `bot_promoradar_demo.py` quando resolver.

---

**Vamos fazer isso agora? Qual opção prefere?**
