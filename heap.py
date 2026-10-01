"""Heap binário de mínimo, implementado do zero sobre um vetor.

O elemento da posição i tem filhos em 2i+1 e 2i+2 e pai em (i-1)//2.
A ordem é dada pelo operador `<` dos próprios itens; na fila do PA os itens
são `Entrada`, cujo `<` compara (risco, seq). Como `seq` é único e crescente,
nunca existem dois itens "iguais" — o desempate por chegada está embutido
na chave e não depende de o heap ser estável (heap NÃO é estável por si só).

Custos (n = itens no heap), todos de PIOR CASO:
  inserir          O(log n)  (sift-up percorre no máximo a altura ⌊log2 n⌋)
  remover_topo     O(log n)  (sift-down)
  topo             O(1)
  construir        O(n)      (heapify de baixo para cima, Cormen cap. 6)
O `append`/`pop` no fim do vetor Python é O(1) amortizado, então inserir é
O(log n) amortizado quando se considera o crescimento do vetor.
"""


class HeapMin:
    def __init__(self, itens=None):
        self._a = []
        if itens is not None:
            self.construir(itens)

    def __len__(self):
        return len(self._a)

    def topo(self):
        if len(self._a) == 0:
            raise IndexError("heap vazio")
        return self._a[0]

    def inserir(self, item):
        self._a.append(item)
        self._subir(len(self._a) - 1)

    def remover_topo(self):
        a = self._a
        if len(a) == 0:
            raise IndexError("heap vazio")
        topo = a[0]
        ultimo = a.pop()
        if len(a) > 0:
            a[0] = ultimo
            self._descer(0)
        return topo

    def construir(self, itens):
        """Substitui o conteúdo por `itens` e reorganiza em O(n)."""
        self._a = list(itens)
        for i in range(len(self._a) // 2 - 1, -1, -1):
            self._descer(i)

    def itens(self):
        """Itens na ordem interna do vetor (não ordenados)."""
        return list(self._a)

    # ---------------------------------------------------------------- sift

    def _subir(self, i):
        a = self._a
        item = a[i]
        while i > 0:
            pai = (i - 1) // 2
            if item < a[pai]:
                a[i] = a[pai]
                i = pai
            else:
                break
        a[i] = item

    def _descer(self, i):
        a = self._a
        n = len(a)
        item = a[i]
        while True:
            filho = 2 * i + 1
            if filho >= n:
                break
            dir_ = filho + 1
            if dir_ < n and a[dir_] < a[filho]:
                filho = dir_
            if a[filho] < item:
                a[i] = a[filho]
                i = filho
            else:
                break
        a[i] = item

    def valido(self):
        """Confere a propriedade de heap (usado nos testes)."""
        a = self._a
        for i in range(1, len(a)):
            if a[i] < a[(i - 1) // 2]:
                return False
        return True
