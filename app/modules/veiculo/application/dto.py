from pydantic import BaseModel
from datetime import datetime


class VeiculoInputDTO(BaseModel):
    placa: str
    modelo: str
    ano: int


class VeiculoOutputDTO(BaseModel):
    veiculo_id: int
    placa: str
    modelo: str
    ano: int
    cliente_id: int
    dta_cadastro: datetime
