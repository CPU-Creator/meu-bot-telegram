from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from PIL import Image

import bot_promocoes
from bot_promocoes import criar_mensagem, enriquecer_produto_com_detalhes


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
    assert "🎟️ Cupom disponível" in msg
    assert "Frete grátis: verifique na página do produto" in msg


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


def test_criar_mensagem_frete_gratis():
    p = SimpleNamespace(
        product_title="Fonte Gamer",
        target_sale_price="149.90",
        original_price="199.90",
        evaluate_rate="4.8",
        lastest_volume="500",
        promotion_link="https://ex.com/p/3",
        free_shipping=True,
        product_main_image_url="img3.jpg",
        product_id="p3",
    )
    msg = criar_mensagem(p, "Legenda")
    assert "Frete grátis" in msg
    assert "🎟️ Cupom:" in msg


def test_criar_mensagem_cupom_fallback_quando_api_nao_informa():
    p = SimpleNamespace(
        product_title="Webcam Full HD",
        target_sale_price="89.90",
        original_price="129.90",
        evaluate_rate="4.6",
        lastest_volume="240",
        promotion_link="https://ex.com/p/5",
        installments=None,
        product_main_image_url="img5.jpg",
        product_id="p5",
    )
    msg = criar_mensagem(p, "Legenda")
    assert "consulte os cupons ativos na página do produto" in msg


def test_criar_mensagem_cupom_objeto_aninhado():
    cupom = SimpleNamespace(couponCode="SAVE30", discountAmount="30%")
    p = SimpleNamespace(
        product_title="SSD NVMe",
        target_sale_price="249.90",
        original_price="499.90",
        evaluate_rate="4.8",
        lastest_volume="1200",
        promotion_link="https://ex.com/p/4",
        coupon_info=cupom,
        installments=None,
        product_main_image_url="img4.jpg",
        product_id="p4",
    )
    msg = criar_mensagem(p, "Legenda")
    assert "SAVE30" in msg or "30%" in msg


def test_enriquecer_produto_com_detalhes_mescla_campos_novos():
    produto = SimpleNamespace(product_id="p6", product_title="Produto", target_sale_price="99.90")
    detalhe = SimpleNamespace(coupon_code="CUPOM99", free_shipping=True, installments={"count": 5, "value": 19.98})

    class FakeApi:
        def get_products_details(self, product_ids):
            assert product_ids == ["p6"]
            return [detalhe]

    enriquecido = enriquecer_produto_com_detalhes(FakeApi(), produto)

    assert enriquecido is produto
    assert produto.coupon_code == "CUPOM99"
    assert produto.free_shipping is True
    assert produto.installments == {"count": 5, "value": 19.98}


def test_colocar_logo_em_imagem_remota(tmp_path):
    logo_path = tmp_path / "logo.png"
    logo = Image.new("RGBA", (40, 40), (255, 0, 0, 180))
    logo.save(logo_path)

    base = Image.new("RGB", (120, 120), (255, 255, 255))
    imagem_bytes = BytesIO()
    base.save(imagem_bytes, format="PNG")

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return imagem_bytes.getvalue()

    with patch.object(bot_promocoes, "LOGO", str(logo_path)):
        with patch.object(bot_promocoes, "urlopen", return_value=FakeResponse()):
            arquivo = bot_promocoes.colocar_logo("https://exemplo.com/imagem.png")

    assert Path(arquivo).exists()

    with Image.open(arquivo) as imagem_final:
        assert imagem_final.size == (120, 120)
        assert imagem_final.getpixel((25, 25)) != (255, 255, 255, 255)

    Path(arquivo).unlink(missing_ok=True)