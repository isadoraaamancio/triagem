"""Fase 2.1 e Fase 3.4 — cronometragem das operações, Fase 1 x Fase 3.

Experimento A (o pedido no enunciado): para N = 10.000 e 100.000 cadastros,
aplica a MESMA sequência de operações às duas versões e mede o tempo de
cada chamada de R2 (buscar_cadastro) e R4 (chamar_proximo) com
time.perf_counter_ns(). Mede também R1, R3 e R5 de carona.

Experimento B (complementar): o custo de R4 não depende de N, depende de K
(quantos aguardam). Fixa N e varia K = 100, 1.000, 10.000 para mostrar
O(K) contra O(log K).

Uso:
    python -m experimentos.bench_operacoes            # completo
    python -m experimentos.bench_operacoes --rapido   # N menores, para testar
"""

import argparse
import csv
import os
import platform
import random
import statistics
import sys
import time

from pronto_atendimento.fase1 import ProntoAtendimento as PAFase1
from pronto_atendimento.fase3 import ProntoAtendimento as PAFase3
from pronto_atendimento.modelo import ErroPA

from .gerador_carga import encher_fila, gerar_cadastros, gerar_operacoes

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "resultados")

FASES = [("Fase 1", PAFase1), ("Fase 3", PAFase3)]
OPERACOES = ["R1 cadastrar", "R2 buscar_cadastro", "R3 dar_entrada",
             "R4 chamar_proximo", "R5 desistir"]


def popular(sistema, cadastros, tempos):
    t_total = time.perf_counter()
    pc = time.perf_counter_ns
    lista = tempos["R1 cadastrar"]
    for cpf, nome, nasc in cadastros:
        t0 = pc()
        sistema.cadastrar(cpf, nome, nasc)
        lista.append(pc() - t0)
    return time.perf_counter() - t_total


def executar(sistema, ops, tempos):
    pc = time.perf_counter_ns
    erros = 0
    chamados = []
    for op in ops:
        tipo = op[0]
        try:
            if tipo == "buscar":
                t0 = pc()
                sistema.buscar_cadastro(op[1])
                tempos["R2 buscar_cadastro"].append(pc() - t0)
            elif tipo == "chamar":
                t0 = pc()
                a = sistema.chamar_proximo()
                tempos["R4 chamar_proximo"].append(pc() - t0)
                chamados.append(a.cpf)
            elif tipo == "entrada":
                t0 = pc()
                sistema.dar_entrada(op[1], op[2])
                tempos["R3 dar_entrada"].append(pc() - t0)
            elif tipo == "desistir":
                t0 = pc()
                sistema.desistir(op[1])
                tempos["R5 desistir"].append(pc() - t0)
        except ErroPA:
            erros += 1  # casos de erro gerados de propósito
    return chamados, erros


def resumo(ns):
    if not ns:
        return (0, float("nan"), float("nan"))
    return (len(ns), statistics.mean(ns) / 1000, statistics.median(ns) / 1000)


def experimento_a(ns_lista, total_ops, linhas):
    print("\n=== Experimento A: mesma carga, N variando ===")
    for n in ns_lista:
        cadastros = gerar_cadastros(n)
        cpfs = [c[0] for c in cadastros]
        ops = gerar_operacoes(cpfs, total_ops)
        chamados_por_fase = []
        for nome_fase, Classe in FASES:
            tempos = {op: [] for op in OPERACOES}
            s = Classe()
            print(f"N={n:>7} {nome_fase}: populando...", end=" ", flush=True)
            t_pop = popular(s, cadastros, tempos)
            print(f"{t_pop:.2f}s; executando {len(ops)} ops...", end=" ", flush=True)
            t0 = time.perf_counter()
            chamados, erros = executar(s, ops, tempos)
            t_ops = time.perf_counter() - t0
            print(f"{t_ops:.2f}s (erros tratados: {erros})")
            chamados_por_fase.append(chamados)
            for op in OPERACOES:
                qtd, media, mediana = resumo(tempos[op])
                linhas.append({"experimento": "A", "fase": nome_fase, "N": n,
                               "K": "~300", "operacao": op, "chamadas": qtd,
                               "media_us": round(media, 3),
                               "mediana_us": round(mediana, 3)})
            linhas.append({"experimento": "A", "fase": nome_fase, "N": n, "K": "~300",
                           "operacao": "popular (N x R1) [s]", "chamadas": n,
                           "media_us": round(t_pop, 3), "mediana_us": ""})
        # corretude antes de velocidade: as duas fases precisam chamar os
        # mesmos pacientes, na mesma ordem
        assert chamados_por_fase[0] == chamados_por_fase[1], "Fase 1 e Fase 3 divergiram!"
        print(f"N={n:>7} ordem de chamada idêntica nas duas fases "
              f"({len(chamados_por_fase[0])} chamadas)")


def experimento_b(n, ks, linhas, reps=200):
    print("\n=== Experimento B: N fixo, K (tamanho da fila) variando ===")
    cadastros = gerar_cadastros(n)
    cpfs = [c[0] for c in cadastros]
    for nome_fase, Classe in FASES:
        s = Classe()
        for cpf, nome, nasc in cadastros:
            s.cadastrar(cpf, nome, nasc)
        for k in ks:
            escolhidos = encher_fila(s, cpfs, k)
            pc = time.perf_counter_ns
            t_chamar, t_entrada = [], []
            # chama um e devolve outro para manter K constante
            for i in range(reps):
                t0 = pc()
                a = s.chamar_proximo()
                t_chamar.append(pc() - t0)
                t0 = pc()
                s.dar_entrada(a.cpf, 1 + i % 5)
                t_entrada.append(pc() - t0)
            # desistentes sorteados em qualquer posição da fila (não só os
            # primeiros a chegar, que seriam o melhor caso da Fase 1)
            t_desistir = []
            for cpf in random.Random(k).sample(escolhidos, min(reps, k)):
                if s.tamanho_fila() == 0:
                    break
                try:
                    t0 = pc()
                    s.desistir(cpf)
                    t_desistir.append(pc() - t0)
                except ErroPA:
                    pass
            # esvazia para o próximo K
            while s.tamanho_fila() > 0:
                s.chamar_proximo()
            for op, ns in (("R4 chamar_proximo", t_chamar),
                           ("R3 dar_entrada", t_entrada),
                           ("R5 desistir", t_desistir)):
                qtd, media, mediana = resumo(ns)
                linhas.append({"experimento": "B", "fase": nome_fase, "N": n, "K": k,
                               "operacao": op, "chamadas": qtd,
                               "media_us": round(media, 3),
                               "mediana_us": round(mediana, 3)})
            print(f"{nome_fase} K={k:>6}: R4 mediana {statistics.median(t_chamar)/1000:9.2f} µs")


def salvar(linhas, nome):
    os.makedirs(SAIDA, exist_ok=True)
    caminho = os.path.join(SAIDA, nome)
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"\nresultados gravados em {caminho}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rapido", action="store_true", help="N pequenos, só para conferir")
    ap.add_argument("--ops", type=int, default=20000, help="operações na sequência")
    args = ap.parse_args()

    print(f"Python {sys.version.split()[0]} em {platform.platform()}")
    linhas = []
    if args.rapido:
        experimento_a([1000, 5000], 3000, linhas)
        experimento_b(5000, [100, 1000], linhas, reps=50)
        salvar(linhas, "operacoes_rapido.csv")
    else:
        experimento_a([10_000, 100_000], args.ops, linhas)
        experimento_b(10_000, [100, 1_000, 10_000], linhas)
        salvar(linhas, "operacoes.csv")


if __name__ == "__main__":
    main()
