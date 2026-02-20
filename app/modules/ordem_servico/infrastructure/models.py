from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class OrdemServicoModel(Base):
    __tablename__ = 'ordem_servico'

    ordem_servico_id = Column(Integer, primary_key=True, autoincrement=True)
    veiculo_id = Column(
        Integer, ForeignKey('veiculo.veiculo_id', ondelete="CASCADE"), nullable=False
    )
    status = Column(
        Enum(
            'RECEBIDA',
            'EM_DIAGNOSTICO',
            'AGUARDANDO_APROVACAO',
            'EM_EXECUCAO',
            'FINALIZADA',
            'ENTREGUE',
            name='status_ordem_servico',
        ),
        nullable=False,
    )
    obsercacoes = Column(String(255), nullable=True)
    dta_criacao = Column(DateTime, default=datetime.now)
    dta_finalizacao = Column(DateTime, nullable=True)

    # Relacionamentos
    veiculo = relationship('VeiculoModel', back_populates='ordens_servico')
    # orcamento = relationship(
    #     'OrcamentoModel', back_populates='ordem_servico', uselist=False
    # )
