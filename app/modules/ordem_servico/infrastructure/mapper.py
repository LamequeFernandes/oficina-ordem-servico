# from app.modules.orcamento.infrastructure.mapper import OrcamentoMapper
from app.modules.veiculo.domain.entities import Veiculo
from app.modules.ordem_servico.domain.entities import OrdemServico
from app.modules.ordem_servico.application.dto import OrdemServicoOutputDTO
from app.modules.veiculo.application.dto import VeiculoOutputDTO
from app.modules.ordem_servico.infrastructure.models import OrdemServicoModel


class OrdemServicoMapper:
    @staticmethod
    def entity_to_model(ordem_servico: OrdemServico) -> OrdemServicoModel:
        """Converte a Entidade para Modelo ORM."""
        return OrdemServicoModel(
            ordem_servico_id=ordem_servico.ordem_servico_id,
            veiculo_id=ordem_servico.veiculo_id, 
            status=ordem_servico.status.value,
            obsercacoes=ordem_servico.observacoes,
            dta_criacao=ordem_servico.dta_criacao,
            dta_finalizacao=ordem_servico.dta_finalizacao,
        )

    @staticmethod
    def model_to_entity(ordem_servico: OrdemServicoModel) -> OrdemServico:
        """Converte o Modelo ORM para Entidade."""
        return OrdemServico(
            ordem_servico_id=ordem_servico.ordem_servico_id,  # type: ignore
            veiculo_id=ordem_servico.veiculo_id,  # type: ignore
            veiculo=Veiculo(
                veiculo_id=ordem_servico.veiculo.veiculo_id,
                cliente_id=ordem_servico.veiculo.cliente_id,
                placa=ordem_servico.veiculo.placa,
                modelo=ordem_servico.veiculo.modelo,
                ano=ordem_servico.veiculo.ano,
                dta_cadastro=ordem_servico.veiculo.dta_cadastro,
            ),
            status=ordem_servico.status,  # type: ignore
            observacoes=ordem_servico.obsercacoes,  # type: ignore
            dta_criacao=ordem_servico.dta_criacao,  # type: ignore
            dta_finalizacao=ordem_servico.dta_finalizacao,  # type: ignore
            # orcamento=OrcamentoMapper.model_to_entity(ordem_servico.orcamento)
            # if ordem_servico.orcamento
            # else None,
        )

    @staticmethod
    def entity_to_output_dto(
        ordem_servico: OrdemServico,
    ) -> OrdemServicoOutputDTO:
        """Converte a Entidade para DTO de Saída."""
        return OrdemServicoOutputDTO(
            ordem_servico_id=ordem_servico.ordem_servico_id,  # type: ignore
            status=ordem_servico.status,
            veiculo=VeiculoOutputDTO(
                veiculo_id=ordem_servico.veiculo.veiculo_id,  # type: ignore
                placa=ordem_servico.veiculo.placa,
                modelo=ordem_servico.veiculo.modelo,
                ano=ordem_servico.veiculo.ano,
                cliente_id=ordem_servico.veiculo.cliente_id,
                dta_cadastro=ordem_servico.veiculo.dta_cadastro,
            )
            if ordem_servico.veiculo
            else None,
            dta_criacao=ordem_servico.dta_criacao,
            # orcamento=OrcamentoMapper.entity_to_output_dto(
            #     ordem_servico.orcamento
            # )
            # if ordem_servico.orcamento
            # else None,
            observacoes=ordem_servico.observacoes,
            dta_finalizacao=ordem_servico.dta_finalizacao,
        )
