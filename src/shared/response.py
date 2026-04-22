import json

def montar_resposta(status_code, mensagem):
    return {
        "statusCode": status_code,
        "body": json.dumps({"mensagem": mensagem})
    }

def montar_resposta_json(status_code, body, default=None):
    return {
        "statusCode": status_code,
        "body": json.dumps(body, default=default)
    }