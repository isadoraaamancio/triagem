"""Tabela hash com encadeamento separado, implementada do zero.

Estrutura: um vetor de "baldes" (lista Python usada como array de tamanho
fixo). Cada balde é o início de uma lista ligada de nós (chave, valor).

Função de dispersão: FNV-1a de 64 bits sobre os caracteres da chave, seguida
de uma "dobra" (h ^ h >> 32) para misturar os bits altos nos bits baixos,
porque o índice do balde usa só os bits baixos (capacidade = potência de 2).

Fator de carga α = n / m. Quando α passa de 0,75 a capacidade dobra e todos
os itens são redistribuídos (rehash).

Custos (n = itens, m = baldes):
  buscar / contem   O(1) esperado (comprimento médio de cadeia = α ≤ 0,75,
                    sob a hipótese de dispersão uniforme); O(n) no pior caso
                    (todas as chaves no mesmo balde)
  inserir           O(1) amortizado esperado (o rehash custa O(n), mas
                    acontece só quando n dobra)
  remover           O(1) esperado
  memória           Θ(n + m) = Θ(n), pois m ≤ n / 0,375 depois de crescer
"""

_FNV_OFFSET = 0xCBF29CE484222325
_FNV_PRIME = 0x100000001B3
_MASCARA64 = 0xFFFFFFFFFFFFFFFF


def fnv1a(chave):
    h = _FNV_OFFSET
    for c in chave:
        h ^= ord(c)
        h = (h * _FNV_PRIME) & _MASCARA64
    return h ^ (h >> 32)


class _No:
    __slots__ = ("chave", "valor", "prox")

    def __init__(self, chave, valor, prox):
        self.chave = chave
        self.valor = valor
        self.prox = prox


class TabelaHash:
    FATOR_CARGA_MAX = 0.75

    def __init__(self, capacidade_inicial=16, funcao_hash=fnv1a):
        m = 1
        while m < capacidade_inicial:
            m *= 2
        self._baldes = [None] * m
        self._m = m
        self._n = 0
        self._hash = funcao_hash
        self.rehashes = 0  # só para relatório/estatística

    def __len__(self):
        return self._n

    def _indice(self, chave):
        return self._hash(chave) & (self._m - 1)

    def buscar(self, chave, padrao=None):
        no = self._baldes[self._indice(chave)]
        while no is not None:
            if no.chave == chave:
                return no.valor
            no = no.prox
        return padrao

    def contem(self, chave):
        no = self._baldes[self._indice(chave)]
        while no is not None:
            if no.chave == chave:
                return True
            no = no.prox
        return False

    def inserir(self, chave, valor):
        """Insere o par. Devolve False (e não altera nada) se a chave já existe."""
        i = self._indice(chave)
        no = self._baldes[i]
        while no is not None:
            if no.chave == chave:
                return False
            no = no.prox
        self._baldes[i] = _No(chave, valor, self._baldes[i])  # insere no início
        self._n += 1
        if self._n > self.FATOR_CARGA_MAX * self._m:
            self._redimensionar(2 * self._m)
        return True

    def remover(self, chave):
        """Remove a chave e devolve o valor; devolve None se não existia."""
        i = self._indice(chave)
        anterior = None
        no = self._baldes[i]
        while no is not None:
            if no.chave == chave:
                if anterior is None:
                    self._baldes[i] = no.prox
                else:
                    anterior.prox = no.prox
                self._n -= 1
                return no.valor
            anterior = no
            no = no.prox
        return None

    def _redimensionar(self, nova_m):
        antigos = self._baldes
        self._baldes = [None] * nova_m
        self._m = nova_m
        mascara = nova_m - 1
        for no in antigos:
            while no is not None:
                prox = no.prox
                i = self._hash(no.chave) & mascara
                no.prox = self._baldes[i]
                self._baldes[i] = no
                no = prox
        self.rehashes += 1

    def itens(self):
        """Gera os pares (chave, valor) em ordem arbitrária."""
        for no in self._baldes:
            while no is not None:
                yield no.chave, no.valor
                no = no.prox

    def estatisticas(self):
        """Dados sobre a distribuição das chaves, para demonstrar colisões."""
        ocupados = 0
        maior = 0
        colisoes = 0  # itens que caíram em balde já ocupado
        for no in self._baldes:
            c = 0
            while no is not None:
                c += 1
                no = no.prox
            if c:
                ocupados += 1
                colisoes += c - 1
                if c > maior:
                    maior = c
        return EstatisticasHash(self._n, self._m, ocupados, colisoes, maior, self.rehashes)


class EstatisticasHash:
    __slots__ = ("itens", "baldes", "fator_carga", "baldes_ocupados",
                 "itens_em_colisao", "maior_cadeia", "rehashes")

    def __init__(self, itens, baldes, ocupados, colisoes, maior, rehashes):
        self.itens = itens
        self.baldes = baldes
        self.fator_carga = itens / baldes
        self.baldes_ocupados = ocupados
        self.itens_em_colisao = colisoes
        self.maior_cadeia = maior
        self.rehashes = rehashes

    def __repr__(self):
        return (f"itens={self.itens} baldes={self.baldes} "
                f"fator_carga={self.fator_carga:.3f} ocupados={self.baldes_ocupados} "
                f"em_colisao={self.itens_em_colisao} maior_cadeia={self.maior_cadeia} "
                f"rehashes={self.rehashes}")
