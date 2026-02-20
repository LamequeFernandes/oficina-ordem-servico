from datetime import datetime

from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base


class UsuarioModel(Base):
    __tablename__ = 'usuario'

    usuario_id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    senha = Column(String(255), nullable=False)
    nome = Column(String(255), nullable=False)
    dta_cadastro = Column(DateTime, default=datetime.now)
    ativo = Column(Boolean, nullable=False, default=True)

    # Relacionamentos
    cliente = relationship(
        'ClienteModel', back_populates='usuario', uselist=False
    )
    funcionario = relationship(
        'FuncionarioModel', back_populates='usuario', uselist=False
    )


# CREATE TABLE `cliente` (
#   `cliente_id` int NOT NULL AUTO_INCREMENT,
#   `usuario_id` int NOT NULL,
#   `cpf_cnpj` varchar(14) NOT NULL,
#   `tipo_cliente` enum('PF','PJ') NOT NULL,
#   PRIMARY KEY (`cliente_id`),
#   UNIQUE KEY `usuario_id` (`usuario_id`),
#   UNIQUE KEY `cpf_cnpj` (`cpf_cnpj`),
#   CONSTRAINT `cliente_ibfk_1` FOREIGN KEY (`usuario_id`) 
#       REFERENCES `usuario` (`usuario_id`) ON DELETE CASCADE
# ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;


class ClienteModel(Base):
    __tablename__ = 'cliente'

    cliente_id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(
        Integer, ForeignKey('usuario.usuario_id', ondelete="CASCADE"), unique=True, nullable=False
    )
    cpf_cnpj = Column(String(14), unique=True, nullable=False)
    tipo_cliente = Column(
        Enum('PF', 'PJ', name='tipo_cliente'), nullable=False
    )

    # Relacionamentos
    usuario = relationship('UsuarioModel', back_populates='cliente')
    veiculos = relationship('VeiculoModel', back_populates='cliente')


class FuncionarioModel(Base):
    __tablename__ = 'funcionario'

    funcionario_id = Column(Integer, primary_key=True, autoincrement=True)
    usuario_id = Column(
        Integer, ForeignKey('usuario.usuario_id', ondelete="CASCADE"), unique=True, nullable=False
    )
    matricula = Column(Integer, unique=True, nullable=False)
    tipo_funcionario = Column(
        Enum('ADMINISTRADOR', 'MECANICO', name='tipo_funcionario'),
        nullable=False,
    )
    cpf = Column(String(11), unique=True, nullable=False)

    # Relacionamentos
    usuario = relationship('UsuarioModel', back_populates='funcionario')
    # orcamentos = relationship('OrcamentoModel', back_populates='funcionario')
