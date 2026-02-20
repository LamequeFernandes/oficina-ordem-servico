from dataclasses import dataclass
from datetime import datetime

from app.modules.usuario.domain.value_objects import CPF, CNPJ


@dataclass
class Usuario:
    usuario_id: int | None
    email: str
    senha: str
    nome: str
    dta_cadastro: datetime = datetime.now()


@dataclass
class Cliente:
    cliente_id: int | None
    usuario: Usuario
    cpf_cnpj: str
    tipo: str  # 'PF' ou 'PJ'

    def __post_init__(self):
        if self.tipo == 'PF':
            CPF(valor=self.cpf_cnpj)  # Levanta ValueError se inválido
        elif self.tipo == 'PJ':
            CNPJ(valor=self.cpf_cnpj)
        else:
            raise ValueError('Tipo de cliente inválido')


@dataclass
class Funcionario:
    funcionario_id: int | None
    usuario: Usuario
    matricula: int
    tipo: str  # 'ADMINISTRADOR' ou 'MECANICO'
    cpf: str

    def __post_init__(self):
        if not self.tipo == 'ADMINISTRADOR' and not self.tipo == 'MECANICO':
            raise ValueError('Tipo de funcionário inválido')
