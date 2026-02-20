from sqlalchemy.exc import IntegrityError

import requests

import re

from app.core.config import settings


def obter_valor_e_key_duplicado_integrity_error(e: IntegrityError):
    """
    Extrai o valor duplicado de uma exceção IntegrityError.
    """
    msg = str(e.orig)

    match = re.search(r"Duplicate entry '(.+?)' for key '(.+?)'", msg)

    if not match:
        raise e
    valor_duplicado = match.group(1)
    chave = match.group(2).split('.')[-1]

    return valor_duplicado, chave


def obter_item_fila_execucao(ordem_servico_id: int):
    response = requests.get(f"{settings.URL_API_EXECUCAO}/fila-execucao/ordem-servico/{ordem_servico_id}")
    if response.status_code == 200:
        return response.json()
    return None


def adicionar_em_fila_execucao(ordem_servico_id: int, prioridade: str = "NORMAL"):
    requests.post(
        f"{settings.URL_API_EXECUCAO}/fila-execucao",
        json={
            "ordem_servico_id": ordem_servico_id,
            "prioridade": prioridade
        }
    )


def iniciar_diagnostico_fila_execucao(ordem_servico_id: int, mecanico_responsavel_id: int):
    item_fila = obter_item_fila_execucao(ordem_servico_id)  
    requests.post(
        f"{settings.URL_API_EXECUCAO}/fila-execucao/{item_fila['fila_id']}/iniciar-diagnostico",
        json={
            "mecanico_responsavel_id": mecanico_responsavel_id
        }
    )


def finalizar_diagnostico_fila_execucao(ordem_servico_id: int, diagnostico: str):
    item_fila = obter_item_fila_execucao(ordem_servico_id)  
    requests.post(
        f"{settings.URL_API_EXECUCAO}/fila-execucao/{item_fila['fila_id']}/finalizar-diagnostico",
        json={
            "diagnostico": diagnostico
        }
    )


def iniciar_execucao_fila_execucao(ordem_servico_id: int, mecanico_responsavel_id: int):
    item_fila = obter_item_fila_execucao(ordem_servico_id)  
    requests.post(
        f"{settings.URL_API_EXECUCAO}/fila-execucao/{item_fila['fila_id']}/iniciar-reparo",
        json={
            "mecanico_responsavel_id": mecanico_responsavel_id
        }
    )


def finalizar_execucao_fila_execucao(ordem_servico_id: int, observacoes_reparo: str):
    item_fila = obter_item_fila_execucao(ordem_servico_id)  
    requests.post(
        f"{settings.URL_API_EXECUCAO}/fila-execucao/{item_fila['fila_id']}/finalizar-reparo",
        json={
            "observacoes_reparo": observacoes_reparo
        }
    )
