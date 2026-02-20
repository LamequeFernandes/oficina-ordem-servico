from fastapi.testclient import TestClient
from app.main import app
from app.modules.ordem_servico.application.dto import OrdemServicoOutputDTO
from app.modules.ordem_servico.domain.entities import StatusOrdemServico

client = TestClient(app, raise_server_exceptions=False)


def test_cadastrar_ordem_servico(obter_veiculo):
    token_cliente, id_veiculo = obter_veiculo
    response = client.post(
        f"/veiculos/{id_veiculo}/ordens_servico", 
        json={
            "observacoes": "Trocar oleo e filtro"
        },
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    body = response.json()
    assert response.status_code == 201
    assert "ordem_servico_id" in body
    assert body["observacoes"] == "Trocar oleo e filtro"
    assert body["status"] == "RECEBIDA"
    assert body["dta_finalizacao"] == None
    assert body["veiculo"]["veiculo_id"] == id_veiculo


def test_obter_ordem_servico_por_id(obter_ordem_servico):
    token_cliente, ordem_servico = obter_ordem_servico
    response = client.get(
        f"/veiculos/{ordem_servico.veiculo.veiculo_id}/ordens_servico/{ordem_servico.ordem_servico_id}",
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    body = response.json()
    assert response.status_code == 200
    assert body["ordem_servico_id"] == ordem_servico.ordem_servico_id
    assert body["veiculo"]["veiculo_id"] == ordem_servico.veiculo.veiculo_id
    assert body["status"] == ordem_servico.status
    assert body["observacoes"] == ordem_servico.observacoes
    assert body["dta_criacao"] is not None
    assert body["dta_finalizacao"] is None
    # assert body["orcamento"] is None


def test_listar_ordens_servico_por_veiculo(obter_ordem_servico):
    token_cliente, ordem_servico = obter_ordem_servico
    response = client.get(
        f"/veiculos/{ordem_servico.veiculo.veiculo_id}/ordens_servico",
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    body = response.json()
    assert response.status_code == 200
    assert isinstance(body, list)
    assert len(body) >= 1
    assert any(
        os["ordem_servico_id"] == ordem_servico.ordem_servico_id for os in body
    )


def test_alterar_status_ordem_servico(obter_ordem_servico, obter_admin):
    _, ordem_servico = obter_ordem_servico
    token_admin, _ = obter_admin
    response = client.patch(
        f"/veiculos/{ordem_servico.veiculo.veiculo_id}/ordens_servico/{ordem_servico.ordem_servico_id}/status",
        json={
            "status": StatusOrdemServico.EM_DIAGNOSTICO.value
        },
        headers={
            "Authorization": f"Bearer {token_admin}"
        }
    )
    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "EM_DIAGNOSTICO"


# TODO
# def test_deletar_ordem_servico(obter_ordem_servico, obter_admin):
#     _, ordem_servico = obter_ordem_servico
#     token_admin, _ = obter_admin
#     response = client.delete(
#         f"/veiculos/{ordem_servico.veiculo.veiculo_id}/ordens_servico/{ordem_servico.ordem_servico_id}",
#         headers={
#             "Authorization": f"Bearer {token_admin}"
#         }
#     )
#     assert response.status_code == 204


def test_deletar_ordem_servico_erro_permissao(obter_ordem_servico):
    token_cliente, ordem_servico = obter_ordem_servico
    response = client.delete(
        f"/veiculos/{ordem_servico.veiculo.veiculo_id}/ordens_servico/{ordem_servico.ordem_servico_id}",
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    assert response.status_code == 403


def test_consultar_status_ordem_servico(obter_ordem_servico):
    token_cliente, ordem_servico = obter_ordem_servico
    response = client.get(
        f"/veiculos/{ordem_servico.veiculo.veiculo_id}/ordens_servico/{ordem_servico.ordem_servico_id}/status",
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    body = response.json()
    assert response.status_code == 200
    assert "status" in body

