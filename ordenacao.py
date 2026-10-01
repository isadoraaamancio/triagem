"""Algoritmos de ordenação do R7, implementados do zero.

Os dois algoritmos recebem uma lista e uma função `chave` e devolvem uma NOVA
lista ordenada (a original não é alterada). As chaves são calculadas uma única
vez e ficam em um vetor paralelo, para que o laço interno compare inteiros em
vez de chamar a função `chave` a cada comparação.

Os dois algoritmos são ESTÁVEIS: itens com a mesma chave mantêm a ordem
relativa que tinham na entrada. No relatório do dia isso significa que, entre
dois pacientes com o mesmo tempo de espera, aparece primeiro quem foi
atendido primeiro.
"""


def _preparar(itens, chave, decrescente):
    v = list(itens)
    if decrescente:
        k = [-chave(x) for x in v]  # inverter o sinal mantém a estabilidade
    else:
        k = [chave(x) for x in v]
    return v, k


def insertion_sort(itens, chave=lambda x: x, decrescente=False):
    """Ordenação por inserção. O(n^2) no pior caso e no caso médio, O(n) se já ordenado."""
    v, k = _preparar(itens, chave, decrescente)
    n = len(v)
    for i in range(1, n):
        item = v[i]
        ki = k[i]
        j = i - 1
        # desloca para a direita tudo que for ESTRITAMENTE maior (<= manteria
        # o item à direita dos iguais -> estável)
        while j >= 0 and k[j] > ki:
            v[j + 1] = v[j]
            k[j + 1] = k[j]
            j -= 1
        v[j + 1] = item
        k[j + 1] = ki
    return v


def merge_sort(itens, chave=lambda x: x, decrescente=False):
    """Ordenação por intercalação (top-down). O(n log n) em todos os casos.

    T(n) = 2 T(n/2) + Θ(n)  ->  Θ(n log n)
    Usa um vetor auxiliar de tamanho n alocado uma única vez (memória Θ(n)).
    """
    v, k = _preparar(itens, chave, decrescente)
    n = len(v)
    if n < 2:
        return v
    aux_v = [None] * n
    aux_k = [0] * n
    _merge_sort_rec(v, k, aux_v, aux_k, 0, n)
    return v


def _merge_sort_rec(v, k, aux_v, aux_k, ini, fim):
    # ordena o intervalo semiaberto [ini, fim)
    if fim - ini < 2:
        return
    meio = (ini + fim) // 2
    _merge_sort_rec(v, k, aux_v, aux_k, ini, meio)   # T(n/2)
    _merge_sort_rec(v, k, aux_v, aux_k, meio, fim)   # T(n/2)
    if k[meio - 1] <= k[meio]:
        return  # metades já em ordem: nada a intercalar
    _intercalar(v, k, aux_v, aux_k, ini, meio, fim)  # Θ(n)


def _intercalar(v, k, aux_v, aux_k, ini, meio, fim):
    for t in range(ini, fim):
        aux_v[t] = v[t]
        aux_k[t] = k[t]
    i, j = ini, meio
    for t in range(ini, fim):
        if i < meio and (j >= fim or aux_k[i] <= aux_k[j]):  # <= garante estabilidade
            v[t] = aux_v[i]
            k[t] = aux_k[i]
            i += 1
        else:
            v[t] = aux_v[j]
            k[t] = aux_k[j]
            j += 1


def obter_algoritmo(nome):
    if nome == "insertion":
        return insertion_sort
    if nome == "merge":
        return merge_sort
    raise ValueError(f"algoritmo desconhecido: {nome!r} (use 'insertion' ou 'merge')")
