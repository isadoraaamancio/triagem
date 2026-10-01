"""Fase 2.2 — ordenação do relatório (R7): insertion sort x merge sort.

Os M registros de atendimento são produzidos rodando o próprio sistema
(Fase 3, porque a Fase 1 levaria muito tempo só para gerar 100.000
atendimentos) com uma carga em que a fila fica em torno de 300 pessoas. Os
registros saem na ordem de chamada, exatamente como o relatório os recebe.

Também mede sorted() da linguagem como referência (item opcional 2.2c) e
confere se os três resultados são idênticos (inclusive a estabilidade).

Uso:
    python -m experimentos.bench_ordenacao               # M = 10.000 e 100.000
    python -m experimentos.bench_ordenacao --m 1000 5000 # outros valores
"""

import argparse
import csv
import os
import random
import time

from pronto_atendimento.fase3 import ProntoAtendimento as PAFase3
from pronto_atendimento.ordenacao import insertion_sort, merge_sort

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "resultados")


def gerar_atendimentos(m, fila_alvo=300, semente=2024):
    """Roda o PA até haver m atendidos; devolve a lista na ordem de chamada."""
    rng = random.Random(semente)
    s = PAFase3()
    n_cad = max(2 * fila_alvo, m // 2)
    cpfs = []
    for i in range(n_cad):
        cpf = f"{rng.randrange(10**11):011d}"
        try:
            s.cadastrar(cpf, f"Paciente {i}", "2000-01-01")
            cpfs.append(cpf)
        except Exception:
            pass
    atendidos = 0
    while atendidos < m:
        k = s.tamanho_fila()
        if k < fila_alvo // 2 or (k < 2 * fila_alvo and rng.random() < 0.5):
            try:
                s.dar_entrada(rng.choice(cpfs),
                              rng.choices([1, 2, 3, 4, 5], weights=[2, 8, 30, 40, 20])[0])
            except Exception:
                pass
        elif rng.random() < 0.05:
            # alguém desiste (escolhe um CPF qualquer; se não estiver na fila, ignora)
            try:
                s.desistir(rng.choice(cpfs))
            except Exception:
                pass
        else:
            s.chamar_proximo()
            atendidos += 1
    return s.atendidos()


def cronometrar(funcao, dados, reps):
    tempos = []
    resultado = None
    for _ in range(reps):
        t0 = time.perf_counter()
        resultado = funcao(dados)
        tempos.append(time.perf_counter() - t0)
    return min(tempos), resultado


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m", type=int, nargs="+", default=[10_000, 100_000])
    args = ap.parse_args()

    chave = lambda a: a.espera
    algoritmos = [
        ("insertion sort", lambda v: insertion_sort(v, chave, decrescente=True)),
        ("merge sort", lambda v: merge_sort(v, chave, decrescente=True)),
        # referência da linguagem (só em código de experimento). sorted() é
        # estável, assim como os nossos; reverse=True também preserva a ordem
        # original dos empates.
        ("sorted() Python", lambda v: sorted(v, key=chave, reverse=True)),
    ]
    linhas = []
    for m in args.m:
        dados = gerar_atendimentos(m)
        esperas = [a.espera for a in dados]
        print(f"\nM = {m}: espera min={min(esperas)} max={max(esperas)} "
              f"média={sum(esperas)/m:.1f} valores distintos={len(set(esperas))}")
        resultados = []
        for nome, f in algoritmos:
            # insertion sort em M grande leva minutos: 1 repetição basta
            reps = 1 if (nome == "insertion sort" and m > 20_000) else 3
            print(f"  {nome:<16}...", end=" ", flush=True)
            t, res = cronometrar(f, dados, reps)
            print(f"{t:10.4f} s (melhor de {reps})")
            resultados.append(res)
            linhas.append({"algoritmo": nome, "M": m, "tempo_s": round(t, 6), "repeticoes": reps})
        ref = [id(a) for a in resultados[2]]
        for (nome, _), res in zip(algoritmos[:2], resultados[:2]):
            assert [id(a) for a in res] == ref, f"{nome} difere de sorted()!"
        print("  saídas idênticas às de sorted() (mesma ordem, inclusive nos empates)")

    os.makedirs(SAIDA, exist_ok=True)
    caminho = os.path.join(SAIDA, "ordenacao.csv")
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["algoritmo", "M", "tempo_s", "repeticoes"])
        w.writeheader()
        w.writerows(linhas)
    print(f"\nresultados gravados em {caminho}")

    # razões entre os dois M, se houver exatamente dois
    if len(args.m) == 2:
        m1, m2 = args.m
        print(f"\nRazão de tempo M={m2} / M={m1}:")
        for nome, _ in algoritmos:
            t1 = next(l["tempo_s"] for l in linhas if l["algoritmo"] == nome and l["M"] == m1)
            t2 = next(l["tempo_s"] for l in linhas if l["algoritmo"] == nome and l["M"] == m2)
            print(f"  {nome:<16} {t2 / t1:8.1f}x")


if __name__ == "__main__":
    main()
