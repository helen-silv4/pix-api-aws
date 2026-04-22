import json
import boto3
import uuid
import jwt
from decimal import Decimal
from datetime import datetime
from zoneinfo import ZoneInfo

# conexão dynamo
dynamodb = boto3.resource("dynamodb")
tabela_contas = dynamodb.Table("tb_contas")
tabela_transacoes = dynamodb.Table("tb_transacoes")

# token 
SECRET = "chave-secreta-geracao-token-com-jwt"

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
    resposta = tabela_contas.get_item(
        Key={"contaId": conta_id}
    )
    return resposta.get("Item")

def atualizar_saldo(conta_id, novo_saldo):
    tabela_contas.update_item(
        Key={"contaId": conta_id},
        UpdateExpression="SET saldo = :novo_saldo",
        ExpressionAttributeValues={
            ":novo_saldo": novo_saldo
        }
    )

def registrar_transacao(origem, destino, valor, status):
    transacao_id = str(uuid.uuid4())
    criado_em = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%dT%H:%M:%S")

    tabela_transacoes.put_item(
        Item={
            "transacaoId": transacao_id,
            "origem": origem,
            "destino": destino,
            "valor": valor,
            "status": status,
            "criadoEm": criado_em
        }
    )

    return transacao_id
 
def validar_token(event):
    headers = event.get("headers") or {}
    authorization = headers.get("authorization") or headers.get("Authorization")

    if not authorization:
        return montar_resposta(401, "Token não informado")

    if not authorization.startswith("Bearer "):
        return montar_resposta(401, "Formato do token inválido")

    token = authorization.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return payload  # sucesso
    except jwt.ExpiredSignatureError:
        return montar_resposta(401, "Token expirado")
    except jwt.InvalidTokenError:
        return montar_resposta(401, "Token inválido")


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

    transacao_id = registrar_transacao(origem, destino, valor, "SUCESSO")

    return {
        "statusCode": 200,
        "body": json.dumps(
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
    }

def consultar_extrato(event):
    query_params = event.get("queryStringParameters") or {}
    conta_id = query_params.get("contaId")

    if not conta_id:
        return montar_resposta(400, "contaId é obrigatório")

    # busca os dados
    resposta = tabela_transacoes.scan()
    todas_transacoes = resposta.get("Items", [])

    # filtra
    extrato = []
    for transacao in todas_transacoes: 
        if transacao.get("origem") == conta_id or transacao.get("destino") == conta_id: 
            extrato.append(transacao)

    # ordenar por data mais recente
    extrato.sort(key=lambda x: x.get("criadoEm"), reverse=True)

    return {
        "statusCode": 200,
        "body": json.dumps(extrato, default=converter_decimal_para_json)
    }

def lambda_handler(event, context):
    try:
        # valida token
        resultado = validar_token(event)

        if "statusCode" in resultado:
            return resultado
        payload = resultado

        rota = event.get("rawPath")
        metodo = event.get("requestContext", {}).get("http", {}).get("method")

        if rota == "/saldo" and metodo == "GET":
            return consultar_saldo(event)
        if rota == "/transferencia" and metodo == "POST":
            return transferir(event)
        if rota == "/extrato" and metodo == "GET":
            return consultar_extrato(event)

        return montar_resposta(404, "Rota não encontrada")

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({
                "mensagem": "Erro interno",
                "erro": str(e)
            })
        }