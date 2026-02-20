from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import obter_cliente_logado, obter_usuario_logado
from app.modules.veiculo.application.use_cases import (
    CriarVeiculoUseCase,
    ConsultarVeiculoUseCase,
    AlterarVeiculoUseCase,
    RemoverVeiculoUseCase,
)
from app.modules.veiculo.application.dto import (
    VeiculoInputDTO,
    VeiculoOutputDTO,
)


router = APIRouter()


@router.post('/', response_model=VeiculoOutputDTO, status_code=201)
def criar_veiculo(
    veiculo_data: VeiculoInputDTO,
    cliente=Depends(obter_cliente_logado),
    db: Session = Depends(get_db),
):
    use_case = CriarVeiculoUseCase(db)
    return use_case.execute(cliente.cliente_id, veiculo_data)


@router.get('/{veiculo_id}', response_model=VeiculoOutputDTO)
def buscar_veiculo_por_id(
    veiculo_id: int,
    usuario=Depends(obter_usuario_logado),
    db: Session = Depends(get_db),
):
    use_case = ConsultarVeiculoUseCase(db, usuario)
    return use_case.execute(veiculo_id)


@router.put('/{veiculo_id}', response_model=VeiculoOutputDTO)
def alterar_veiculo(
    veiculo_id: int,
    veiculo_data: VeiculoInputDTO,
    usuario=Depends(obter_usuario_logado),
    db: Session = Depends(get_db),
):
    use_case = AlterarVeiculoUseCase(db, usuario)
    return use_case.execute(veiculo_id, veiculo_data)


@router.delete('/{veiculo_id}', status_code=204)
def remover_veiculo(
    veiculo_id: int,
    usuario=Depends(obter_usuario_logado),
    db: Session = Depends(get_db),
):
    use_case = RemoverVeiculoUseCase(db, usuario)
    use_case.execute(veiculo_id)
