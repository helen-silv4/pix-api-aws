import json
from src.shared.serializers import converter_decimal_para_json

def log_info(mensagem, **dados):
    print(json.dumps({
        "nivel": "INFO",
        "mensagem": mensagem,
        "dados": dados
    }, default=converter_decimal_para_json))

def log_error(mensagem, **dados):
    print(json.dumps({
        "nivel": "ERROR",
        "mensagem": mensagem,
        "dados": dados
    }, default=converter_decimal_para_json))