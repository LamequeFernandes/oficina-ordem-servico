from sqlalchemy.orm import Session
from datetime import datetime

from app.modules.usuario.infrastructure.models import ClienteModel, UsuarioModel
from app.modules.ordem_servico.domain.entities import OrdemServico
from .dto import (
    OrdemServicoCriacaoInputDTO,
    OrdemServicoOutputDTO,
    StatusOrdemServico,
    StatusOrdemServicoOutputDTO,
)
from app.modules.ordem_servico.infrastructure.mapper import OrdemServicoMapper
from app.modules.ordem_servico.infrastructure.repositories import (
    OrdemServicoRepository,
)
from app.core.exceptions import OrdemServicoNotFoundError, StatusOSInvalido

from app.core.utils import (
    adicionar_em_fila_execucao,
    iniciar_diagnostico_fila_execucao,
    finalizar_diagnostico_fila_execucao,
    iniciar_execucao_fila_execucao,
    finalizar_execucao_fila_execucao,
)


class CriarOrdemServicoUseCase:
    def __init__(self, db: Session, cliente_logado: ClienteModel):
        self.repo = OrdemServicoRepository(db)
        self.cliente_logado = cliente_logado

    def validar_cliente_dono_veiculo(self, veiculo_id: int):
        if veiculo_id not in [veiculo.veiculo_id for veiculo in self.cliente_logado.veiculos]:
            raise ValueError("Cliente não é o proprietário do veículo.")

    def execute(
        self, veiculo_id: int, dados: OrdemServicoCriacaoInputDTO
    ) -> OrdemServicoOutputDTO:
        ordem_servico = OrdemServico(
            ordem_servico_id=None,
            veiculo_id=veiculo_id,
            status=StatusOrdemServico.RECEBIDA,
            observacoes=dados.observacoes,
        )
        ordem_servico_salva = self.repo.salvar(ordem_servico)
        adicionar_em_fila_execucao(ordem_servico_salva.ordem_servico_id)

        return OrdemServicoMapper.entity_to_output_dto(ordem_servico_salva)


class AlterarStatusOrdemServicoUseCase:
    def __init__(self, db: Session, usuario_id: int):
        self.repo = OrdemServicoRepository(db)
        self.usuario_id = usuario_id

    def validar_mudanca_para_aguardando_aprovacao(self, status_novo: StatusOrdemServico, ordem_servico: OrdemServico):
        if status_novo == StatusOrdemServico.AGUARDANDO_APROVACAO:
            if not ordem_servico.orcamento.servicos: # type: ignore
                raise ValueError(
                    'A ordem de serviço não possui serviços vinculados.'
                )

    def validar_alteracao_status(
        self, novo_status: StatusOrdemServico, ordem_servico: OrdemServico
    ):
        status_atual = ordem_servico.status

        if (
            status_atual == StatusOrdemServico.RECEBIDA
            and novo_status != StatusOrdemServico.EM_DIAGNOSTICO
        ):
            raise StatusOSInvalido(
                status_atual, StatusOrdemServico.EM_DIAGNOSTICO
            )
        if (
            status_atual == StatusOrdemServico.EM_DIAGNOSTICO
            and novo_status != StatusOrdemServico.AGUARDANDO_APROVACAO
        ):
            raise StatusOSInvalido(
                status_atual, StatusOrdemServico.AGUARDANDO_APROVACAO
            )
        if (
            status_atual == StatusOrdemServico.AGUARDANDO_APROVACAO
            and novo_status != StatusOrdemServico.EM_EXECUCAO
        ):
            raise StatusOSInvalido(
                status_atual, StatusOrdemServico.EM_EXECUCAO
            )
        if (
            status_atual == StatusOrdemServico.EM_EXECUCAO
            and novo_status != StatusOrdemServico.FINALIZADA
        ):
            raise StatusOSInvalido(status_atual, StatusOrdemServico.FINALIZADA)
        if (
            status_atual == StatusOrdemServico.FINALIZADA
            and novo_status != StatusOrdemServico.ENTREGUE
        ):
            raise StatusOSInvalido(status_atual, StatusOrdemServico.ENTREGUE)
        if status_atual == StatusOrdemServico.ENTREGUE:
            raise ValueError(
                'A Ordem de Serviço já foi entregue e não pode ser alterada.'
            )

    def execute(
        self, ordem_servico_id: int, status: StatusOrdemServico
    ) -> OrdemServicoOutputDTO:
        ordem_servico = self.repo.buscar_por_id(ordem_servico_id)
        if not ordem_servico:
            raise OrdemServicoNotFoundError

        self.validar_alteracao_status(status, ordem_servico)
        self.validar_mudanca_para_aguardando_aprovacao(status, ordem_servico)

        if status == StatusOrdemServico.ENTREGUE:
            ordem_servico.status = status.value  # type: ignore
            ordem_servico.dta_finalizacao = datetime.now()  # type: ignore
            ordem_servico_atualizada = self.repo.alterar(ordem_servico)
            finalizar_execucao_fila_execucao(ordem_servico_id, "Reparo finalizado, ordem de serviço entregue ao cliente.")
        else:
            ordem_servico_atualizada = self.repo.alterar_status(
                ordem_servico_id, status
            )

        if not ordem_servico_atualizada:
            raise OrdemServicoNotFoundError
        
        if status == StatusOrdemServico.EM_DIAGNOSTICO:
            iniciar_diagnostico_fila_execucao(ordem_servico_id, self.usuario_id)
        
        if status == StatusOrdemServico.AGUARDANDO_APROVACAO:
            finalizar_diagnostico_fila_execucao(ordem_servico_id, "Diagnóstico concluído, aguardando aprovação do cliente.")

        if status == StatusOrdemServico.EM_EXECUCAO:
            iniciar_execucao_fila_execucao(ordem_servico_id, self.usuario_id)
        

        return OrdemServicoMapper.entity_to_output_dto(
            ordem_servico_atualizada
        )


