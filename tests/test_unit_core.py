"""
Testes unitários para core: exceptions, utils, security, value_objects.
Foco em cobrir linhas não atingidas pelos testes de integração.
"""
import re
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import (
    ApenasAdminPodeAcessarError,
    ApenasClientesPodemAcessarError,
    ApenasFuncionariosError,
    ApenasFuncionariosProprietariosError,
    ApenasMecanicosPodemAcessarError,
    ApenasMecanicoResponsavel,
    ClienteNotFoundError,
    FuncionarioNotFoundError,
    NaoEncontradoError,
    ObjetoPossuiVinculoError,
    OrdemServicoNotFoundError,
    PadraoPlacaIncorretoError,
    SomenteProprietarioDoUsuarioError,
    SomenteProprietarioOuAdminError,
    StatusOSInvalido,
    TamanhoCNPJInvalidoError,
    TamanhoCPFInvalidoError,
    TipoInvalidoClienteError,
    TokenInvalidoError,
    ValorDuplicadoError,
    ValidacaoTokenError,
    VeiculoNotFoundError,
    tratar_erro_dominio,
)
from app.core.utils import (
    adicionar_em_fila_execucao,
    finalizar_diagnostico_fila_execucao,
    finalizar_execucao_fila_execucao,
    iniciar_diagnostico_fila_execucao,
    iniciar_execucao_fila_execucao,
    obter_item_fila_execucao,
    obter_valor_e_key_duplicado_integrity_error,
)
from app.modules.usuario.domain.value_objects import CNPJ, CPF


# ─────────────────────────────────────────────────────────────────────────────
# Exceções – instanciação sem args
# ─────────────────────────────────────────────────────────────────────────────


def test_nao_encontrado_error_sem_id():
    e = NaoEncontradoError("Veiculo")
    assert "Veiculo" in str(e)


def test_nao_encontrado_error_com_id():
    e = NaoEncontradoError("Veiculo", 42)
    assert "42" in str(e)


def test_ordem_servico_not_found_sem_id():
    e = OrdemServicoNotFoundError()
    assert "Ordem de serviço" in str(e)


def test_ordem_servico_not_found_com_id():
    e = OrdemServicoNotFoundError(10)
    assert "10" in str(e)
    assert e.ordem_servico_id == 10


def test_veiculo_not_found_sem_id():
    e = VeiculoNotFoundError()
    assert "Veículo" in str(e)


def test_veiculo_not_found_com_id():
    e = VeiculoNotFoundError(5)
    assert "5" in str(e)
    assert e.veiculo_id == 5


def test_cliente_not_found_sem_id():
    e = ClienteNotFoundError()
    assert "Cliente" in str(e)


def test_cliente_not_found_com_id():
    e = ClienteNotFoundError(7)
    assert "7" in str(e)
    assert e.cliente_id == 7


def test_funcionario_not_found_sem_id():
    e = FuncionarioNotFoundError()
    assert "Funcionário" in str(e)


def test_funcionario_not_found_com_id():
    e = FuncionarioNotFoundError(9)
    assert "9" in str(e)
    assert e.funcionario_id == 9


def test_apenas_admin_error():
    e = ApenasAdminPodeAcessarError()
    assert "administradores" in str(e).lower() or "admin" in str(e).lower()


def test_apenas_mecanicos_error():
    e = ApenasMecanicosPodemAcessarError()
    assert "mecanicos" in str(e).lower()


def test_apenas_clientes_error():
    e = ApenasClientesPodemAcessarError()
    assert "clientes" in str(e).lower()


def test_apenas_funcionarios_error():
    e = ApenasFuncionariosError()
    assert "funcionários" in str(e).lower()


def test_apenas_funcionarios_proprietarios_error():
    e = ApenasFuncionariosProprietariosError()
    assert "funcionários" in str(e).lower()


def test_somente_proprietario_error():
    e = SomenteProprietarioDoUsuarioError()
    assert "proprietário" in str(e).lower()


def test_somente_proprietario_ou_admin_error():
    e = SomenteProprietarioOuAdminError()
    assert "proprietário" in str(e).lower()


def test_token_invalido_error():
    e = TokenInvalidoError()
    assert "token" in str(e).lower()


def test_validacao_token_error():
    e = ValidacaoTokenError()
    assert "validação" in str(e).lower() or "token" in str(e).lower()


