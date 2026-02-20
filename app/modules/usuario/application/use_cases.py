from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    ClienteNotFoundError,
    FuncionarioNotFoundError,
    SomenteProprietarioDoUsuarioError,
    SomenteProprietarioOuAdminError,
    ValorDuplicadoError,
)
from app.core.security import (
    criar_hash_senha,
    criar_token_jwt,
    verificar_senha,
)
from app.core.utils import obter_valor_e_key_duplicado_integrity_error
from app.modules.usuario.infrastructure.mapper import (
    ClienteMapper,
    FuncionarioMapper,
)
from app.modules.usuario.infrastructure.models import (
    ClienteModel,
    UsuarioModel,
)
from app.modules.usuario.infrastructure.repositories import (
    AuthRepository,
    ClienteRepository,
    FuncionarioRepository,
)
from app.modules.usuario.domain.entities import Cliente, Usuario, Funcionario
from .dto import (
    ClienteInputDTO,
    ClienteOutputDTO,
    FuncionarioInputDTO,
    FuncionarioOutputDTO,
    LoginOutputDTO,
)


class CriarClienteUseCase:
    def __init__(self, db: Session):
        self.repo = ClienteRepository(db)

    def executar(self, dados: ClienteInputDTO) -> ClienteOutputDTO:
        senha_hash = criar_hash_senha(dados.senha)
        usuario = Usuario(
            usuario_id=None,
            email=dados.email,
            senha=senha_hash,
            nome=dados.nome,
        )
        cliente = Cliente(
            cliente_id=None,
            usuario=usuario,
            cpf_cnpj=dados.cpf_cnpj,
            tipo=dados.tipo,
        )

        try:
            cliente_salvo = self.repo.salvar(cliente)
        except IntegrityError as e:
            (
                valor_duplicado,
                chave,
            ) = obter_valor_e_key_duplicado_integrity_error(e)
            raise ValorDuplicadoError(valor_duplicado, chave)
        return ClienteMapper.entity_to_output_dto(cliente_salvo)


class AlterarClienteUseCase:
    def __init__(self, db: Session, cliente_logado: ClienteModel):
        self.repo = ClienteRepository(db)
        self.cliente_logado = cliente_logado

    def executar(
        self, cliente_id: int, dados: ClienteInputDTO
    ) -> ClienteOutputDTO:
        if self.cliente_logado.cliente_id != cliente_id:   # type: ignore
            raise SomenteProprietarioDoUsuarioError

        cliente = self.repo.buscar_por_id(cliente_id)
        if not cliente:
            raise ClienteNotFoundError(cliente_id)

        cliente.usuario.email = dados.email
        cliente.usuario.senha = criar_hash_senha(dados.senha)
        cliente.usuario.nome = dados.nome
        cliente.cpf_cnpj = dados.cpf_cnpj
        cliente.tipo = dados.tipo

        try:
            cliente_alterado = self.repo.alterar(cliente)
        except IntegrityError as e:
            (
                valor_duplicado,
                chave,
            ) = obter_valor_e_key_duplicado_integrity_error(e)
            raise ValorDuplicadoError(valor_duplicado, chave)
        return ClienteMapper.entity_to_output_dto(
            cliente_alterado  # type: ignore
        )


class RemoverClienteUseCase:
    def __init__(self, db: Session, usuario_logado: UsuarioModel):
        self.repo = ClienteRepository(db)
        self.usuario_logado = usuario_logado

    def usuario_logado_eh_admin(self) -> bool:
        if self.usuario_logado.funcionario:
            return (
                self.usuario_logado.funcionario.tipo_funcionario
                == 'ADMINISTRADOR'
            )   # type: ignore
        return False

    def usuario_logado_eh_proprietario_conta(self, cliente_id: int) -> bool:
        if self.usuario_logado.cliente:
            return self.usuario_logado.cliente.cliente_id == cliente_id
        return False
    
    def cliente_possui_veiculo_vinculado(self) -> bool:
        if self.usuario_logado.cliente:
            return bool(self.usuario_logado.cliente.veiculos)
        return False

    def executar(self, cliente_id: int) -> None:
        if (
            not self.usuario_logado_eh_proprietario_conta(cliente_id)
            and not self.usuario_logado_eh_admin()
        ):
            raise SomenteProprietarioOuAdminError

        cliente = self.repo.buscar_por_id(cliente_id)
        if not cliente:
            raise ClienteNotFoundError(cliente_id)

        if self.cliente_possui_veiculo_vinculado():
            raise ValueError("O Cliente possui veículos vinculados, primeiro remova os veículos relacionados.")

        self.repo.remover(cliente_id)


