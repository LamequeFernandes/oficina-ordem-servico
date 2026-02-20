from fastapi.testclient import TestClient
from app.main import app
from app.modules.veiculo.application.dto import VeiculoInputDTO

client = TestClient(app, raise_server_exceptions=False)


def test_cadastrar_veiculo(obter_cliente):
    token_cliente, _ = obter_cliente
    veiculo_novo = VeiculoInputDTO(
        placa="AAA1111", modelo="FIAT UNO", ano=2010
    )
    response = client.post(
        "/veiculos", 
        json=veiculo_novo.dict(),
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    assert response.status_code == 201


def test_obter_veiculo(obter_veiculo):
    token_cliente, id_veiculo = obter_veiculo
    response = client.get(
        f"/veiculos/{id_veiculo}", 
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    assert response.status_code == 200
    assert "veiculo_id" in response.json()


def test_alterar_veiculo(obter_veiculo):
    token_cliente, id_veiculo = obter_veiculo
    response = client.put(
        f"/veiculos/{id_veiculo}", 
        json={
            "placa": "ZZZ9999",
            "modelo": "FIAT UNO",
            "ano": 2010
        },
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    assert response.status_code == 200
    assert response.json()['placa'] == "ZZZ9999"


def test_alterar_veiculo_erro_formato_placa(obter_veiculo):
    token_cliente, id_veiculo = obter_veiculo
    response = client.put(
        f"/veiculos/{id_veiculo}", 
        json={
            "placa": "1111111",
            "modelo": "FIAT UNO",
            "ano": 2010
        },
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    assert response.status_code == 400
    print(response.json())
    assert response.json()['detail'] == "Padrão da placa incorreto, exemplo correto: 'AAA2A22' ou 'AAA2222'."


def test_deleta_veiculo(obter_veiculo):
    token_cliente, id_veiculo = obter_veiculo
    response = client.delete(
        f"/veiculos/{id_veiculo}", 
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    assert response.status_code == 204