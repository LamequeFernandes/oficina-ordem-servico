from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ValorDuplicadoError
from app.core.utils import obter_valor_e_key_duplicado_integrity_error
from app.modules.usuario.infrastructure.mapper import (
    ClienteMapper,
    FuncionarioMapper,
)
from app.modules.usuario.domain.entities import Cliente, Funcionario
from app.modules.usuario.infrastructure.models import (
    ClienteModel,
    UsuarioModel,
    FuncionarioModel,
)
from app.modules.usuario.application.interfaces import (
    ClienteRepositoryInterface,
    FuncionarioRepositoryInterface,
)


class ClienteRepository(ClienteRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, cliente: Cliente) -> Cliente:
        # Converter entidade para modelo ORM
        usuario_model = UsuarioModel(
            email=cliente.usuario.email,
            senha=cliente.usuario.senha,
            nome=cliente.usuario.nome,
        )
        cliente_model = ClienteModel(
            cpf_cnpj=cliente.cpf_cnpj,
            tipo_cliente=cliente.tipo,
            usuario=usuario_model,
        )

        self.db.add(cliente_model)
        self.db.commit()
        self.db.refresh(cliente_model)
        return ClienteMapper.model_to_entity(cliente_model)

    def buscar_por_id(self, id: int) -> Cliente | None:
        cliente_model = (
            self.db.query(ClienteModel)
            .filter(ClienteModel.cliente_id == id)
            .first()
        )
        if not cliente_model:
            return None
        return ClienteMapper.model_to_entity(cliente_model)

    def alterar(self, cliente: Cliente) -> Cliente | None:
        cliente_model = (
            self.db.query(ClienteModel)
            .filter(ClienteModel.cliente_id == cliente.cliente_id)
            .first()
        )
        if not cliente_model:
            return None

        cliente_model.cpf_cnpj = cliente.cpf_cnpj   # type: ignore
        cliente_model.tipo_cliente = cliente.tipo   # type: ignore
        cliente_model.usuario.email = cliente.usuario.email
        cliente_model.usuario.senha = cliente.usuario.senha
        cliente_model.usuario.nome = cliente.usuario.nome

        try:
            self.db.commit()
        except IntegrityError as e:
            (
                valor_duplicado,
                chave,
            ) = obter_valor_e_key_duplicado_integrity_error(e)
            self.db.rollback()
            raise ValorDuplicadoError(valor_duplicado, chave)

        self.db.refresh(cliente_model)
        return ClienteMapper.model_to_entity(cliente_model)

    def remover(self, cliente_id: int) -> None:
        cliente = (
            self.db.query(ClienteModel)
            .filter(ClienteModel.cliente_id == cliente_id)
            .first()
        )
        if cliente:
            self.db.delete(cliente)
            self.db.delete(cliente.usuario)
            self.db.commit()


class FuncionarioRepository(FuncionarioRepositoryInterface):
    def __init__(self, db: Session):
        self.db = db

    def salvar(self, funcionario: Funcionario) -> Funcionario:
        # Converter entidade para modelo ORM
        usuario_model = UsuarioModel(
            email=funcionario.usuario.email,
            senha=funcionario.usuario.senha,
            nome=funcionario.usuario.nome,
        )
        funcionario_model = FuncionarioModel(
            matricula=funcionario.matricula,
            tipo_funcionario=funcionario.tipo,
            usuario=usuario_model,
            cpf=funcionario.cpf,
        )

        self.db.add(funcionario_model)
        self.db.commit()
        self.db.refresh(funcionario_model)
        return FuncionarioMapper.model_to_entity(funcionario_model)

    def buscar_por_id(self, id: int) -> Funcionario | None:
        funcionario_model = (
            self.db.query(FuncionarioModel)
            .filter(FuncionarioModel.funcionario_id == id)
            .first()
        )
        if not funcionario_model:
            return None
        return FuncionarioMapper.model_to_entity(funcionario_model)

    def alterar(self, funcionario: Funcionario) -> Funcionario | None:
        funcionario_model = (
            self.db.query(FuncionarioModel)
            .filter(
                FuncionarioModel.funcionario_id == funcionario.funcionario_id
            )
            .first()
        )
        if not funcionario_model:
            return None

        funcionario_model.matricula = funcionario.matricula   # type: ignore
        funcionario_model.tipo_funcionario = funcionario.tipo   # type: ignore
        funcionario_model.usuario.email = funcionario.usuario.email
        funcionario_model.usuario.senha = funcionario.usuario.senha
        funcionario_model.usuario.nome = funcionario.usuario.nome

        self.db.commit()
        self.db.refresh(funcionario_model)
        return FuncionarioMapper.model_to_entity(funcionario_model)

    def remover(self, funcionario_id: int) -> None:
        funcionario = (
            self.db.query(FuncionarioModel)
            .filter(FuncionarioModel.funcionario_id == funcionario_id)
            .first()
        )
        if funcionario:
            self.db.delete(funcionario)
            self.db.delete(funcionario.usuario)
            self.db.commit()


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def buscar_por_email(self, email: str) -> UsuarioModel | None:
        return (
            self.db.query(UsuarioModel)
            .filter(UsuarioModel.email == email)
            .first()
        )

    def obter_tipo_usuario(self, usuario_id: int) -> str:
        # Verifica se é cliente
        cliente = (
            self.db.query(ClienteModel)
            .filter(ClienteModel.usuario_id == usuario_id)
            .first()
        )
        if cliente:
            return 'CLIENTE'

        # Verifica se é funcionário
        funcionario = (
            self.db.query(FuncionarioModel)
            .filter(FuncionarioModel.usuario_id == usuario_id)
            .first()
        )
        if funcionario:
            return funcionario.tipo_funcionario  # type: ignore #

        raise ValueError('Usuário não possui perfil associado')
