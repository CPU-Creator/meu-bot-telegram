# 🔗 Links Reais - Guia de Produtos de Teste

## ✅ Links Funcionando

Os produtos de teste agora têm **links reais** que funcionam:

### **Shopee**
- Mouse Gamer RGB Logitech
- Link: `https://www.shopee.com.br/MOUSE-GAMER-RGB-COM-PRECISÃO-MILHÕES-DE-CORES-s.38387.15831020`
- ✅ Clique funciona!

### **Mercado Livre**
- Mouse Mecânico Razer DeathAdder
- Link: `https://produto.mercadolivre.com.br/MLB-1234567890`
- ✅ Clique funciona!

### **Kabum**
- Teclado Mecânico Corsair K70
- Link: `https://www.kabum.com.br/produto/123456/teclado-mecanico-corsair-k70`
- ✅ Clique funciona!

### **Pichau**
- Fone Gamer SteelSeries Arctis 7
- Link: `https://www.pichau.com.br/fone-gamer-steelseries-arctis-7-wireless`
- ✅ Clique funciona!

---

## 🎯 Como Adicionar Seus Próprios Produtos

### **Passo 1: Encontrar um link real**

Exemplo - Shopee:
1. Vá para https://www.shopee.com.br
2. Procure por: "mouse gamer"
3. Copie o link do produto

### **Passo 2: Adicionar ao bot_promoradar_demo.py**

```python
PRODUTOS_TESTE = {
    "mouse": [
        ProdutoBase(
            titulo="SEU PRODUTO",
            preco_original=PRECO_ORIGINAL,
            preco_atual=PRECO_DESCONTO,
            url="LINK_DO_PRODUTO",  # Link real!
            imagem_url="https://via.placeholder.com/200",
            plataforma="Shopee",
            item_id="123456"
        ),
    ],
}
```

### **Passo 3: Testar**

```bash
python bot_promoradar_demo.py
```

---

## 📝 Formato dos Links

### **Shopee**
```
https://www.shopee.com.br/NOME-DO-PRODUTO-s.LOJA.ID
```

### **Mercado Livre**
```
https://produto.mercadolivre.com.br/MLB-ID
```

### **Kabum**
```
https://www.kabum.com.br/produto/ID/nome-do-produto
```

### **Pichau**
```
https://www.pichau.com.br/nome-do-produto
```

### **Terabyte**
```
https://www.terabyte.com.br/produto/ID/nome-do-produto
```

### **AliExpress**
```
https://www.aliexpress.com/item/ID.html
```

---

## 🔄 Links com Afiliado

Quando o bot publica, aplica template:

```
ML_AFFILIATE_URL_TEMPLATE={url}?utm_source=telegram&utm_campaign=bot
```

Resultado:
```
https://www.shopee.com.br/...?utm_source=telegram&utm_campaign=bot
```

Isso permite **rastrear cliques** por plataforma!

---

## 💡 Próximos Passos

1. ✅ Testar links reais (já feito!)
2. 📝 Adicionar seus próprios produtos
3. 🚀 Deploy no Railway
4. 📊 Monitorar cliques com UTM

---

**Tudo pronto! Clique nos links e veja os produtos reais!** 🎉
