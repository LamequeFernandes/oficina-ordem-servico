from pydantic import BaseModel, validator

from app.core.exceptions import (
    TamanhoCNPJInvalidoError,
    TamanhoCPFInvalidoError,
)


class CPF(BaseModel):
    valor: str

    @validator('valor')
    def validar_cpf(cls, v):
        if len(v) != 11 or not v.isdigit():
            raise TamanhoCPFInvalidoError
        # TODO
        # Adicione a validação de dígitos verificadores aqui (ex: módulo 11)
        return v


class CNPJ(BaseModel):
    valor: str

    @validator('valor')
    def validar_cnpj(cls, v):
        if len(v) != 14 or not v.isdigit():
            raise TamanhoCNPJInvalidoError
        # TODO
        # Adicione a validação de dígitos verificadores
        return v
