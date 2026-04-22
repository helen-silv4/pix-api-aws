import json
from unittest.mock import patch

from src.service.extrato_service import consultar_extrato

@patch("src.service.extrato_service.listar_transacoes")
def test_consultar_extrato_com_sucesso(mock_listar_transacoes):
    # arrange
    event = {
        "queryStringParameters": {
            "contaId": "conta1"
        }
    }
    payload = {"contaId": "conta1"}

    mock_listar_transacoes.return_value = [
        {
            "transacaoId": "1",
            "origem": "conta1",
            "destino": "conta2",
            "valor": 10,
            "criadoEm": "2026-04-22T10:00:00"
        },
        {
            "transacaoId": "2",
            "origem": "conta3",
            "destino": "conta1",
            "valor": 20,
            "criadoEm": "2026-04-22T11:00:00"
        },
        {
            "transacaoId": "3",
            "origem": "conta4",
            "destino": "conta5",
            "valor": 30,
            "criadoEm": "2026-04-22T09:00:00"
        }
    ]

    # act
    resposta = consultar_extrato(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 200
    assert len(body) == 2
    assert body[0]["transacaoId"] == "2"
    assert body[1]["transacaoId"] == "1"

def test_consultar_extrato_retorna_403_quando_conta_for_diferente_do_token():
    # arrange
    event = {
        "queryStringParameters": {
            "contaId": "conta2"
        }
    }
    payload = {"contaId": "conta1"}

    # act
    resposta = consultar_extrato(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 403
    assert body["mensagem"] == "Acesso não permitido para esta conta"

def test_consultar_extrato_retorna_401_quando_token_nao_tiver_conta_id():
    # arrange
    event = {
        "queryStringParameters": {
            "contaId": "conta1"
        }
    }
    payload = {}

    # act
    resposta = consultar_extrato(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 401
    assert body["mensagem"] == "Token sem contaId"

@patch("src.service.extrato_service.listar_transacoes")
def test_consultar_extrato_retorna_lista_vazia_quando_nao_houver_transacoes(mock_listar_transacoes):
    # arrange
    event = {
        "queryStringParameters": {
            "contaId": "conta1"
        }
    }
    payload = {"contaId": "conta1"}

    mock_listar_transacoes.return_value = []

    # act
    resposta = consultar_extrato(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 200
    assert body == []