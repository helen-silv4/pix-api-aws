import json
import boto3
from decimal import Decimal

# conexão dynamo
dynamodb = boto3.resource("dynamodb")
tabela = dynamodb.Table("tb_contas")

# funções auxiliares
def converter_decimal_para_json(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    raise TypeError

def montar_resposta(status_code, mensagem):
    return {
        "statusCode": status_code,
        "body": json.dumps({"mensagem": mensagem})
    }

def buscar_conta_por_id(conta_id):
    resposta = tabela.get_item(
        Key={"contaId": conta_id}
    )
    return resposta.get("Item")

def atualizar_saldo(conta_id, novo_saldo):
    tabela.update_item(
        Key={"contaId": conta_id},
        UpdateExpression="SET saldo = :novo_saldo",
        ExpressionAttributeValues={
            ":novo_saldo": novo_saldo
        }
    )

def consultar_saldo(event):
    conta_id = None

    path_params = event.get("pathParameters") or {}
    query_params = event.get("queryStringParameters") or {}

    if path_params.get("contaId"):
        conta_id = path_params["contaId"]
    elif query_params.get("contaId"):
        conta_id = query_params["contaId"]

    if not conta_id:
        return montar_resposta(400, "contaId é obrigatório")

    conta = buscar_conta_por_id(conta_id)

    if not conta:
        return montar_resposta(404, "Conta não encontrada")

    return {
        "statusCode": 200,
        "body": json.dumps(conta, default=converter_decimal_para_json)
    }


def transferir(event):

    # corpo
    body = event.get("body")

    if not body:
        return montar_resposta(400, "Body é obrigatório")

    try:
        dados = json.loads(body) # transforma para dicionário
    except json.JSONDecodeError:
        return montar_resposta(400, "JSON inválido")

    origem = dados.get("origem")
    destino = dados.get("destino")
    valor = dados.get("valor")

    if not origem or not destino or valor is None:
        return montar_resposta(400, "origem, destino e valor são obrigatórios")

    if origem == destino:
        return montar_resposta(400, "Origem e destino não podem ser iguais")

    # saldo
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
        return montar_resposta(400, "Saldo insuficiente")

    novo_saldo_origem = saldo_origem - valor
    novo_saldo_destino = saldo_destino + valor

    atualizar_saldo(origem, novo_saldo_origem)
    atualizar_saldo(destino, novo_saldo_destino)

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "mensagem": "Transferência realizada",
                "origem": origem,
                "destino": destino,
                "valor": valor,
                "saldoOrigemAtual": novo_saldo_origem,
                "saldoDestinoAtual": novo_saldo_destino
            },
            default=converter_decimal_para_json
        )
    }

def lambda_handler(event, context):
    try:
        rota = event.get("rawPath")
        metodo = event.get("requestContext", {}).get("http", {}).get("method")

        if rota == "/saldo" and metodo == "GET":
            return consultar_saldo(event)

        if rota == "/transferencia" and metodo == "POST":
            return transferir(event)

        return montar_resposta(404, "Rota não encontrada")

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "mensagem": "Erro interno",
                "erro": str(e)
            })
        }