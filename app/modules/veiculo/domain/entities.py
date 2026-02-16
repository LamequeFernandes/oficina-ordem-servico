from dataclasses import dataclass
from datetime import datetime

from app.modules.veiculo.domain.value_objects import Placa


@dataclass
class Veiculo:
    veiculo_id: int | None
    cliente_id: int
    placa: str
    modelo: str
    ano: int
    dta_cadastro: datetime = datetime.now()

    def __post_init__(self):
        self.placa = self.placa.upper()
        Placa(valor=self.placa)   # valida placa
