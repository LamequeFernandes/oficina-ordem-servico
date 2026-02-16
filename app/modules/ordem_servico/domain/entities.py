from enum import Enum, StrEnum
from dataclasses import dataclass
from datetime import datetime

# from app.modules.orcamento.domain.entities import Orcamento
from app.modules.veiculo.domain.entities import Veiculo


class StatusOrdemServico(StrEnum):
    RECEBIDA = 'RECEBIDA'
    EM_DIAGNOSTICO = 'EM_DIAGNOSTICO'
    AGUARDANDO_APROVACAO = 'AGUARDANDO_APROVACAO'
    EM_EXECUCAO = 'EM_EXECUCAO'
    FINALIZADA = 'FINALIZADA'
    ENTREGUE = 'ENTREGUE'


@dataclass
class OrdemServico:
    ordem_servico_id: int | None
    veiculo_id: int
    status: StatusOrdemServico
    veiculo: Veiculo | None = None
    observacoes: str | None = None
    dta_criacao: datetime = datetime.now()
    dta_finalizacao: datetime | None = None
    # orcamento: Orcamento | None = None
