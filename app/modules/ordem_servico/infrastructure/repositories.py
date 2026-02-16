from sqlalchemy.orm import Session
from app.modules.ordem_servico.application.dto import (
    OrdemServicoCriacaoInputDTO,
)
from app.modules.ordem_servico.domain.entities import (
    OrdemServico,
    StatusOrdemServico,
)
from app.modules.veiculo.domain.entities import Veiculo
from app.modules.ordem_servico.infrastructure.models import OrdemServicoModel
from app.modules.ordem_servico.application.interfaces import (
    OrdemServicoRepositoryInterface,
)
from app.modules.ordem_servico.infrastructure.mapper import OrdemServicoMapper
from app.modules.veiculo.infrastructure.models import VeiculoModel


class OrdemServicoRepository(OrdemServicoRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, ordem_servico: OrdemServico) -> OrdemServico:
        ordem_servico_model = OrdemServicoMapper.entity_to_model(ordem_servico)

        self.db.add(ordem_servico_model)
        self.db.commit()
        self.db.refresh(ordem_servico_model)

        return OrdemServicoMapper.model_to_entity(ordem_servico_model)

    def buscar_por_id(self, ordem_servico_id: int) -> OrdemServico | None:
        ordem_servico = (
            self.db.query(OrdemServicoModel)
            .filter(OrdemServicoModel.ordem_servico_id == ordem_servico_id)
            .first()
        )

        if not ordem_servico:
            return None
        return OrdemServicoMapper.model_to_entity(ordem_servico)

    def buscar_por_veiculo(self, veiculo_id: int) -> list[OrdemServico]:
        ordens_servico = (
            self.db.query(OrdemServicoModel)
            .filter(OrdemServicoModel.veiculo_id == veiculo_id)
            .all()
        )

        if not ordens_servico:
            return []
        return [
            OrdemServicoMapper.model_to_entity(ordem_servico)
            for ordem_servico in ordens_servico
        ]

    def buscar_por_cliente(self, cliente_id: int) -> list[OrdemServico]:
        ordens_servico = (
            self.db.query(OrdemServicoModel)
            .join(
                VeiculoModel,
                OrdemServicoModel.veiculo_id == VeiculoModel.veiculo_id,
            )
            .filter(VeiculoModel.cliente_id == cliente_id)
            .all()
        )

        if not ordens_servico:
            return []
        return [
            OrdemServicoMapper.model_to_entity(ordem_servico)
            for ordem_servico in ordens_servico
        ]

    def listar(self) -> list[OrdemServico]:
        ordens_servico = (
            self.db.query(OrdemServicoModel)
            .order_by(OrdemServicoModel.dta_criacao.asc())
            .all()
        )

        ordens_servico_ordenadas = [
            OrdemServicoMapper.model_to_entity(ordem_servico)
            for ordem_servico in ordens_servico
            if ordem_servico.status == StatusOrdemServico.EM_EXECUCAO.value # type: ignore
        ]
        ordens_servico_ordenadas += [
            OrdemServicoMapper.model_to_entity(ordem_servico)
            for ordem_servico in ordens_servico
            if ordem_servico.status == StatusOrdemServico.AGUARDANDO_APROVACAO.value  # type: ignore
        ]
        ordens_servico_ordenadas += [
            OrdemServicoMapper.model_to_entity(ordem_servico)
            for ordem_servico in ordens_servico
            if ordem_servico.status == StatusOrdemServico.EM_DIAGNOSTICO.value  # type: ignore
        ]
        ordens_servico_ordenadas += [
            OrdemServicoMapper.model_to_entity(ordem_servico)
            for ordem_servico in ordens_servico
            if ordem_servico.status == StatusOrdemServico.RECEBIDA.value  # type: ignore
        ]
        return ordens_servico_ordenadas

    def alterar(self, ordem_servico: OrdemServico) -> OrdemServico:
        ordem_servico_model = self.db.query(OrdemServicoModel).filter(
            OrdemServicoModel.ordem_servico_id == ordem_servico.ordem_servico_id
        ).first()

        ordem_servico_model.dta_finalizacao = ordem_servico.dta_finalizacao # type: ignore
        ordem_servico_model.status = ordem_servico.status  # type: ignore

        self.db.merge(ordem_servico_model)
        self.db.commit()
        self.db.refresh(ordem_servico_model)
        return OrdemServicoMapper.model_to_entity(ordem_servico_model)

    def alterar_status(
        self, ordem_servico_id: int, status: StatusOrdemServico
    ) -> OrdemServico:
        ordem_servico = (
            self.db.query(OrdemServicoModel)
            .filter(OrdemServicoModel.ordem_servico_id == ordem_servico_id)
            .first()
        )

        ordem_servico.status = status.value  # type: ignore
        self.db.commit()
        self.db.refresh(ordem_servico)

        return OrdemServicoMapper.model_to_entity(ordem_servico)

    def remover(self, ordem_servico_id: int) -> None:
        ordem_servico = (
            self.db.query(OrdemServicoModel)
            .filter(OrdemServicoModel.ordem_servico_id == ordem_servico_id)
            .first()
        )
        self.db.delete(ordem_servico)
        self.db.commit()