def test_tamanho_cpf_invalido_error():
    e = TamanhoCPFInvalidoError()
    assert "cpf" in str(e).lower() or "11" in str(e)


def test_tamanho_cnpj_invalido_error():
    e = TamanhoCNPJInvalidoError()
    assert "cnpj" in str(e).lower() or "14" in str(e)


def test_tipo_invalido_cliente_error():
    e = TipoInvalidoClienteError()
    assert "tipo" in str(e).lower()


def test_valor_duplicado_error():
    e = ValorDuplicadoError("abc@mail.com", "email")
    assert e.valor == "abc@mail.com"
    assert e.chave == "email"
    assert "email" in str(e)


def test_padrao_placa_incorreto_error():
    e = PadraoPlacaIncorretoError()
    assert "placa" in str(e).lower()


def test_objeto_possui_vinculo_error():
    e = ObjetoPossuiVinculoError("Veiculo", 1, "OrdemServico")
    assert e.objeto == "Veiculo"
    assert e.objeto_id == 1
    assert e.objeto_vinculado == "OrdemServico"


def test_apenas_mecanico_responsavel_error():
    e = ApenasMecanicoResponsavel()
    assert "mecânico" in str(e).lower()


def test_status_os_invalido_error():
    e = StatusOSInvalido("ABERTO", "EM_PROGRESSO")
    assert "ABERTO" in str(e)


# ─────────────────────────────────────────────────────────────────────────────
# tratar_erro_dominio
# ─────────────────────────────────────────────────────────────────────────────


def test_tratar_erro_dominio_400_value_error():
    resultado = tratar_erro_dominio(ValueError("campo inválido"))
    assert isinstance(resultado, HTTPException)
    assert resultado.status_code == 400


def test_tratar_erro_dominio_400_cpf():
    resultado = tratar_erro_dominio(TamanhoCPFInvalidoError())
    assert resultado.status_code == 400


def test_tratar_erro_dominio_400_placa():
    resultado = tratar_erro_dominio(PadraoPlacaIncorretoError())
    assert resultado.status_code == 400


def test_tratar_erro_dominio_400_veiculo_not_found():
    resultado = tratar_erro_dominio(VeiculoNotFoundError(1))
    assert resultado.status_code == 400


def test_tratar_erro_dominio_400_status_os():
    resultado = tratar_erro_dominio(StatusOSInvalido("ABERTO", "EM_PROGRESSO"))
    assert resultado.status_code == 400


def test_tratar_erro_dominio_401_token_invalido():
    resultado = tratar_erro_dominio(TokenInvalidoError())
    assert resultado.status_code == 401


def test_tratar_erro_dominio_401_validacao_token():
    resultado = tratar_erro_dominio(ValidacaoTokenError())
    assert resultado.status_code == 401


def test_tratar_erro_dominio_403_admin():
    resultado = tratar_erro_dominio(ApenasAdminPodeAcessarError())
    assert resultado.status_code == 403


def test_tratar_erro_dominio_403_mecanico():
    resultado = tratar_erro_dominio(ApenasMecanicosPodemAcessarError())
    assert resultado.status_code == 403


def test_tratar_erro_dominio_403_cliente_not_found():
    resultado = tratar_erro_dominio(ClienteNotFoundError(1))
    assert resultado.status_code == 403


def test_tratar_erro_dominio_403_funcionario_not_found():
    resultado = tratar_erro_dominio(FuncionarioNotFoundError(1))
    assert resultado.status_code == 403


def test_tratar_erro_dominio_403_proprietario():
    resultado = tratar_erro_dominio(SomenteProprietarioDoUsuarioError())
    assert resultado.status_code == 403


def test_tratar_erro_dominio_403_mecanico_responsavel():
    resultado = tratar_erro_dominio(ApenasMecanicoResponsavel())
    assert resultado.status_code == 403


def test_tratar_erro_dominio_409_valor_duplicado():
    resultado = tratar_erro_dominio(ValorDuplicadoError("x", "email"))
    assert resultado.status_code == 409


def test_tratar_erro_dominio_409_integrity_error():
    orig = Exception("Duplicate entry 'test@email.com' for key 'usuarios.email'")
    err = IntegrityError("statement", {}, orig)
    resultado = tratar_erro_dominio(err)
    assert resultado.status_code == 409
    assert "email" in resultado.detail


