from types import SimpleNamespace
from bot_promocoes import criar_mensagem


def test_criar_mensagem_cupom_string():
    p = SimpleNamespace(
        product_title="Mouse Gamer X",
        target_sale_price="49.90",
        original_price="99.90",
        evaluate_rate="4.7",
        lastest_volume="1500",
        promotion_link="https://ex.com/p/1",
        coupon_code="CUPOM10",
        installments=None,
        product_main_image_url="img.jpg",
        product_id="p1",
    )
    msg = criar_mensagem(p, "Legenda")
    assert "🎟️ Cupom" in msg


def test_criar_mensagem_parcelas_dict():
    p = SimpleNamespace(
        product_title="Teclado",
        target_sale_price="199.00",
        original_price="399.00",
        evaluate_rate="4.9",
        lastest_volume="800",
        promotion_link="https://ex.com/p/2",
        coupon={"code": "SAVE20", "amount": "20%"},
        installments={"count": 10, "value": 19.90, "interest": False},
        product_main_image_url="img2.jpg",
        product_id="p2",
    )
    msg = criar_mensagem(p, "Legenda")
    assert "💳 Parcelamento" in msg
    assert "10x" in msg or "até 10" in msg