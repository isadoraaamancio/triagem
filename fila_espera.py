"""Fila de espera da Fase 3: heap de mínimo + índice por CPF + remoção preguiçosa.

Por que não basta o heap: o R5 (desistir) precisa tirar um paciente
QUALQUER da fila, e o heap só oferece barato a remoção do topo. Achar o
paciente dentro do heap custaria O(K) (o heap não é ordenado por CPF).

Solução escolhida (remoção preguiçosa, "lazy deletion"):
  * `_por_cpf` é uma tabela hash CPF -> Entrada com quem está REALMENTE
    aguardando. Ela responde em O(1) esperado "esse CPF está na fila?".
  * desistir apenas marca a Entrada como inativa e a tira de `_por_cpf`.
    A entrada continua fisicamente dentro do heap ("lápide").
  * remover_proximo descarta as lápides que aparecerem no topo antes de
    devolver a primeira entrada ativa.
  * Para a memória não crescer sem limite, quando as lápides passam a ser
    mais da metade do heap, o heap é reconstruído só com as ativas (O(n),
    heapify). Como isso só acontece depois de pelo menos n/2 desistências,
    o custo se dilui: O(1) amortizado por desistência.

Custos (K = pacientes ativos, L = lápides, sempre L ≤ K + 64 por causa
da compactação, logo log(K + L) = O(log K)):
  inserir          O(log K) amortizado (heap) + O(1) esperado (hash)
  remover_proximo  O(log K) amortizado: cada lápide é retirada do heap uma
                   única vez, então o custo de descartá-la é cobrado da
                   desistência que a criou
  remover(cpf)     O(1) esperado + amortizado (hash + marcação)
  contem / len     O(1) esperado / O(1)
"""

from .heap import HeapMin
from .tabela_hash import TabelaHash

_MIN_COMPACTAR = 64  # não vale a pena compactar heaps pequenos


class FilaEspera:
    def __init__(self):
        self._heap = HeapMin()
        self._por_cpf = TabelaHash()
        self._lapides = 0
        self.compactacoes = 0  # só para estatística

    def __len__(self):
        return len(self._por_cpf)

    def contem(self, cpf):
        return self._por_cpf.contem(cpf)

    def inserir(self, entrada):
        """Supõe que o chamador já verificou que o CPF não está na fila."""
        self._por_cpf.inserir(entrada.paciente.cpf, entrada)
        self._heap.inserir(entrada)

    def remover_proximo(self):
        """Devolve a Entrada ativa de menor (risco, seq), ou None se vazia."""
        heap = self._heap
        while len(heap) > 0:
            e = heap.remover_topo()
            if e.ativa:
                self._por_cpf.remover(e.paciente.cpf)
                e.ativa = False
                return e
            self._lapides -= 1  # lápide descartada
        return None

    def remover(self, cpf):
        """Remove o paciente da fila (desistência). Devolve a Entrada ou None."""
        e = self._por_cpf.remover(cpf)
        if e is None:
            return None
        e.ativa = False
        self._lapides += 1
        if self._lapides > len(self._por_cpf) and len(self._heap) > _MIN_COMPACTAR:
            self._compactar()
        return e

    def _compactar(self):
        ativas = [e for e in self._heap.itens() if e.ativa]
        self._heap.construir(ativas)
        self._lapides = 0
        self.compactacoes += 1

    def tamanho_heap(self):
        """Tamanho físico do heap (ativas + lápides)."""
        return len(self._heap)
