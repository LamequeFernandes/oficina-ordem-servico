from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import (
    obter_cliente_logado,
    obter_id_usuario_logado,
    obter_usuario_logado,
)
from app.modules.usuario.application.use_cases import (
    AlterarClienteUseCase,
    ConsultarClienteUseCase,
    CriarClienteUseCase,
    RemoverClienteUseCase,
)
from app.modules.usuario.application.dto import (
    ClienteInputDTO,
    ClienteOutputDTO,
)


router = APIRouter()


@router.post('/cadastrar', response_model=ClienteOutputDTO, status_code=201)
def criar_cliente(
    cliente_data: ClienteInputDTO, db: Session = Depends(get_db)
):
    use_case = CriarClienteUseCase(db)
    return use_case.executar(cliente_data)


@router.get('/{cliente_id}', response_model=ClienteOutputDTO)
def consultar_cliente(
    cliente_id: int,
    usuario_id=Depends(obter_id_usuario_logado),
    db: Session = Depends(get_db),
):
    use_case = ConsultarClienteUseCase(db)
    return use_case.executar_consulta_por_id(cliente_id)


@router.put('/{cliente_id}', response_model=ClienteOutputDTO)
def alterar_cliente(
    cliente_id: int,
    cliente_data: ClienteInputDTO,
    cliente=Depends(obter_cliente_logado),
    db: Session = Depends(get_db),
):
    use_case = AlterarClienteUseCase(db, cliente)
    return use_case.executar(cliente_id, cliente_data)


@router.delete('/{cliente_id}', status_code=204)
def remover_cliente(
    cliente_id: int,
    usuario=Depends(obter_usuario_logado),
    db: Session = Depends(get_db),
):
    use_case = RemoverClienteUseCase(db, usuario)
    use_case.executar(cliente_id)
