import json
import boto3
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
tabela = dynamodb.Table("tb_contas")


def decimal_para_json(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError


def lambda_handler(event, context):
    try:
        usuario_id = None

        path_params = event.get("pathParameters") or {}
        query_params = event.get("queryStringParameters") or {}

        if path_params.get("usuarioId"):
            usuario_id = path_params["usuarioId"]
        elif query_params.get("usuarioId"):
            usuario_id = query_params["usuarioId"]

        if not usuario_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"mensagem": "usuarioId é obrigatório"})
            }

        resposta = tabela.get_item(
            Key={"usuarioId": usuario_id}
        )

        item = resposta.get("Item")

        if not item:
            return {
                "statusCode": 404,
                "body": json.dumps({"mensagem": "Usuário não encontrado"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps(item, default=decimal_para_json)
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "mensagem": "Erro interno",
                "erro": str(e)
            })
        }