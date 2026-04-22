import json
from service.extrato_service import consultar_extrato
from service.saldo_service import consultar_saldo
from service.transferencia_service import transferir
from shared.auth import validar_token
from shared.logger import log_error, log_info
from shared.response import montar_resposta

def lambda_handler(event, context):
    try:
        resultado = validar_token(event)
        
        if "statusCode" in resultado:
            return resultado
        
        payload = resultado

        rota = event.get("rawPath")
        metodo = event.get("requestContext", {}).get("http", {}).get("method")

        log_info("Requisicao recebida", rota=rota, metodo=metodo)

        if rota == "/saldo" and metodo == "GET":
            return consultar_saldo(event, payload)
        if rota == "/transferencia" and metodo == "POST":
            return transferir(event, payload)
        if rota == "/extrato" and metodo == "GET":
            return consultar_extrato(event, payload)
        
        return montar_resposta(404, "Rota não encontrada")

    except Exception as e:
        log_error("Erro interno na lambda", erro=str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({
                "mensagem": "Erro interno",
                "erro": str(e)
            })
        }