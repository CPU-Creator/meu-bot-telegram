import importlib
import unittest


class SmokeTests(unittest.TestCase):
    def test_import_modules(self):
        for module_name in ["agente_ia", "pontuacao", "memoria"]:
            module = importlib.import_module(module_name)
            self.assertTrue(hasattr(module, "__file__"))


if __name__ == "__main__":
    unittest.main()
