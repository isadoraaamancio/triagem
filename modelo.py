"""Tipos e exceções compartilhados pelas duas versões do sistema (Fase 1 e Fase 3).

As duas versões expõem exatamente a mesma interface pública, para que o mesmo
gerador de carga e os mesmos testes rodem sobre qualquer uma delas.
"""

# índice = nível de risco (a posição 0 não é usada)
NOMES_RISCO = ["", "Emergência", "Muito urgente", "Urgente", "Pouco urgente", "Não urgente"]


class Paciente:
    """Cadastro do paciente. O CPF é o identificador."""

    __slots__ = ("cpf", "nome", "nascimento")

    def __init__(self, cpf, nome, nascimento):
        self.cpf = cpf
        self.nome = nome
        self.nascimento = nascimento

    def __repr__(self):
        return f"Paciente({self.cpf!r}, {self.nome!r}, {self.nascimento!r})"


class Entrada:
    """Um paciente aguardando na fila.

    `seq` é o valor do contador de eventos no momento da entrada. Como o
    contador só cresce, `seq` também serve como ordem de chegada: quem tem o
    menor `seq` chegou primeiro. A ordem da fila é (risco, seq).
    """

    __slots__ = ("paciente", "risco", "seq", "ativa")

    def __init__(self, paciente, risco, seq):
        self.paciente = paciente
        self.risco = risco
        self.seq = seq
        self.ativa = True  # usado só pela Fase 3 (remoção preguiçosa)

    def __lt__(self, outra):
        if self.risco != outra.risco:
            return self.risco < outra.risco
        return self.seq < outra.seq

    def __repr__(self):
        return f"Entrada({self.paciente.cpf}, risco={self.risco}, seq={self.seq})"


class Atendimento:
    """Registro de um paciente já chamado, usado no relatório do dia (R7)."""

    __slots__ = ("cpf", "nome", "risco", "evento_entrada", "evento_chamada", "espera")

    def __init__(self, cpf, nome, risco, evento_entrada, evento_chamada):
        self.cpf = cpf
        self.nome = nome
        self.risco = risco
        self.evento_entrada = evento_entrada
        self.evento_chamada = evento_chamada
        # eventos ocorridos estritamente entre a entrada e a chamada
        self.espera = evento_chamada - evento_entrada - 1

    def __repr__(self):
        return (f"Atendimento({self.cpf}, risco={self.risco}, "
                f"espera={self.espera})")


# ---------------------------------------------------------------- exceções

class ErroPA(Exception):
    """Base de todos os erros de regra de negócio do sistema."""


class CPFDuplicado(ErroPA):
    pass


class CadastroInexistente(ErroPA):
    pass


class PacienteJaNaFila(ErroPA):
    pass


class PacienteForaDaFila(ErroPA):
    pass


class FilaVazia(ErroPA):
    pass


class RiscoInvalido(ErroPA):
    pass


def validar_risco(risco):
    if not isinstance(risco, int) or isinstance(risco, bool) or not 1 <= risco <= 5:
        raise RiscoInvalido(f"risco deve ser de 1 a 5, recebido {risco!r}")
