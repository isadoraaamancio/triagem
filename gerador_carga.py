"""Gerador de carga (Fase 2.1 / Fase 3.4).

Cria N cadastros com CPFs aleatórios e uma sequência longa de operações
(entradas, buscas, chamadas e desistências). A sequência é gerada ANTES e
de forma determinística (semente fixa), para que exatamente a mesma carga
seja aplicada à Fase 1 e à Fase 3.

Código de experimento: aqui é permitido usar set/dict da linguagem.
"""

import random

NOMES = ["Ana", "Bruno", "Carla", "Daniel", "Eduarda", "Felipe", "Gabriela",
         "Heitor", "Isabela", "João", "Larissa", "Marcos", "Natália", "Otávio",
         "Paula", "Rafael", "Sofia", "Thiago", "Vitória", "William"]
SOBRENOMES = ["Silva", "Santos", "Oliveira", "Souza", "Lima", "Pereira",
              "Costa", "Rodrigues", "Almeida", "Nascimento", "Carvalho",
              "Gomes", "Ribeiro", "Martins", "Araújo"]


def gerar_cpfs(n, rng):
    """n CPFs distintos de 11 dígitos (sem validar dígito verificador)."""
    vistos = set()
    cpfs = []
    while len(cpfs) < n:
        c = f"{rng.randrange(10**11):011d}"
        if c not in vistos:
            vistos.add(c)
            cpfs.append(c)
    return cpfs


def gerar_cadastros(n, semente=42):
    rng = random.Random(semente)
    cadastros = []
    for cpf in gerar_cpfs(n, rng):
        nome = f"{rng.choice(NOMES)} {rng.choice(SOBRENOMES)}"
        nasc = f"{rng.randint(1930, 2024)}-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}"
        cadastros.append((cpf, nome, nasc))
    return cadastros


def cpf_inexistente(rng, existentes):
    while True:
        c = f"{rng.randrange(10**11):011d}"
        if c not in existentes:
            return c


def gerar_operacoes(cpfs, total_ops, fila_alvo=300, semente=7,
                    p_busca=0.30, p_desistencia=0.05, p_busca_inexistente=0.2):
    """Sequência de operações simulando um dia de PA.

    Mantém a fila oscilando em torno de `fila_alvo` (centenas de pacientes,
    como estimado pela direção). Cada operação é uma tupla:
      ("buscar", cpf) | ("entrada", cpf, risco) | ("chamar",) | ("desistir", cpf)
    Também gera alguns casos de erro de propósito (busca de CPF inexistente,
    entrada de quem já está na fila, desistência de quem não está).
    """
    rng = random.Random(semente)
    existentes = set(cpfs)
    na_fila = []           # para sortear quem desiste
    pos = {}               # cpf -> índice em na_fila
    ops = []

    def tirar(cpf):
        i = pos.pop(cpf)
        ultimo = na_fila.pop()
        if ultimo != cpf:
            na_fila[i] = ultimo
            pos[ultimo] = i

    # o modelo da fila do gerador precisa saber quem sai em cada "chamar";
    # para isso simulamos a prioridade com uma referência simples (heapq é
    # permitido em código de experimento).
    import heapq
    ref = []
    seq = 0

    for _ in range(total_ops):
        r = rng.random()
        k = len(na_fila)
        if r < p_busca:
            if rng.random() < p_busca_inexistente:
                ops.append(("buscar", cpf_inexistente(rng, existentes)))
            else:
                ops.append(("buscar", rng.choice(cpfs)))
            continue
        r = rng.random()
        if k > 0 and r < p_desistencia:
            cpf = rng.choice(na_fila)
            ops.append(("desistir", cpf))
            tirar(cpf)
            continue
        # entrada x chamada: probabilidade de entrada cai à medida que a fila
        # passa do alvo, o que mantém o tamanho estável
        p_entrada = 0.5 if k == 0 else min(0.9, max(0.1, 0.5 * fila_alvo / k))
        if k == 0 or rng.random() < p_entrada:
            cpf = rng.choice(cpfs)
            risco = rng.choices([1, 2, 3, 4, 5], weights=[2, 8, 30, 40, 20])[0]
            ops.append(("entrada", cpf, risco))
            if cpf not in pos:
                pos[cpf] = len(na_fila)
                na_fila.append(cpf)
                seq += 1
                heapq.heappush(ref, (risco, seq, cpf))
        else:
            ops.append(("chamar",))
            while ref:
                _, _, cpf = heapq.heappop(ref)
                if cpf in pos:
                    tirar(cpf)
                    break
    return ops


def encher_fila(sistema, cpfs, k, semente=11):
    """Coloca exatamente k pacientes distintos na fila (para medir R4 x K)."""
    rng = random.Random(semente)
    escolhidos = rng.sample(cpfs, k)
    for cpf in escolhidos:
        sistema.dar_entrada(cpf, rng.randint(1, 5))
    return escolhidos
