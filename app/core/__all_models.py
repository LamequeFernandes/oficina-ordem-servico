from app.modules.usuario.infrastructure.models import (
    UsuarioModel, ClienteModel, FuncionarioModel
)  # noqa: F401
from app.modules.veiculo.infrastructure.models import VeiculoModel  # noqa: F401
from app.modules.ordem_servico.infrastructure.models import OrdemServicoModel  # noqa: F401
# from app.modules.orcamento.infrastructure.models import OrcamentoModel  # noqa: F401
# from app.modules.peca.infrastructure.models import TipoPecaModel, PecaModel  # noqa: F401
# from app.modules.servico.infrastructure.models import TipoServicoModel, ServicoModel  # noqa: F401

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

