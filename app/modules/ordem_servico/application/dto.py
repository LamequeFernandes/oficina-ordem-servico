from datetime import datetime
from pydantic import BaseModel

# from app.modules.orcamento.application.dto import OrcamentoOutputDTO
from app.modules.veiculo.application.dto import VeiculoOutputDTO

from app.modules.ordem_servico.domain.entities import StatusOrdemServico


class OrdemServicoOutputDTO(BaseModel):
    ordem_servico_id: int
    # veiculo_id: int
    veiculo: VeiculoOutputDTO
    status: StatusOrdemServico
    dta_criacao: datetime
    dta_finalizacao: datetime | None = None
    observacoes: str | None = None
    # orcamento: OrcamentoOutputDTO | None = None


class OrdemServicoCriacaoInputDTO(BaseModel):
    observacoes: str | None = None


class OrdemServicoAlteracaoStatusInputDTO(BaseModel):
    status: StatusOrdemServico


class StatusOrdemServicoOutputDTO(BaseModel):
    status: StatusOrdemServico