class ConsultarOrdemServicoUseCase:
    def __init__(self, db: Session, usuario_logado: UsuarioModel):
        self.repo = OrdemServicoRepository(db)
        self.usuario_logado = usuario_logado

    def valida_vinculo_com_veiculo(
        self, usuario_logado: UsuarioModel, ordem_servico: OrdemServico
    ):
        if usuario_logado.cliente:
            if (
                not usuario_logado.cliente.cliente_id
                == ordem_servico.veiculo.cliente_id  # type: ignore
            ):
                raise ValueError(
                    'O cliente não é o proprietário do veículo vinculado a esta ordem de serviço.'
                )

    def execute_por_id(self, ordem_servico_id: int) -> OrdemServicoOutputDTO:
        ordem_servico = self.repo.buscar_por_id(ordem_servico_id)
        if not ordem_servico:
            raise OrdemServicoNotFoundError
        self.valida_vinculo_com_veiculo(self.usuario_logado, ordem_servico)
        return OrdemServicoMapper.entity_to_output_dto(ordem_servico)

    def execute_por_veiculo(
        self, veiculo_id: int
    ) -> list[OrdemServicoOutputDTO]:
        ordens_servico = self.repo.buscar_por_veiculo(veiculo_id)
        return [
            OrdemServicoMapper.entity_to_output_dto(ordem)
            for ordem in ordens_servico
        ]

    def execute_por_cliente(
        self, cliente_id: int
    ) -> list[OrdemServicoOutputDTO]:
        ordens_servico = self.repo.buscar_por_cliente(cliente_id)
        return [
            OrdemServicoMapper.entity_to_output_dto(ordem)
            for ordem in ordens_servico
        ]

    def execute_listar(self) -> list[OrdemServicoOutputDTO]:
        ordens_servico = self.repo.listar()
        return [
            OrdemServicoMapper.entity_to_output_dto(ordem)
            for ordem in ordens_servico
        ]
    
    def execute_obter_status(self, ordem_servico_id: int) -> StatusOrdemServicoOutputDTO:
        ordem_servico = self.repo.buscar_por_id(ordem_servico_id)
        if not ordem_servico:
            raise OrdemServicoNotFoundError
        self.valida_vinculo_com_veiculo(self.usuario_logado, ordem_servico)
        return StatusOrdemServicoOutputDTO(status=ordem_servico.status)  # type: ignore


class RemoverServicoUseCase:
    def __init__(self, db: Session, admin_usuario: UsuarioModel):
        self.repo = OrdemServicoRepository(db)
        self.admin_usuario = admin_usuario

    def valida_vinculo_orcamento(self, ordem_servico: OrdemServico):
        if ordem_servico.orcamento:
            raise ValueError(
                'Não é possível remover uma Ordem de Serviço que possui um orçamento vinculado.'
            )

    def execute(self, ordem_servico_id: int) -> None:
        ordem_servico = self.repo.buscar_por_id(ordem_servico_id)
        if not ordem_servico:
            raise OrdemServicoNotFoundError
        self.valida_vinculo_orcamento(ordem_servico)
        self.repo.remover(ordem_servico_id)
