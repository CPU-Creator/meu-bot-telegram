import unittest

from bot_promocoes import formatar_tempo


class ConsoleTests(unittest.TestCase):
    def test_formatar_tempo(self):
        self.assertEqual(formatar_tempo(65), "1m 5s")
        self.assertEqual(formatar_tempo(3661), "1h 1m 1s")
        self.assertEqual(formatar_tempo(0), "agora")


if __name__ == "__main__":
    unittest.main()
