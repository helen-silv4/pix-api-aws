import boto3
from shared.config import TABELA_CONTAS

# conexão dynamo
dynamodb = boto3.resource("dynamodb")
tabela_contas = dynamodb.Table(TABELA_CONTAS)

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