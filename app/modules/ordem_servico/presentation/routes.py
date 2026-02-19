from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import obter_admin_logado, obter_id_usuario_logado, obter_usuario_logado, obter_cliente_logado
from app.modules.ordem_servico.application.use_cases import (
    CriarOrdemServicoUseCase,
    ConsultarOrdemServicoUseCase,
    AlterarStatusOrdemServicoUseCase,
    RemoverServicoUseCase,
)
from app.modules.ordem_servico.application.dto import (
    OrdemServicoAlteracaoStatusInputDTO,
    OrdemServicoCriacaoInputDTO,
    OrdemServicoOutputDTO,
    StatusOrdemServicoOutputDTO,
)


router = APIRouter()


@router.get('/ordens_servico', response_model=list[OrdemServicoOutputDTO])
def listar_todas_ordens_de_servico(
    usuario_logado=Depends(obter_usuario_logado), db: Session = Depends(get_db)
):
    use_case = ConsultarOrdemServicoUseCase(db, usuario_logado)
    return use_case.execute_listar()


@router.post(
    '/veiculos/{veiculo_id}/ordens_servico',
    response_model=OrdemServicoOutputDTO,
    status_code=201,
)
def criar_ordem_servico(
    veiculo_id: int,
    ordem_servico_data: OrdemServicoCriacaoInputDTO,
    cliente=Depends(obter_cliente_logado),
    db: Session = Depends(get_db),
):
    use_case = CriarOrdemServicoUseCase(db, cliente)
    return use_case.execute(veiculo_id, ordem_servico_data)


@router.get(
    '/veiculos/{veiculo_id}/ordens_servico/{ordem_servico_id}',
    response_model=OrdemServicoOutputDTO,
)
def consultar_ordem_servico(
    veiculo_id: int,
    ordem_servico_id: int,
    usuario_logado=Depends(obter_usuario_logado),
    db: Session = Depends(get_db),
):
    use_case = ConsultarOrdemServicoUseCase(db, usuario_logado)
    return use_case.execute_por_id(ordem_servico_id)


@router.get(
    '/veiculos/{veiculo_id}/ordens_servico',
    response_model=list[OrdemServicoOutputDTO],
)
def listar_ordens_servico_por_veiculo(
    veiculo_id: int,
    usuario_logado=Depends(obter_usuario_logado),
    db: Session = Depends(get_db),
):
    use_case = ConsultarOrdemServicoUseCase(db, usuario_logado)
    return use_case.execute_por_veiculo(veiculo_id)


@router.get('/veiculos/{veiculo_id}/ordens_servico/{ordem_servico_id}/status', response_model=StatusOrdemServicoOutputDTO)
def consultar_status_ordem_servico(
    veiculo_id: int,
    ordem_servico_id: int,
    usuario_logado=Depends(obter_usuario_logado),
    db: Session = Depends(get_db)
):
    use_case = ConsultarOrdemServicoUseCase(db, usuario_logado)
    return use_case.execute_obter_status(ordem_servico_id)


@router.patch(
    '/veiculos/{veiculo_id}/ordens_servico/{ordem_servico_id}/status',
    response_model=OrdemServicoOutputDTO,
)
def atualizar_status_ordem_servico(
    veiculo_id: int,
    ordem_servico_id: int,
    ordem_servico_data: OrdemServicoAlteracaoStatusInputDTO,
    usuario_id = Depends(obter_id_usuario_logado),
    db: Session = Depends(get_db),
):
    use_case = AlterarStatusOrdemServicoUseCase(db)
    return use_case.execute(ordem_servico_id, ordem_servico_data.status)


@router.delete(
    '/veiculos/{veiculo_id}/ordens_servico/{ordem_servico_id}',
    status_code=204, response_model=None
)
def remover_ordem_servico(
    veiculo_id: int,
    ordem_servico_id: int,
    administrador=Depends(obter_admin_logado),
    db: Session = Depends(get_db),
):
    use_case = RemoverServicoUseCase(db, administrador)
    use_case.execute(ordem_servico_id)
