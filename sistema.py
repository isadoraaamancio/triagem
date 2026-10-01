"""Fase 3 — estruturas próprias que eliminam os gargalos da Fase 1.

  * cadastros: TabelaHash (CPF -> Paciente)            -> R1, R2 em O(1) esperado
  * fila:      FilaEspera (heap + hash + lápides)       -> R3, R4 em O(log K)
  * atendidos: vetor simples, na ordem de chamada       -> R7 com merge sort

N = cadastros, K = aguardando, M = atendidos.
  cadastrar        O(1) amortizado esperado
  buscar_cadastro  O(1) esperado                  (O(N) no pior caso)
  dar_entrada      O(1) esperado + O(log K) amortizado
  chamar_proximo   O(log K) amortizado
  desistir         O(1) esperado / amortizado
  tamanho_fila     O(1) pior caso
  relatorio_do_dia O(M log M) pior caso com merge sort
"""

from ..modelo import (
    Atendimento, CadastroInexistente, CPFDuplicado, Entrada, FilaVazia,
    Paciente, PacienteForaDaFila, PacienteJaNaFila, validar_risco,
)
from ..ordenacao import obter_algoritmo
from .fila_espera import FilaEspera
from .tabela_hash import TabelaHash


class ProntoAtendimento:
    FASE = 3

    def __init__(self, capacidade_inicial=16):
        self._cadastros = TabelaHash(capacidade_inicial)
        self._fila = FilaEspera()
        self._atendidos = []
        self._evento = 0

    def cadastrar(self, cpf, nome, nascimento):
        """R1."""
        p = Paciente(cpf, nome, nascimento)
        if not self._cadastros.inserir(cpf, p):
            raise CPFDuplicado(f"CPF {cpf} já cadastrado")
        return p

    def buscar_cadastro(self, cpf):
        """R2. Devolve o Paciente ou None."""
        return self._cadastros.buscar(cpf)

    def dar_entrada(self, cpf, risco):
        """R3."""
        validar_risco(risco)
        p = self._cadastros.buscar(cpf)
        if p is None:
            raise CadastroInexistente(f"CPF {cpf} não tem cadastro")
        if self._fila.contem(cpf):
            raise PacienteJaNaFila(f"CPF {cpf} já está aguardando")
        self._evento += 1
        e = Entrada(p, risco, self._evento)
        self._fila.inserir(e)
        return e

    def chamar_proximo(self):
        """R4."""
        e = self._fila.remover_proximo()
        if e is None:
            raise FilaVazia("não há pacientes aguardando")
        self._evento += 1
        a = Atendimento(e.paciente.cpf, e.paciente.nome, e.risco, e.seq, self._evento)
        self._atendidos.append(a)
        return a

    def desistir(self, cpf):
        """R5."""
        e = self._fila.remover(cpf)
        if e is None:
            raise PacienteForaDaFila(f"CPF {cpf} não está na fila")
        self._evento += 1
        return e

    def tamanho_fila(self):
        """R6."""
        return len(self._fila)

    def relatorio_do_dia(self, algoritmo="merge"):
        """R7."""
        ordenar = obter_algoritmo(algoritmo)
        return ordenar(self._atendidos, chave=lambda a: a.espera, decrescente=True)

    # ------------------------------------------------------------ extras

    def total_cadastros(self):
        return len(self._cadastros)

    def atendidos(self):
        return list(self._atendidos)

    def estatisticas_hash(self):
        return self._cadastros.estatisticas()
