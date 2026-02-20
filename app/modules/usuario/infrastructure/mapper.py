from app.modules.usuario.domain.entities import Cliente, Funcionario, Usuario
from app.modules.usuario.application.dto import (
    ClienteOutputDTO,
    FuncionarioOutputDTO,
)
from app.modules.usuario.infrastructure.models import (
    ClienteModel,
    FuncionarioModel,
    UsuarioModel,
)


class ClienteMapper:
    @staticmethod
    def entity_to_model(cliente: Cliente) -> ClienteModel:
        """Converte a Entidade para Modelo ORM."""
        return ClienteModel(
            cliente_id=cliente.cliente_id,
            cpf_cnpj=cliente.cpf_cnpj,
            tipo_cliente=cliente.tipo,
            usuario=UsuarioModel(
                usuario_id=cliente.usuario.usuario_id,
                email=cliente.usuario.email,
                senha=cliente.usuario.senha,
                nome=cliente.usuario.nome,
            ),
        )

    @staticmethod
    def model_to_entity(cliente: ClienteModel) -> Cliente:
        """Converte o Modelo ORM para Entidade."""
        return Cliente(
            cliente_id=cliente.cliente_id,  # type: ignore
            cpf_cnpj=cliente.cpf_cnpj,  # type: ignore
            tipo=cliente.tipo_cliente,  # type: ignore
            usuario=Usuario(
                usuario_id=cliente.usuario.usuario_id,
                email=cliente.usuario.email,
                senha=cliente.usuario.senha,
                nome=cliente.usuario.nome,
            ),
        )

    @staticmethod
    def entity_to_output_dto(cliente: Cliente) -> ClienteOutputDTO:
        """Converte a Entidade para DTO de Saída."""
        return ClienteOutputDTO(
            cliente_id=cliente.cliente_id,  # type: ignore
            nome=cliente.usuario.nome,
            email=cliente.usuario.email,
            cpf_cnpj=cliente.cpf_cnpj,
            tipo=cliente.tipo,
        )


class FuncionarioMapper:
    @staticmethod
    def entity_to_model(funcionario: Funcionario) -> FuncionarioModel:
        """Converte a Entidade para Modelo ORM."""
        return FuncionarioModel(
            funcionario_id=funcionario.funcionario_id,
            matricula=funcionario.matricula,
            tipo_funcionario=funcionario.tipo,
            cpf=funcionario.cpf,
            usuario=UsuarioModel(
                usuario_id=funcionario.usuario.usuario_id,
                email=funcionario.usuario.email,
                senha=funcionario.usuario.senha,
                nome=funcionario.usuario.nome,
            ),
        )

    @staticmethod
    def model_to_entity(funcionario: FuncionarioModel) -> Funcionario:
        """Converte o Modelo ORM para Entidade."""
        return Funcionario(
            funcionario_id=funcionario.funcionario_id,  # type: ignore
            matricula=funcionario.matricula,  # type: ignore
            tipo=funcionario.tipo_funcionario,  # type: ignore
            cpf=funcionario.cpf,
            usuario=Usuario(
                usuario_id=funcionario.usuario.usuario_id,
                email=funcionario.usuario.email,
                senha=funcionario.usuario.senha,
                nome=funcionario.usuario.nome,
            ),
        )

    @staticmethod
    def entity_to_output_dto(funcionario: Funcionario) -> FuncionarioOutputDTO:
        """Converte a Entidade para DTO de Saída."""
        return FuncionarioOutputDTO(
            funcionario_id=funcionario.funcionario_id,  # type: ignore
            email=funcionario.usuario.email,
            nome=funcionario.usuario.nome,
            matricula=funcionario.matricula,
            tipo=funcionario.tipo, 
            cpf=funcionario.cpf
        )
