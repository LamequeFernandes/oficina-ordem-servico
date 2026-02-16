from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    ApenasFuncionariosProprietariosError,
    ValorDuplicadoError,
    VeiculoNotFoundError,
)
from app.core.utils import obter_valor_e_key_duplicado_integrity_error
from app.modules.usuario.infrastructure.models import UsuarioModel
from app.modules.veiculo.application.dto import (
    VeiculoInputDTO,
    VeiculoOutputDTO,
)
from app.modules.veiculo.infrastructure.mapper import VeiculoMapper

from app.modules.veiculo.domain.entities import Veiculo
from app.modules.veiculo.infrastructure.repositories import VeiculoRepository


class CriarVeiculoUseCase:
    def __init__(self, db: Session):
        self.repo = VeiculoRepository(db)

    def execute(
        self, cliente_id: int, dados: VeiculoInputDTO
    ) -> VeiculoOutputDTO:
        veiculo = Veiculo(
            veiculo_id=None,
            cliente_id=cliente_id,  # Associa ao cliente autenticado
            placa=dados.placa,
            modelo=dados.modelo,
            ano=dados.ano,
        )
        try:
            veiculo_salvo = self.repo.salvar(cliente_id, veiculo)
        except IntegrityError as e:
            (
                valor_duplicado,
                chave,
            ) = obter_valor_e_key_duplicado_integrity_error(e)
            raise ValorDuplicadoError(valor_duplicado, chave)
        return VeiculoMapper.entity_to_output_dto(veiculo_salvo)


class ConsultarVeiculoUseCase:
    def __init__(self, db: Session, usuario_logado: UsuarioModel):
        self.repo = VeiculoRepository(db)
        self.usuario_logado = usuario_logado

    def usuario_tem_permissao(self, veiculo: Veiculo) -> bool:
        if self.usuario_logado.funcionario:
            return True
        return veiculo.cliente_id == self.usuario_logado.cliente.cliente_id

    def execute(self, veiculo_id: int) -> VeiculoOutputDTO | None:
        veiculo = self.repo.buscar_por_id(veiculo_id)
        if not veiculo:
            raise VeiculoNotFoundError(veiculo_id)
        if not self.usuario_tem_permissao(veiculo):
            raise ApenasFuncionariosProprietariosError
        return VeiculoMapper.entity_to_output_dto(veiculo)


class AlterarVeiculoUseCase:
    def __init__(self, db: Session, usuario_logado: UsuarioModel):
        self.repo = VeiculoRepository(db)
        self.usuario_logado = usuario_logado

    def usuario_tem_permissao(self, veiculo: Veiculo) -> bool:
        if self.usuario_logado.funcionario:
            return True
        return veiculo.cliente_id == self.usuario_logado.cliente.cliente_id

    def execute(
        self, veiculo_id: int, dados: VeiculoInputDTO
    ) -> VeiculoOutputDTO:
        veiculo = self.repo.buscar_por_id(veiculo_id)

        if not veiculo:
            raise VeiculoNotFoundError(veiculo_id)
        if not self.usuario_tem_permissao(veiculo):
            raise ApenasFuncionariosProprietariosError

        veiculo.placa = dados.placa
        veiculo.modelo = dados.modelo
        veiculo.ano = dados.ano

        try:
            veiculo_atualizado = self.repo.alterar(veiculo)
        except IntegrityError as e:
            (
                valor_duplicado,
                chave,
            ) = obter_valor_e_key_duplicado_integrity_error(e)
            raise ValorDuplicadoError(valor_duplicado, chave)
        return VeiculoMapper.entity_to_output_dto(veiculo_atualizado)


class RemoverVeiculoUseCase:
    def __init__(self, db: Session, usuario_logado: UsuarioModel):
        self.repo = VeiculoRepository(db)
        self.usuario_logado = usuario_logado

    def usuario_tem_permissao(self, veiculo: Veiculo) -> bool:
        if self.usuario_logado.funcionario:
            return True
        return veiculo.cliente_id == self.usuario_logado.cliente.cliente_id

    def execute(self, veiculo_id: int) -> None:
        veiculo = self.repo.buscar_por_id(veiculo_id)
        if not veiculo:
            raise VeiculoNotFoundError(veiculo_id)
        if not self.usuario_tem_permissao(veiculo):
            raise ApenasFuncionariosProprietariosError
        self.repo.remover(veiculo_id)
