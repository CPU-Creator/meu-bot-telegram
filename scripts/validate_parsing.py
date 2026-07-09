"""
Script de validação para parsing de cupom e parcelamento.
Execute: PYTHONPATH=. python scripts/validate_parsing.py
"""
import logging
from types import SimpleNamespace
from bot_promocoes import preparar_produto, criar_mensagem

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def make(prod):
    try:
        logging.info("--- CASO ---")
        logging.info("produto.product_title: %s", prod.product_title)
        logging.info("preparar_produto output:\n%s", preparar_produto(prod))
        logging.info("criar_mensagem output:\n%s", criar_mensagem(prod, "Legenda de teste"))
    except Exception as e:
        logging.error("Erro ao processar caso: %s", e)


if __name__ == "__main__":
    casos = []

    # 1) cupom como string
    casos.append(SimpleNamespace(
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
    ))

    # 2) cupom como dict
    casos.append(SimpleNamespace(
        product_title="Teclado Mecânico Y",
        target_sale_price="199.00",
        original_price="399.00",
        evaluate_rate="4.9",
        lastest_volume="800",
        promotion_link="https://ex.com/p/2",
        coupon={"code": "SAVE20", "amount": "20%"},
        installments={"count": 10, "value": 19.90, "interest": False},
        product_main_image_url="img2.jpg",
        product_id="p2",
    ))

    # 3) parcelamento como lista de opções
    casos.append(SimpleNamespace(
        product_title="Fone Bluetooth Z",
        target_sale_price="79.90",
        original_price="159.90",
        evaluate_rate="4.5",
        lastest_volume="300",
        promotion_link="https://ex.com/p/3",
        coupon=None,
        installments=[{"count": 6, "value": 13.32}, {"count": 12, "value": 6.66}],
        product_main_image_url="img3.jpg",
        product_id="p3",
    ))

    # 4) cupom e parcelas em formatos inesperados
    casos.append(SimpleNamespace(
        product_title="SSD NVMe 1TB",
        target_sale_price="249.00",
        original_price="499.00",
        evaluate_rate="4.8",
        lastest_volume="200",
        promotion_link="https://ex.com/p/4",
        coupon={"name": "PROMO50"},
        installments="até 12x de R$ 20,75",
        product_main_image_url="img4.jpg",
        product_id="p4",
    ))

    for c in casos:
        make(c)
        logging.info("\n")
