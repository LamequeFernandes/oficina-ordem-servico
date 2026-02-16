from sqlalchemy.exc import IntegrityError

import re


def obter_valor_e_key_duplicado_integrity_error(e: IntegrityError):
    """
    Extrai o valor duplicado de uma exceção IntegrityError.
    """
    msg = str(e.orig)

    match = re.search(r"Duplicate entry '(.+?)' for key '(.+?)'", msg)

    if not match:
        raise e
    valor_duplicado = match.group(1)
    chave = match.group(2).split('.')[-1]

    return valor_duplicado, chave
