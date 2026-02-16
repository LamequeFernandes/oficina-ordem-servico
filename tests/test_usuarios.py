from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_cadastrar_cliente(cleanup_usuario):
    cliente_novo = {
        "email": "lameque@teste.com",
        "senha": "lameque123",
        "nome": "Lameque Usuario Teste",
        "cpf_cnpj": "32735323005",
        "tipo": "PF"
    }
    response = client.post(
        "/usuarios/clientes/cadastrar", 
        json=cliente_novo
    )
    assert response.status_code == 201


def test_cadastrar_administrador(cleanup_admin):
    admin_novo = {
        "email": "robin@teste.com",
        "senha": "robin123",
        "nome": "Robin Administrador Teste",
        "matricula": "1234567",
        "tipo": "ADMINISTRADOR",
        "cpf": "91704687020"
    }
    response = client.post(
        "/usuarios/funcionarios/cadastrar", 
        json=admin_novo
    )
    assert response.status_code == 201


def test_cadastrar_mecanico(cleanup_mecanico):
    mecanico_novo = {
        "email": "joao@teste.com",
        "senha": "joao123",
        "nome": "Joao Mecanico Teste",
        "matricula": "7654321",
        "tipo": "MECANICO",
        "cpf": "91704687020"
    }
    response = client.post(
        "/usuarios/funcionarios/cadastrar", 
        json=mecanico_novo
    )
    assert response.status_code == 201


def test_login_sucesso(criar_cliente_teste):
    response = client.post(
        "/usuarios/login", 
        data={
            "username": "lameque@teste.com",
            "password": "lameque123"
        } 
    )
    body = response.json()
    assert response.status_code == 200
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_invalido():
    data = {
        "username": "lameque@teste.com",
        "password": "senha_errada"
    }

    response = client.post("/usuarios/login", data=data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciais inválidas" 


def test_obter_cliente_por_id(obter_cliente):
    token_cliente, cliente_logado = obter_cliente
    response = client.get(
        f"/usuarios/clientes/{cliente_logado.cliente_id}",
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "lameque@teste.com"


def test_deletar_cliente(obter_cliente):
    token_cliente, cliente_logado = obter_cliente
    response = client.delete(
        f"/usuarios/clientes/{cliente_logado.cliente_id}",
        headers={
            "Authorization": f"Bearer {token_cliente}"
        }
    )
    assert response.status_code == 204


def test_atualizar_cliente(obter_cliente):
    token_cliente, cliente_logado = obter_cliente
    cliente_atualizado = {
        "email": "lameque@teste.com",
        "senha": "lameque123",
        "nome": "Lameque Usuario Teste Atualizado",
        "cpf_cnpj": "32735323005",
        "tipo": "PF"
    }
    response = client.put(
        f"/usuarios/clientes/{cliente_logado.cliente_id}",
        headers={
            "Authorization": f"Bearer {token_cliente}"
        },
        json=cliente_atualizado
    )
    assert response.status_code == 200
    assert response.json()["nome"] == "Lameque Usuario Teste Atualizado"


def test_obter_funcionario_por_id(obter_admin):
    token_admin, admin_logado = obter_admin
    response = client.get(
        f"/usuarios/funcionarios/{admin_logado.funcionario_id}",
        headers={
            "Authorization": f"Bearer {token_admin}"
        }
    )
    assert response.status_code == 200
    assert response.json()["email"] == "robin@teste.com"


def test_deletar_funcionario(obter_admin):
    token_admin, admin_logado = obter_admin
    response = client.delete(
        f"/usuarios/funcionarios/{admin_logado.funcionario_id}",
        headers={
            "Authorization": f"Bearer {token_admin}"
        }
    )
    assert response.status_code == 204


def test_atualizar_funcionario(obter_admin):
    token_admin, admin_logado = obter_admin
    admin_atualizado = {
        "email": "robin@teste.com",
        "senha": "robin123",
        "nome": "Robin Usuario Teste Atualizado",
        "matricula": "1234567",
        "tipo": "ADMINISTRADOR",
        "cpf": "91704687020"
    }
    response = client.put(
        f"/usuarios/funcionarios/{admin_logado.funcionario_id}",
        headers={
            "Authorization": f"Bearer {token_admin}"
        },
        json=admin_atualizado
    )
    assert response.status_code == 200
    assert response.json()["nome"] == "Robin Usuario Teste Atualizado"


# def test_obter_funcionario_por_matricula(obter_admin):
#     token_admin, admin_logado = obter_admin
#     response = client.get(
#         f"/usuarios/funcionarios/matricula/{admin_logado.matricula}",
#         headers={
#             "Authorization": f"Bearer {token_admin}"
#         }
#     )
#     assert response.status_code == 200
#     assert response.json()["email"] == "robin@teste.com"


# def test_obter_cliente_por_cpf_cnpj(obter_cliente):
#     token_cliente, cliente_logado = obter_cliente
#     response = client.get(
#         f"/usuarios/clientes/cpfcnpj/{cliente_logado.cpf_cnpj}",
#         headers={
#             "Authorization": f"Bearer {token_cliente}"
#         }
#     )
#     assert response.status_code == 200
#     assert response.json()["email"] == "lameque@teste.com"
