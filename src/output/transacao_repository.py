import boto3
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from src.shared.config import TABELA_TRANSACOES

# conexão dynamo
dynamodb = boto3.resource("dynamodb")
tabela_transacoes = dynamodb.Table(TABELA_TRANSACOES)

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

def listar_transacoes():
    resposta = tabela_transacoes.scan()
    return resposta.get("Items", [])