from abc import ABC, abstractmethod
from app.modules.ordem_servico.domain.entities import (
    OrdemServico,
    StatusOrdemServico,
)


class OrdemServicoRepositoryInterface(ABC):
    @abstractmethod
    def salvar(self, ordem_servico: OrdemServico) -> OrdemServico:
        pass

    @abstractmethod
    def buscar_por_id(self, ordem_servico_id: int) -> OrdemServico | None:
        pass

    @abstractmethod
    def buscar_por_veiculo(self, veiculo_id: int) -> list[OrdemServico]:
        pass

    @abstractmethod
    def buscar_por_cliente(self, cliente_id: int) -> list[OrdemServico]:
        pass

    @abstractmethod
    def listar(self) -> list[OrdemServico]:
        pass

    @abstractmethod
    def alterar(self, ordem_servico: OrdemServico) -> OrdemServico:
        pass

    @abstractmethod
    def alterar_status(
        self, ordem_servico_id: int, status: StatusOrdemServico
    ) -> OrdemServico:
        pass

    @abstractmethod
    def remover(self, ordem_servico_id: int) -> None:
        pass
