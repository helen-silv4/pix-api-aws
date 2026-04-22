from decimal import Decimal

# dynamo armazenar valores monetários como decimal para evitar problemas de precisão, 
# mas isso não é compatível com JSON, que espera tipos nativos como float. 
def converter_decimal_para_json(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    raise TypeError