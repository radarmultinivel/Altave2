from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class TipoAlerta(Enum):
    MOVIMENTACAO = "Movimentação"
    CALOR = "Calor"

class Prioridade(Enum):
    CRITICO = 1
    MEDIO = 2
    BAIXO = 3

@dataclass
class Alert:
    id: str
    timestamp: datetime
    tipo: TipoAlerta
    prioridade: Prioridade
    mensagem: str

    def __post_init__(self):
        if not isinstance(self.id, (str,)) or not self.id:
            raise ValueError("ID do alerta deve ser uma string não vazia")
        if not isinstance(self.timestamp, (datetime,)):
            raise TypeError("Timestamp deve ser do tipo datetime")
        if not isinstance(self.tipo, (TipoAlerta,)):
            raise TypeError("Tipo deve ser do enum TipoAlerta")
        if not isinstance(self.prioridade, (Prioridade,)):
            raise TypeError("Prioridade deve ser do enum Prioridade")
        if not isinstance(self.mensagem, (str,)) or not self.mensagem:
            raise ValueError("Mensagem do alerta deve ser uma string não vazia")

    def __lt__(self, other: 'Alert') -> bool:
        if not isinstance(other, (Alert,)):
            raise TypeError("Comparação deve ser feita com outro objeto Alert")
        if self.prioridade.value != other.prioridade.value:
            return self.prioridade.value < other.prioridade.value
        return self.timestamp < other.timestamp

    def __str__(self) -> str:
        return (f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] "
                f"ID:{self.id} | {self.tipo.value} | {self.prioridade.name} | {self.mensagem}")