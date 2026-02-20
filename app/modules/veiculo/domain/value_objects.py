import re
from pydantic import BaseModel, validator

from app.core.exceptions import PadraoPlacaIncorretoError


class Placa(BaseModel):
    valor: str

    @validator('valor')
    def validar_placa(cls, v):
        if len(v) != 7:
            raise PadraoPlacaIncorretoError
        if bool(re.search(r'\d', v[:3])):
            raise PadraoPlacaIncorretoError
        if not v[3].isdigit() or not v[5:].isdigit():
            raise PadraoPlacaIncorretoError
        return v
