import unittest

from telegram.error import BadRequest

from bot_promocoes import enviar_mensagem_segura


class FakeBot:
    def __init__(self):
        self.sent_photo = False
        self.sent_message = False
        self.last_message = None

    async def send_photo(self, **kwargs):
        self.sent_photo = True
        raise BadRequest("Not Found")

    async def send_message(self, **kwargs):
        self.sent_message = True
        self.last_message = kwargs


class EnvioTests(unittest.IsolatedAsyncioTestCase):
    async def test_fallback_to_text_when_photo_send_fails(self):
        bot = FakeBot()

        enviado = await enviar_mensagem_segura(bot, "123", None, "mensagem", None)

        self.assertTrue(enviado)
        self.assertTrue(bot.sent_message)


if __name__ == "__main__":
    unittest.main()
