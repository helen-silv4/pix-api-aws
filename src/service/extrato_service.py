from src.output.transacao_repository import listar_transacoes
from src.shared.logger import log_info
from src.shared.response import montar_resposta, montar_resposta_json
from src.shared.serializers import converter_decimal_para_json

def consultar_extrato(event, payload):
    conta_id_token = payload.get("contaId")

    if not conta_id_token:
        return montar_resposta(401, "Token sem contaId")

    query_params = event.get("queryStringParameters") or {}
    conta_id_param = query_params.get("contaId")

    if conta_id_param and conta_id_param != conta_id_token:
        return montar_resposta(403, "Acesso não permitido para esta conta")

    todas_transacoes = listar_transacoes()

    extrato = []
    for transacao in todas_transacoes:
        if (transacao.get("origem") == conta_id_token or transacao.get("destino") == conta_id_token):
            extrato.append(transacao)

    # ordena o extrato por data de criação (mais recente para o mais antigo)
    extrato.sort(key=lambda x: x.get("criadoEm"), reverse=True)

    log_info("Extrato consultado com sucesso", contaId=conta_id_token, quantidadeTransacoes=len(extrato))

    return montar_resposta_json(200, extrato, default=converter_decimal_para_json)