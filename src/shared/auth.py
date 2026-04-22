import jwt
from src.shared.config import SECRET
from src.shared.response import montar_resposta

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
        return payload
    except jwt.ExpiredSignatureError:
        return montar_resposta(401, "Token expirado")
    except jwt.InvalidTokenError:
        return montar_resposta(401, "Token inválido")