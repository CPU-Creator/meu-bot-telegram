def calcular_pontuacao(produto) -> int:
    try:
        preco = float(str(getattr(produto, "target_sale_price", 0)).replace(",", "."))
    except Exception:
        preco = 0.0

    try:
        antigo = float(str(getattr(produto, "original_price", 0)).replace(",", "."))
    except Exception:
        antigo = preco or 1.0

    if antigo <= 0:
        antigo = preco or 1.0

    desconto = 0
    if antigo > 0:
        desconto = int(((antigo - preco) / antigo) * 100)

    desconto = max(1, min(desconto, 95))

    volume = int(getattr(produto, "lastest_volume", 0) or 0)
    # considerar avaliação do produto quando disponível (escala 0-5)
    try:
        avaliacao = float(str(getattr(produto, "evaluate_rate", 0) or 0))
    except Exception:
        avaliacao = 0.0

    bonus_avaliacao = 0
    if avaliacao and avaliacao > 0:
        # normalizar para 0-10 pontos
        bonus_avaliacao = int(min(max((avaliacao / 5.0) * 10, 0), 10))

    score = 50 + min(desconto, 40) + min(volume // 1000, 10) + bonus_avaliacao
    return min(100, score)
