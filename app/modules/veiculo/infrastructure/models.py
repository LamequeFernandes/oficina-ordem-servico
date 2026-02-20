from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class VeiculoModel(Base):
    __tablename__ = 'veiculo'

    veiculo_id = Column(Integer, primary_key=True, autoincrement=True)
    cliente_id = Column(
        Integer, ForeignKey('cliente.cliente_id', ondelete="CASCADE"), nullable=False
    )
    placa = Column(String(7), unique=True, nullable=False)
    modelo = Column(String(255), nullable=False)
    ano = Column(Integer, nullable=False)
    dta_cadastro = Column(DateTime, default=datetime.now)

    # Relacionamentos
    cliente = relationship(
        'ClienteModel', back_populates='veiculos', uselist=False
    )
    ordens_servico = relationship(
        'OrdemServicoModel', back_populates='veiculo'
    )
