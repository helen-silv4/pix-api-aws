import json
from decimal import Decimal
from unittest.mock import patch

from src.service.transferencia_service import transferir

@patch("src.service.transferencia_service.registrar_transacao")
@patch("src.service.transferencia_service.atualizar_saldo")
@patch("src.service.transferencia_service.buscar_conta_por_id")
def test_transferencia_com_sucesso(mock_buscar_conta, mock_atualizar_saldo, mock_registrar_transacao):
    # arrange
    event = {
        "body": json.dumps({
            "origem": "conta1",
            "destino": "conta2",
            "valor": 50
        })
    }
    payload = {"contaId": "conta1"}

    mock_buscar_conta.side_effect = [
        {"contaId": "conta1", "saldo": Decimal("100")},
        {"contaId": "conta2", "saldo": Decimal("200")}
    ]
    mock_registrar_transacao.return_value = "tx-123"

    # act
    resposta = transferir(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 200
    assert body["mensagem"] == "Transferência realizada"
    assert body["transacaoId"] == "tx-123"
    assert body["origem"] == "conta1"
    assert body["destino"] == "conta2"
    assert body["valor"] == 50.0
    assert body["saldoOrigemAtual"] == 50.0
    assert body["saldoDestinoAtual"] == 250.0
    assert mock_atualizar_saldo.call_count == 2
    mock_registrar_transacao.assert_called_once_with("conta1", "conta2", Decimal("50"), "SUCESSO")

def test_transferencia_retorna_403_quando_origem_for_diferente_do_token():
    # arrange
    event = {
        "body": json.dumps({
            "origem": "conta2",
            "destino": "conta1",
            "valor": 50
        })
    }
    payload = {"contaId": "conta1"}

    # act
    resposta = transferir(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 403
    assert body["mensagem"] == "Você só pode transferir a partir da sua própria conta"

@patch("src.service.transferencia_service.buscar_conta_por_id")
def test_transferencia_retorna_400_quando_saldo_for_insuficiente(mock_buscar_conta):
    # arrange
    event = {
        "body": json.dumps({
            "origem": "conta1",
            "destino": "conta2",
            "valor": 500
        })
    }
    payload = {"contaId": "conta1"}

    mock_buscar_conta.side_effect = [
        {"contaId": "conta1", "saldo": Decimal("100")},
        {"contaId": "conta2", "saldo": Decimal("200")}
    ]

    # act
    resposta = transferir(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 400
    assert body["mensagem"] == "Saldo insuficiente"

def test_transferencia_retorna_400_quando_origem_e_destino_forem_iguais():
    # arrange
    event = {
        "body": json.dumps({
            "origem": "conta1",
            "destino": "conta1",
            "valor": 10
        })
    }
    payload = {"contaId": "conta1"}

    # act
    resposta = transferir(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 400
    assert body["mensagem"] == "Origem e destino não podem ser iguais"

def test_transferencia_retorna_400_quando_valor_for_invalido():
    # arrange
    event = {
        "body": json.dumps({
            "origem": "conta1",
            "destino": "conta2",
            "valor": "abc"
        })
    }
    payload = {"contaId": "conta1"}

    # act
    resposta = transferir(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 400
    assert body["mensagem"] == "Valor inválido"

def test_transferencia_retorna_400_quando_body_estiver_ausente():
    # arrange
    event = {}
    payload = {"contaId": "conta1"}

    # act
    resposta = transferir(event, payload)
    body = json.loads(resposta["body"])

    # assert
    assert resposta["statusCode"] == 400
    assert body["mensagem"] == "Body é obrigatório"