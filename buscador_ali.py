from aliexpress_api import AliexpressApi, models

# --- AS SUAS CREDENCIAIS ---
KEY = '538904'
SECRET = '44A11VBSkzXXKReeQDyNzcszKFCd9VOS' # Mantenha a chave que está funcionando!
TRACKING_ID = 'default' 

# Inicializa a API
aliexpress = AliexpressApi(KEY, SECRET, models.Language.PT, models.Currency.BRL, TRACKING_ID)

def encontrar_lista_produtos(objeto):
    """Função inteligente que vasculha o labirinto de dados e encontra a lista de produtos."""
    if isinstance(objeto, list):
        return objeto
    
    if hasattr(objeto, '__dict__'):
        for chave, valor in vars(objeto).items():
            # Se encontrar uma lista, achou os produtos!
            if isinstance(valor, list):
                return valor
            # Se encontrar outra "caixa", vasculha dentro dela também
            resultado = encontrar_lista_produtos(valor)
            if resultado:
                return resultado
    return []

print("A buscar ofertas no AliExpress...")

try:
    # A conexão que já sabemos que funciona perfeitamente
    produtos_brutos = aliexpress.get_products(keywords='tecnologia', limit=3)
    
    print("\n✅ CONEXÃO BEM SUCEDIDA!\n")
    
    # Usamos a nossa função para encontrar a lista, não importa onde a biblioteca a escondeu
    lista_produtos = encontrar_lista_produtos(produtos_brutos)
    
    if not lista_produtos:
        print("❌ A lista de produtos veio vazia ou a estrutura mudou radicalmente.")
        print("Dados brutos:", vars(produtos_brutos))
    else:
        # Imprimindo os resultados formatados
        for p in lista_produtos:
            # Puxando os dados (com opções de nomes alternativos por segurança)
            titulo = getattr(p, 'product_title', getattr(p, 'title', 'Sem título'))
            preco = getattr(p, 'target_sale_price', getattr(p, 'sale_price', 'N/A'))
            link = getattr(p, 'promotion_link', getattr(p, 'url', 'Link não disponível'))
            
            print(f"🔥 Produto: {titulo}")
            print(f"💰 Preço: R$ {preco}")
            print(f"🔗 Link Afiliado: {link}")
            print("-" * 40)
            
except Exception as e:
    print(f"\n❌ ERRO NA BUSCA: {e}")