def test_tratar_erro_dominio_500_generico():
    resultado = tratar_erro_dominio(RuntimeError("erro inesperado"))
    assert resultado.status_code == 500


# ─────────────────────────────────────────────────────────────────────────────
# obter_valor_e_key_duplicado_integrity_error
# ─────────────────────────────────────────────────────────────────────────────


def test_obter_valor_chave_integrity_error_sucesso():
    orig = Exception("Duplicate entry 'foo@bar.com' for key 'tabela.email'")
    err = IntegrityError("stmt", {}, orig)
    valor, chave = obter_valor_e_key_duplicado_integrity_error(err)
    assert valor == "foo@bar.com"
    assert chave == "email"


def test_obter_valor_chave_integrity_error_sem_match():
    orig = Exception("Algum outro erro de banco")
    err = IntegrityError("stmt", {}, orig)
    with pytest.raises(IntegrityError):
        obter_valor_e_key_duplicado_integrity_error(err)


# ─────────────────────────────────────────────────────────────────────────────
# core/utils.py – funções HTTP (mockadas)
# ─────────────────────────────────────────────────────────────────────────────


@patch("app.core.utils.requests.get")
def test_obter_item_fila_execucao_sucesso(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"fila_id": 1, "ordem_servico_id": 10}
    mock_get.return_value = mock_resp

    resultado = obter_item_fila_execucao(10)
    assert resultado["fila_id"] == 1


