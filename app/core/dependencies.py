from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decodificar_token_jwt
from app.modules.usuario.infrastructure.models import (
    FuncionarioModel,
    ClienteModel,
    UsuarioModel,
)
from app.core.exceptions import (
    ApenasFuncionariosError,
    ValidacaoTokenError,
    TokenInvalidoError,
    ApenasClientesPodemAcessarError,
    ApenasMecanicosPodemAcessarError,
    ApenasAdminPodeAcessarError,
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/usuarios/login')


def obter_id_usuario_logado(token: str = Depends(oauth2_scheme)) -> int:
    """Dependência que valida o JWT e retorna o ID do usuário."""
    try:
        usuario_id = decodificar_token_jwt(token)
        if usuario_id is None:
            raise TokenInvalidoError
        return usuario_id
    except JWTError:
        raise ValidacaoTokenError


def obter_usuario_logado(
    usuario_id: int = Depends(obter_id_usuario_logado),
    db: Session = Depends(get_db),
) -> UsuarioModel | None:
    usuario_logado = (
        db.query(UsuarioModel)
        .filter(UsuarioModel.usuario_id == usuario_id)
        .first()
    )
    if not usuario_logado:
        raise TokenInvalidoError
    return usuario_logado


def obter_cliente_logado(
    usuario_id: int = Depends(obter_id_usuario_logado),
    db: Session = Depends(get_db),
) -> ClienteModel | None:
    cliente_logado = (
        db.query(ClienteModel)
        .filter(ClienteModel.usuario_id == usuario_id)
        .first()
    )
    if not cliente_logado:
        raise ApenasClientesPodemAcessarError
    return cliente_logado


def obter_funcionario_logado(
    usuario_id: int = Depends(obter_id_usuario_logado),
    db: Session = Depends(get_db),
) -> FuncionarioModel | None:
    funci_logado = (
        db.query(FuncionarioModel)
        .filter(FuncionarioModel.usuario_id == usuario_id)
        .first()
    )
    if not funci_logado:
        raise ApenasFuncionariosError
    return funci_logado


def obter_admin_logado(
    usuario_id: int = Depends(obter_id_usuario_logado),
    db: Session = Depends(get_db),
) -> FuncionarioModel:
    funci_logado = (
        db.query(FuncionarioModel)
        .filter(FuncionarioModel.usuario_id == usuario_id)
        .first()
    )

    if not funci_logado:
        raise ApenasAdminPodeAcessarError
    if funci_logado.tipo_funcionario != 'ADMINISTRADOR':   # type: ignore
        raise ApenasAdminPodeAcessarError
    return funci_logado


def obter_mecanico_logado(
    usuario_id: int = Depends(obter_id_usuario_logado),
    db: Session = Depends(get_db),
) -> FuncionarioModel:
    funci_logado = (
        db.query(FuncionarioModel)
        .filter(FuncionarioModel.usuario_id == usuario_id)
        .first()
    )
    if funci_logado.tipo_funcionario != 'MECANICO':   # type: ignore
        raise ApenasMecanicosPodemAcessarError
    return funci_logado
