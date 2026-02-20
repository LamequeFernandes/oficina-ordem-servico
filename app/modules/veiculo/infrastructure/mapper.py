from app.modules.usuario.domain.entities import Cliente
from app.modules.veiculo.domain.entities import Veiculo
from app.modules.veiculo.application.dto import VeiculoOutputDTO
from app.modules.veiculo.infrastructure.models import VeiculoModel


class VeiculoMapper:
    @staticmethod
    def entity_to_model(veiculo: Veiculo) -> VeiculoModel:
        return VeiculoModel(
            veiculo_id=veiculo.veiculo_id,
            cliente_id=veiculo.cliente_id,
            placa=veiculo.placa,
            modelo=veiculo.modelo,
            ano=veiculo.ano,
            dta_cadastro=veiculo.dta_cadastro,
        )

    @staticmethod
    def model_to_entity(veiculo_model: VeiculoModel) -> Veiculo:
        return Veiculo(
            veiculo_id=veiculo_model.veiculo_id,  # type: ignore
            cliente_id=veiculo_model.cliente_id,  # type: ignore
            placa=veiculo_model.placa,  # type: ignore
            modelo=veiculo_model.modelo,  # type: ignore
            ano=veiculo_model.ano,  # type: ignore
            dta_cadastro=veiculo_model.dta_cadastro,  # type: ignore
        )

    @staticmethod
    def entity_to_output_dto(veiculo: Veiculo) -> VeiculoOutputDTO:
        return VeiculoOutputDTO(
            veiculo_id=veiculo.veiculo_id,  # type: ignore
            cliente_id=veiculo.cliente_id,
            placa=veiculo.placa,
            modelo=veiculo.modelo,
            ano=veiculo.ano,
            dta_cadastro=veiculo.dta_cadastro,
        )
