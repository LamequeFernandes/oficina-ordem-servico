from abc import ABC, abstractmethod
from app.modules.veiculo.domain.entities import Veiculo


class VeiculoRepositoryInterface(ABC):
    @abstractmethod
    def salvar(self, cliente_id: int, veiculo: Veiculo) -> Veiculo:
        pass

    @abstractmethod
    def buscar_por_placa(self, placa: str) -> Veiculo | None:
        pass

    @abstractmethod
    def buscar_por_id(self, veiculo_id: int) -> Veiculo | None:
        pass

    @abstractmethod
    def alterar(self, veiculo: Veiculo) -> Veiculo:
        pass

    @abstractmethod
    def remover(self, veiculo_id: int) -> None:
        pass
