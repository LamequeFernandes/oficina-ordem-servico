import pytest
from app.core.database import SessionLocal
# from app.modules.orcamento.application.dto import OrcamentoOutputDTO
# from app.modules.orcamento.domain.entities import StatusOrcamento
from app.modules.ordem_servico.application.dto import OrdemServicoOutputDTO
# from app.modules.peca.application.dto import PecaInputDTO, PecaOutDTO
# from app.modules.servico.application.dto import ServicoOutDTO
from app.modules.usuario.application.dto import ClienteOutputDTO, FuncionarioOutputDTO
from app.modules.usuario.infrastructure.models import UsuarioModel, ClienteModel, FuncionarioModel
from fastapi.testclient import TestClient
from app.main import app
from app.modules.veiculo.application.dto import VeiculoInputDTO


from app.core.database import Base, engine

from app.core.__all_models import *  # noqa: F401
Base.metadata.create_all(bind=engine)

db = SessionLocal()
# db.add_all(servicos)
# db.add_all(pecas)
db.commit()

client = TestClient(app, raise_server_exceptions=False)


def deleta_cliente(email: str):
    db = SessionLocal()

    usuario = db.query(UsuarioModel).filter(UsuarioModel.email == email)
    cliente = db.query(ClienteModel).filter(ClienteModel.usuario_id) # type: ignore
    cliente.delete()
    usuario.delete()

    db.commit()
    db.close()


def deleta_funcionario(email: str):
    db = SessionLocal()

    usuario = db.query(UsuarioModel).filter(UsuarioModel.email == email)
    funci = db.query(FuncionarioModel).filter(FuncionarioModel.usuario_id) # type: ignore
    funci.delete()
    usuario.delete()

    db.commit()
    db.close()


@pytest.fixture
def cleanup_usuario():
    # roda antes do teste
    deleta_cliente("lameque@teste.com")
    yield
    # roda depois do teste
    deleta_cliente("lameque@teste.com")


@pytest.fixture
def cleanup_admin():
    deleta_funcionario("robin@teste.com")
    yield
    deleta_funcionario("robin@teste.com")


@pytest.fixture
def cleanup_mecanico():
    deleta_funcionario("joao@teste.com")
    yield
    deleta_funcionario("joao@teste.com")


@pytest.fixture
def criar_cliente_teste():
    email_cliente_teste = "lameque@teste.com"
    
    deleta_cliente(email_cliente_teste)
    cliente_novo = {
        "email": email_cliente_teste,
        "senha": "lameque123",
        "nome": "Lameque Usuario Teste",
        "cpf_cnpj": "32735323005",
        "tipo": "PF"
    }
    cliente = client.post(
        "/usuarios/clientes/cadastrar", 
        json=cliente_novo
    )
    yield ClienteOutputDTO(**cliente.json())
    deleta_cliente(email_cliente_teste)


@pytest.fixture
def obter_cliente():
    email_cliente_teste = "lameque@teste.com"
    senha_cliente_teste = "lameque123"
    
    deleta_cliente(email_cliente_teste)
    cliente_novo = {
        "email": email_cliente_teste,
        "senha": senha_cliente_teste,
        "nome": "Lameque Usuario Teste",
        "cpf_cnpj": "32735323005",
        "tipo": "PF"
    }
    cliente_novo = client.post(
        "/usuarios/clientes/cadastrar", 
        json=cliente_novo
    )

    response = client.post(
        "/usuarios/login", 
        data={
            "username": email_cliente_teste,
            "password": senha_cliente_teste
        } 
    )
    yield response.json()["access_token"], ClienteOutputDTO(**cliente_novo.json())
    deleta_cliente(email_cliente_teste)


@pytest.fixture
def obter_admin():
    email_admin_teste = "robin@teste.com"
    senha_admin_teste = "robin123"
    
    deleta_funcionario(email_admin_teste)
    admin_novo = {
        "email": email_admin_teste,
        "senha": senha_admin_teste,
        "nome": "Robin Administrador Teste",
        "matricula": "1234567",
        "tipo": "ADMINISTRADOR",
        "cpf": "91704687020"
    }
    admin_novo = client.post(
        "/usuarios/funcionarios/cadastrar", 
        json=admin_novo
    )
    response = client.post(
        "/usuarios/login", 
        data={
            "username": email_admin_teste,
            "password": senha_admin_teste
        } 
    )
    yield response.json()["access_token"], FuncionarioOutputDTO(**admin_novo.json())
    deleta_funcionario(email_admin_teste)


@pytest.fixture
def obter_mecanico():
    email_mecanico_teste = "joao@teste.com"
    senha_mecanico_teste = "joao123"
    
    deleta_funcionario(email_mecanico_teste)
    mecanico_novo = {
        "email": email_mecanico_teste,
        "senha": senha_mecanico_teste,
        "nome": "Joao Mecanico Teste",
        "matricula": "7654321",
        "tipo": "MECANICO",
        "cpf": "91704687020"
    }
    mecanico_criado = client.post(
        "/usuarios/funcionarios/cadastrar", 
        json=mecanico_novo
    )

    response = client.post(
        "/usuarios/login", 
        data={
            "username": email_mecanico_teste,
            "password": senha_mecanico_teste
        } 
    )
    yield response.json()["access_token"], FuncionarioOutputDTO(**mecanico_criado.json())
    deleta_funcionario(email_mecanico_teste)


@pytest.fixture
def obter_veiculo(obter_cliente):
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
    yield token_cliente, response.json()["veiculo_id"]


@pytest.fixture
def obter_ordem_servico(obter_veiculo):
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
    yield token_cliente, OrdemServicoOutputDTO(**response.json())


# @pytest.fixture
# def obter_orcamento(obter_ordem_servico, obter_mecanico):
#     token_cliente, ordem_servico = obter_ordem_servico
#     token_mecanico, mecanico = obter_mecanico
#     response = client.post(
#         f"/veiculos/{ordem_servico.veiculo.veiculo_id}/ordem-servicos/{ordem_servico.ordem_servico_id}/orcamento",
#         json={
#             "funcionario_id": mecanico.funcionario_id,
#             "status_orcamento": StatusOrcamento.AGUARDANDO_APROVACAO.value
#         },
#         headers={
#             "Authorization": f"Bearer {token_mecanico}"
#         }
#     )
#     yield token_cliente, token_mecanico, ordem_servico, OrcamentoOutputDTO(**response.json())


# @pytest.fixture
# def obter_peca(obter_mecanico):
#     token_mecanico, _ = obter_mecanico
#     response = client.post(
#         f"/pecas",
#         json={
#             "tipo_peca_id": 1,
#             "valor_peca": 100.0,
#             "marca": "Marca Exemplo",
#         },
#         headers={
#             "Authorization": f"Bearer {token_mecanico}"
#         }
#     )
#     yield token_mecanico, PecaOutDTO(**response.json())


# @pytest.fixture
# def obter_servico(obter_orcamento):
#     _, token_mecanico, _ , orcamento = obter_orcamento
#     response = client.post(
#         f"/servicos",
#         json={
#             "tipo_servico_id": 1,
#             "valor_servico": 150,
#             "orcamento_id": orcamento.orcamento_id
#         },
#         headers={
#             "Authorization": f"Bearer {token_mecanico}"
#         }
#     )
#     assert response.status_code == 201
#     yield token_mecanico, ServicoOutDTO(**response.json())
