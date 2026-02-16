from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import obter_id_usuario_logado, obter_usuario_logado
from app.modules.usuario.application.use_cases import (
    AlterarFuncionarioUseCase,
    ConsultarFuncionarioUseCase,
    CriarFuncionarioUseCase,
    RemoverFuncionarioUseCase,
)
from app.modules.usuario.application.dto import (
    FuncionarioInputDTO,
    FuncionarioOutputDTO,
)


router = APIRouter()


@router.post(
    '/cadastrar', response_model=FuncionarioOutputDTO, status_code=201
)
def criar_funcionario(
    funci_data: FuncionarioInputDTO, db: Session = Depends(get_db)
):
    use_case = CriarFuncionarioUseCase(db)
    return use_case.executar(funci_data)


@router.get('/{funcionario_id}', response_model=FuncionarioOutputDTO)
def consultar_funcionario(
    funcionario_id: int,
    usuario_id=Depends(obter_id_usuario_logado),
    db: Session = Depends(get_db),
):
    use_case = ConsultarFuncionarioUseCase(db)
    return use_case.executar_consulta_por_id(funcionario_id)


@router.put('/{funcionario_id}', response_model=FuncionarioOutputDTO)
def alterar_funcionario(
    funcionario_id: int,
    funcionario_data: FuncionarioInputDTO,
    usuario=Depends(obter_usuario_logado),
    db: Session = Depends(get_db),
):
    use_case = AlterarFuncionarioUseCase(db, usuario)
    return use_case.executar(funcionario_id, funcionario_data)


@router.delete('/{funcionario_id}', status_code=204)
def remover_funcionario(
    funcionario_id: int,
    usuario=Depends(obter_usuario_logado),
    db: Session = Depends(get_db),
):
    use_case = RemoverFuncionarioUseCase(db, usuario)
    use_case.executar(funcionario_id)
