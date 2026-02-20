from sqlalchemy.orm import Session
from app.core.exceptions import NaoEncontradoError, VeiculoNotFoundError
from app.modules.veiculo.domain.entities import Veiculo
from app.modules.veiculo.infrastructure.mapper import VeiculoMapper
from app.modules.veiculo.infrastructure.models import VeiculoModel
from app.modules.veiculo.application.interfaces import (
    VeiculoRepositoryInterface,
)


class VeiculoRepository(VeiculoRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, cliente_id: int, veiculo: Veiculo) -> Veiculo:
        veiculo_model = VeiculoModel(
            cliente_id=cliente_id,
            placa=veiculo.placa,
            modelo=veiculo.modelo,
            ano=veiculo.ano,
        )

        self.db.add(veiculo_model)
        self.db.commit()
        self.db.refresh(veiculo_model)

        return VeiculoMapper.model_to_entity(veiculo_model)

    def buscar_por_placa(self, placa: str):
        veiculo_model = (
            self.db.query(VeiculoModel)
            .filter(VeiculoModel.placa == placa)
            .first()
        )
        return (
            VeiculoMapper.model_to_entity(veiculo_model)
            if veiculo_model
            else None
        )

    def buscar_por_id(self, veiculo_id: int) -> Veiculo | None:
        veiculo_model = (
            self.db.query(VeiculoModel)
            .filter(VeiculoModel.veiculo_id == veiculo_id)
            .first()
        )
        return (
            VeiculoMapper.model_to_entity(veiculo_model)
            if veiculo_model
            else None
        )

    def alterar(self, veiculo: Veiculo) -> Veiculo:
        veiculo_model = (
            self.db.query(VeiculoModel)
            .filter(VeiculoModel.veiculo_id == veiculo.veiculo_id)
            .first()
        )

        if not veiculo_model:
            raise VeiculoNotFoundError(veiculo.veiculo_id)

        veiculo_model.placa = veiculo.placa   # type: ignore
        veiculo_model.modelo = veiculo.modelo   # type: ignore
        veiculo_model.ano = veiculo.ano   # type: ignore

        self.db.merge(veiculo_model)
        self.db.commit()
        self.db.refresh(veiculo_model)
        return VeiculoMapper.model_to_entity(veiculo_model)

    def remover(self, veiculo_id: int) -> None:
        veiculo_model = (
            self.db.query(VeiculoModel)
            .filter(VeiculoModel.veiculo_id == veiculo_id)
            .first()
        )
        if not veiculo_model:
            raise VeiculoNotFoundError(veiculo_id)
        self.db.delete(veiculo_model)
        self.db.commit()
