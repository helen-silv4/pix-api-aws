import json
from decimal import Decimal
from src.output.conta_repository import buscar_conta_por_id, atualizar_saldo
from src.output.transacao_repository import registrar_transacao
from src.shared.logger import log_info, log_error
from src.shared.response import montar_resposta, montar_resposta_json
from src.shared.serializers import converter_decimal_para_json

def transferir(event, payload):
    conta_id_token = payload.get("contaId")
    log_info("Iniciando transferencia", contaToken=conta_id_token)

    if not conta_id_token:
        return montar_resposta(401, "Token sem contaId")

    body = event.get("body")
    if not body:
        return montar_resposta(400, "Body é obrigatório")

    try:
        dados = json.loads(body)
    except json.JSONDecodeError:
        return montar_resposta(400, "JSON inválido")

    origem = dados.get("origem")
    destino = dados.get("destino")
    valor = dados.get("valor")

    log_info("Dados de transferencia recebidos", origem=origem, destino=destino, valor=valor)

    if not origem or not destino or valor is None:
        return montar_resposta(400, "origem, destino e valor são obrigatórios")
    if origem != conta_id_token:
        return montar_resposta(403, "Você só pode transferir a partir da sua própria conta")
    if origem == destino:
        return montar_resposta(400, "Origem e destino não podem ser iguais")

    try:
        valor = Decimal(str(valor))
    except Exception:
        return montar_resposta(400, "Valor inválido")

    if valor <= 0:
        return montar_resposta(400, "Valor deve ser maior que zero")

    conta_origem = buscar_conta_por_id(origem)
    conta_destino = buscar_conta_por_id(destino)

    if not conta_origem:
        return montar_resposta(404, "Conta de origem não encontrada")
    if not conta_destino:
        return montar_resposta(404, "Conta de destino não encontrada")

    saldo_origem = conta_origem["saldo"]
    saldo_destino = conta_destino["saldo"]

    if saldo_origem < valor:
        log_error(
            "Transferencia recusada por saldo insuficiente",
            origem=origem,
            destino=destino,
            valor=valor,
            saldoOrigem=saldo_origem
        )
        return montar_resposta(400, "Saldo insuficiente")

    novo_saldo_origem = saldo_origem - valor
    novo_saldo_destino = saldo_destino + valor

    atualizar_saldo(origem, novo_saldo_origem)
    atualizar_saldo(destino, novo_saldo_destino)

    transacao_id = registrar_transacao(origem, destino, valor, "SUCESSO")

    log_info(
        "Transferencia realizada com sucesso",
        transacaoId=transacao_id,
        origem=origem,
        destino=destino,
        valor=valor
    )

    return montar_resposta_json(
        200,
        {
            "mensagem": "Transferência realizada",
            "transacaoId": transacao_id,
            "origem": origem,
            "destino": destino,
            "valor": valor,
            "saldoOrigemAtual": novo_saldo_origem,
            "saldoDestinoAtual": novo_saldo_destino
        },
        default=converter_decimal_para_json
    )