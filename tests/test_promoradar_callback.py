import asyncio
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import bot_promoradar


def test_handler_health_retorna_ok():
    resposta = asyncio.run(bot_promoradar.handler_health(None))

    assert resposta.status == 200
    assert json.loads(resposta.text) == {"status": "ok"}


def test_handler_ml_callback_rejeita_quando_code_nao_existe():
    request = SimpleNamespace(query={})

    resposta = asyncio.run(bot_promoradar.handler_ml_callback(request))

    assert resposta.status == 400
    assert "code" in resposta.text


def test_handler_ml_callback_salva_code_quando_oauth_nao_esta_configurado():
    request = SimpleNamespace(query={"code": "abc123", "state": "estado-1"})

    with patch.object(bot_promoradar, "ML_APP_ID", ""):
        with patch.object(bot_promoradar, "ML_CLIENT_SECRET", ""):
            with patch.object(bot_promoradar, "ML_REDIRECT_URI", ""):
                with patch.object(bot_promoradar, "salvar_code_mercadolivre") as salvar_code:
                    resposta = asyncio.run(bot_promoradar.handler_ml_callback(request))

    salvar_code.assert_called_once_with("abc123", "estado-1")
    assert resposta.status == 200
    assert "Code recebido e salvo" in resposta.text


def test_handler_ml_callback_troca_code_por_token_quando_oauth_esta_configurado():
    request = SimpleNamespace(query={"code": "abc123", "state": "estado-1"})
    token_data = {"access_token": "token-123"}

    with patch.object(bot_promoradar, "ML_APP_ID", "app-id"):
        with patch.object(bot_promoradar, "ML_CLIENT_SECRET", "secret"):
            with patch.object(bot_promoradar, "ML_REDIRECT_URI", "https://exemplo.com/callback"):
                with patch.object(bot_promoradar, "salvar_code_mercadolivre") as salvar_code:
                    with patch.object(bot_promoradar, "trocar_code_por_token", AsyncMock(return_value=token_data)) as trocar_code:
                        with patch.object(bot_promoradar, "salvar_token_mercadolivre") as salvar_token:
                            resposta = asyncio.run(bot_promoradar.handler_ml_callback(request))

    salvar_code.assert_called_once_with("abc123", "estado-1")
    trocar_code.assert_awaited_once_with("abc123")
    salvar_token.assert_called_once_with(token_data)
    assert resposta.status == 200
    assert "Autorização concluída com sucesso" in resposta.text