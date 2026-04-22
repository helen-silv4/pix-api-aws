import json
from unittest.mock import patch

from src.service.saldo_service import consultar_saldo

@patch("src.service.saldo_service.buscar_conta_por_id")
def test_consultar_saldo_com_sucesso(mock_buscar_conta):
    # arrange
    event = {
        "pathParameters": None,
        "queryStringParameters": {
            "contaId": "conta1"
        }
    }
    payload = {"contaId": "conta1"}

    mock_buscar_conta.return_value = {
        "contaId": "conta1",
        "saldo": 100
    }

    # act
    resposta = consultar_saldo(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 200
    assert body["contaId"] == "conta1"
    assert body["saldo"] == 100

def test_consultar_saldo_retorna_403_quando_conta_for_diferente_do_token():
    # arrange
    event = {
        "pathParameters": None,
        "queryStringParameters": {
            "contaId": "conta2"
        }
    }
    payload = {"contaId": "conta1"}

    # act
    resposta = consultar_saldo(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 403
    assert body["mensagem"] == "Acesso não permitido para esta conta"

@patch("src.service.saldo_service.buscar_conta_por_id")
def test_consultar_saldo_retorna_404_quando_conta_nao_existir(mock_buscar_conta):
    # arrange
    event = {
        "pathParameters": None,
        "queryStringParameters": {
            "contaId": "conta1"
        }
    }
    payload = {"contaId": "conta1"}

    mock_buscar_conta.return_value = None

    # act
    resposta = consultar_saldo(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 404
    assert body["mensagem"] == "Conta não encontrada"

def test_consultar_saldo_retorna_401_quando_token_nao_tiver_conta_id():
    # arrange
    event = {
        "pathParameters": None,
        "queryStringParameters": {
            "contaId": "conta1"
        }
    }
    payload = {}

    # act
    resposta = consultar_saldo(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 401
    assert body["mensagem"] == "Token sem contaId"