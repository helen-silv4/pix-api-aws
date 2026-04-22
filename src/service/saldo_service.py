from output.conta_repository import buscar_conta_por_id
from shared.logger import log_info
from shared.response import montar_resposta, montar_resposta_json
from shared.serializers import converter_decimal_para_json

def consultar_saldo(event, payload):
    conta_id_token = payload.get("contaId")

    if not conta_id_token:
        return montar_resposta(401, "Token sem contaId")

    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}

    conta_id_param = None

    if path_params.get("contaId"):
        conta_id_param = path_params["contaId"]
    elif query_params.get("contaId"):
        conta_id_param = query_params["contaId"]

    if conta_id_param and conta_id_param != conta_id_token:
        return montar_resposta(403, "Acesso não permitido para esta conta")

    log_info("Consultando saldo", contaId=conta_id_token)
    conta = buscar_conta_por_id(conta_id_token)

    if not conta:
        return montar_resposta(404, "Conta não encontrada")

    log_info("Saldo consultado com sucesso", contaId=conta_id_token)

    return montar_resposta_json(200, conta, default=converter_decimal_para_json)