@patch("app.core.utils.requests.get")
def test_obter_item_fila_execucao_nao_encontrado(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_get.return_value = mock_resp

    resultado = obter_item_fila_execucao(99)
    assert resultado is None


@patch("app.core.utils.requests.get")
def test_obter_item_fila_execucao_json_invalido(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.side_effect = ValueError("json inválido")
    mock_get.return_value = mock_resp

    resultado = obter_item_fila_execucao(10)
    assert resultado is None


@patch("app.core.utils.requests.get")
def test_obter_item_fila_execucao_request_exception(mock_get):
    from requests import RequestException
    mock_get.side_effect = RequestException("timeout")

    resultado = obter_item_fila_execucao(10)
    assert resultado is None


@patch("app.core.utils.requests.post")
def test_adicionar_em_fila_execucao_sucesso(mock_post):
    mock_post.return_value = MagicMock(status_code=201)
    adicionar_em_fila_execucao(1, "ALTA")
    mock_post.assert_called_once()


@patch("app.core.utils.requests.post")
def test_adicionar_em_fila_execucao_exception(mock_post):
    from requests import RequestException
    mock_post.side_effect = RequestException("timeout")
    resultado = adicionar_em_fila_execucao(1)
    assert resultado is None


@patch("app.core.utils.obter_item_fila_execucao")
def test_iniciar_diagnostico_sem_item(mock_obter):
    mock_obter.return_value = None
    resultado = iniciar_diagnostico_fila_execucao(1, 2)
    assert resultado is None


@patch("app.core.utils.requests.post")
@patch("app.core.utils.obter_item_fila_execucao")
def test_iniciar_diagnostico_com_item(mock_obter, mock_post):
    mock_obter.return_value = {"fila_id": 5}
    mock_post.return_value = MagicMock(status_code=200)
    iniciar_diagnostico_fila_execucao(1, 2)
    mock_post.assert_called_once()


@patch("app.core.utils.requests.post")
@patch("app.core.utils.obter_item_fila_execucao")
def test_iniciar_diagnostico_request_exception(mock_obter, mock_post):
    from requests import RequestException
    mock_obter.return_value = {"fila_id": 5}
    mock_post.side_effect = RequestException("timeout")
    resultado = iniciar_diagnostico_fila_execucao(1, 2)
    assert resultado is None


@patch("app.core.utils.obter_item_fila_execucao")
def test_finalizar_diagnostico_sem_item(mock_obter):
    mock_obter.return_value = None
    resultado = finalizar_diagnostico_fila_execucao(1, "diagnóstico")
    assert resultado is None


@patch("app.core.utils.requests.post")
@patch("app.core.utils.obter_item_fila_execucao")
def test_finalizar_diagnostico_com_item(mock_obter, mock_post):
    mock_obter.return_value = {"fila_id": 5}
    mock_post.return_value = MagicMock(status_code=200)
    finalizar_diagnostico_fila_execucao(1, "ok")
    mock_post.assert_called_once()


@patch("app.core.utils.requests.post")
@patch("app.core.utils.obter_item_fila_execucao")
def test_finalizar_diagnostico_request_exception(mock_obter, mock_post):
    from requests import RequestException
    mock_obter.return_value = {"fila_id": 5}
    mock_post.side_effect = RequestException("timeout")
    resultado = finalizar_diagnostico_fila_execucao(1, "ok")
    assert resultado is None


@patch("app.core.utils.obter_item_fila_execucao")
def test_iniciar_execucao_sem_item(mock_obter):
    mock_obter.return_value = {}
    resultado = iniciar_execucao_fila_execucao(1, 2)
    assert resultado is None


@patch("app.core.utils.requests.post")
@patch("app.core.utils.obter_item_fila_execucao")
def test_iniciar_execucao_com_item(mock_obter, mock_post):
    mock_obter.return_value = {"fila_id": 3}
    mock_post.return_value = MagicMock(status_code=200)
    iniciar_execucao_fila_execucao(1, 2)
    mock_post.assert_called_once()


@patch("app.core.utils.requests.post")
@patch("app.core.utils.obter_item_fila_execucao")
def test_iniciar_execucao_request_exception(mock_obter, mock_post):
    from requests import RequestException
    mock_obter.return_value = {"fila_id": 3}
    mock_post.side_effect = RequestException("timeout")
    resultado = iniciar_execucao_fila_execucao(1, 2)
    assert resultado is None


@patch("app.core.utils.obter_item_fila_execucao")
def test_finalizar_execucao_sem_item(mock_obter):
    mock_obter.return_value = None
    resultado = finalizar_execucao_fila_execucao(1, "observações")
    assert resultado is None


@patch("app.core.utils.requests.post")
@patch("app.core.utils.obter_item_fila_execucao")
def test_finalizar_execucao_com_item(mock_obter, mock_post):
    mock_obter.return_value = {"fila_id": 4}
    mock_post.return_value = MagicMock(status_code=200)
    finalizar_execucao_fila_execucao(1, "tudo ok")
    mock_post.assert_called_once()


@patch("app.core.utils.requests.post")
@patch("app.core.utils.obter_item_fila_execucao")
def test_finalizar_execucao_request_exception(mock_obter, mock_post):
    from requests import RequestException
    mock_obter.return_value = {"fila_id": 4}
    mock_post.side_effect = RequestException("timeout")
    resultado = finalizar_execucao_fila_execucao(1, "ok")
    assert resultado is None


# ─────────────────────────────────────────────────────────────────────────────
# value_objects
# ─────────────────────────────────────────────────────────────────────────────


def test_cpf_valido():
    cpf = CPF(valor="32735323005")
    assert cpf.valor == "32735323005"


def test_cpf_curto_levanta_erro():
    with pytest.raises(Exception):
        CPF(valor="123")


def test_cpf_com_letras_levanta_erro():
    with pytest.raises(Exception):
        CPF(valor="1234567890a")


def test_cnpj_valido():
    cnpj = CNPJ(valor="12345678000195")
    assert cnpj.valor == "12345678000195"


def test_cnpj_curto_levanta_erro():
    with pytest.raises(Exception):
        CNPJ(valor="123")


def test_cnpj_com_letras_levanta_erro():
    with pytest.raises(Exception):
        CNPJ(valor="1234567800019a")


# ─────────────────────────────────────────────────────────────────────────────
# security.py – funções básicas
# ─────────────────────────────────────────────────────────────────────────────


def test_criar_e_verificar_senha():
    from app.core.security import criar_hash_senha, verificar_senha

    senha = "minhasenha123"
    hashed = criar_hash_senha(senha)
    assert verificar_senha(senha, hashed) is True
    assert verificar_senha("senhaerrada", hashed) is False


def test_criar_token_jwt_retorna_string():
    from app.core.security import criar_token_jwt

    token = criar_token_jwt(1)
    assert isinstance(token, str)
    assert "." in token


def test_decodificar_token_jwt_valido():
    from app.core.security import criar_token_jwt, decodificar_token_jwt

    token = criar_token_jwt(42)
    usuario_id = decodificar_token_jwt(token)
    assert usuario_id == 42


def test_decodificar_token_jwt_invalido():
    from app.core.security import decodificar_token_jwt

    resultado = decodificar_token_jwt("token.invalido.aqui")
    assert resultado is None