class ConsultarClienteUseCase:
    def __init__(self, db: Session):
        self.repo = ClienteRepository(db)

    def executar_consulta_por_id(self, cliente_id: int) -> ClienteOutputDTO:
        cliente = self.repo.buscar_por_id(cliente_id)
        if not cliente:
            raise ClienteNotFoundError(cliente_id)

        return ClienteMapper.entity_to_output_dto(cliente)


class CriarFuncionarioUseCase:
    def __init__(self, db: Session):
        self.repo = FuncionarioRepository(db)

    def executar(self, dados: FuncionarioInputDTO) -> FuncionarioOutputDTO:
        senha_hash = criar_hash_senha(dados.senha)
        usuario = Usuario(
            usuario_id=None,
            email=dados.email,
            senha=senha_hash,
            nome=dados.nome,
        )
        funcionario = Funcionario(
            funcionario_id=None,
            usuario=usuario,
            matricula=dados.matricula,
            tipo=dados.tipo,
            cpf=dados.cpf,
        )

        funcionario_salvo = self.repo.salvar(funcionario)
        return FuncionarioMapper.entity_to_output_dto(funcionario_salvo)


class ConsultarFuncionarioUseCase:
    def __init__(self, db: Session):
        self.repo = FuncionarioRepository(db)

    def executar_consulta_por_id(
        self, funcionario_id: int
    ) -> FuncionarioOutputDTO:
        funcionario = self.repo.buscar_por_id(funcionario_id)
        if not funcionario:
            raise FuncionarioNotFoundError(funcionario_id)
        return FuncionarioMapper.entity_to_output_dto(funcionario)


class AlterarFuncionarioUseCase:
    def __init__(self, db: Session, usuario_logado: UsuarioModel):
        self.repo = FuncionarioRepository(db)
        self.usuario_logado = usuario_logado

    def usuario_logado_eh_admin(self) -> bool:
        if self.usuario_logado.funcionario:
            return (
                self.usuario_logado.funcionario.tipo_funcionario
                == 'ADMINISTRADOR'
            )
        return False

    def usuario_logado_eh_proprietario_conta(
        self, funcionario_id: int
    ) -> bool:
        if self.usuario_logado.funcionario:
            return (
                self.usuario_logado.funcionario.funcionario_id
                == funcionario_id
            )
        return False

    def executar(
        self, funcionario_id: int, dados: FuncionarioInputDTO
    ) -> FuncionarioOutputDTO:
        if (
            not self.usuario_logado_eh_admin()
            and not self.usuario_logado_eh_proprietario_conta(funcionario_id)
        ):
            raise SomenteProprietarioOuAdminError

        funcionario = self.repo.buscar_por_id(funcionario_id)
        if not funcionario:
            raise FuncionarioNotFoundError(funcionario_id)

        funcionario.matricula = dados.matricula
        funcionario.tipo = dados.tipo
        funcionario.usuario.email = dados.email
        funcionario.usuario.nome = dados.nome
        funcionario.cpf = dados.cpf
        funcionario.usuario.senha = criar_hash_senha(dados.senha)

        funcionario_alterado = self.repo.alterar(funcionario)
        return FuncionarioMapper.entity_to_output_dto(
            funcionario_alterado  # type: ignore
        )


class RemoverFuncionarioUseCase:
    def __init__(self, db: Session, usuario_logado: UsuarioModel):
        self.repo = FuncionarioRepository(db)
        self.usuario_logado = usuario_logado

    def usuario_logado_eh_admin(self) -> bool:
        if self.usuario_logado.funcionario:
            return (
                self.usuario_logado.funcionario.tipo_funcionario
                == 'ADMINISTRADOR'
            )
        return False

    def usuario_logado_eh_proprietario_conta(
        self, funcionario_id: int
    ) -> bool:
        if self.usuario_logado.funcionario:
            return (
                self.usuario_logado.funcionario.funcionario_id
                == funcionario_id
            )
        return False

    def executar(self, funcionario_id: int) -> None:
        if (
            not self.usuario_logado_eh_proprietario_conta(funcionario_id)
            and not self.usuario_logado_eh_admin()
        ):
            raise SomenteProprietarioOuAdminError

        funcionario = self.repo.buscar_por_id(funcionario_id)
        if not funcionario:
            raise FuncionarioNotFoundError(funcionario_id)

        self.repo.remover(funcionario_id)


class LoginUseCase:
    def __init__(self, auth_repo: AuthRepository):
        self.auth_repo = auth_repo

    def execute(self, email: str, senha: str) -> LoginOutputDTO:
        usuario = self.auth_repo.buscar_por_email(email)
        if not usuario:
            raise ValueError('Credenciais inválidas')

        if not verificar_senha(senha, usuario.senha):   # type: ignore
            raise ValueError('Credenciais inválidas')

        token = criar_token_jwt(usuario.usuario_id)  # type: ignore
        return LoginOutputDTO(access_token=token)
