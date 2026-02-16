from abc import ABC, abstractmethod
from app.modules.usuario.domain.entities import Cliente, Funcionario


class ClienteRepositoryInterface(ABC):
    @abstractmethod
    def salvar(self, cliente: Cliente) -> Cliente:
        pass

    @abstractmethod
    def buscar_por_id(self, id: int) -> Cliente | None:
        pass

    @abstractmethod
    def alterar(self, cliente: Cliente) -> Cliente | None:
        pass

    @abstractmethod
    def remover(self, cliente_id: int) -> None:
        pass


class FuncionarioRepositoryInterface(ABC):
    @abstractmethod
    def salvar(self, funcionario: Funcionario) -> Funcionario:
        pass

    @abstractmethod
    def buscar_por_id(self, id: int) -> Funcionario | None:
        pass

    @abstractmethod
    def alterar(self, funcionario: Funcionario) -> Funcionario | None:
        pass

    @abstractmethod
    def remover(self, funcionario_id: int) -> None:
        pass
