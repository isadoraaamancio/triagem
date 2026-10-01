"""Interface de linha de comando para operar o PA manualmente.

    python cli.py              # usa a Fase 3
    python cli.py --fase 1     # usa a Fase 1
    python cli.py --demo       # roda um roteiro pronto e sai

Comandos (digite `ajuda` dentro do programa):
    cadastrar <cpf> <nascimento AAAA-MM-DD> <nome...>
    buscar <cpf>
    entrada <cpf> <risco 1-5>
    chamar
    desistir <cpf>
    tamanho
    relatorio [insertion|merge]
    sair
"""

import argparse
import shlex

from pronto_atendimento.fase1 import ProntoAtendimento as PAFase1
from pronto_atendimento.fase3 import ProntoAtendimento as PAFase3
from pronto_atendimento.modelo import NOMES_RISCO, ErroPA

AJUDA = __doc__.split("Comandos (digite `ajuda` dentro do programa):")[1]


def executar(pa, linha):
    partes = shlex.split(linha)
    if not partes:
        return
    cmd, args = partes[0].lower(), partes[1:]
    try:
        if cmd == "cadastrar":
            p = pa.cadastrar(args[0], " ".join(args[2:]), args[1])
            print(f"  cadastrado: {p.nome} (CPF {p.cpf}, nasc. {p.nascimento})")
        elif cmd == "buscar":
            p = pa.buscar_cadastro(args[0])
            print(f"  {p.nome} | nasc. {p.nascimento}" if p else "  cadastro inexistente")
        elif cmd == "entrada":
            e = pa.dar_entrada(args[0], int(args[1]))
            print(f"  {e.paciente.nome} na fila como {e.risco}-{NOMES_RISCO[e.risco]} "
                  f"(evento {e.seq})")
        elif cmd == "chamar":
            a = pa.chamar_proximo()
            print(f"  chamado: {a.nome} (CPF {a.cpf}), risco {a.risco}-{NOMES_RISCO[a.risco]}, "
                  f"esperou {a.espera} eventos")
        elif cmd == "desistir":
            e = pa.desistir(args[0])
            print(f"  {e.paciente.nome} removido da fila")
        elif cmd == "tamanho":
            print(f"  {pa.tamanho_fila()} aguardando")
        elif cmd == "relatorio":
            alg = args[0] if args else "merge"
            rel = pa.relatorio_do_dia(alg)
            print(f"  {len(rel)} atendimentos ({alg} sort), maior espera primeiro:")
            for a in rel:
                print(f"    espera {a.espera:>4} | risco {a.risco} | {a.cpf} {a.nome}")
        elif cmd in ("ajuda", "help", "?"):
            print(AJUDA)
        else:
            print("  comando desconhecido (digite ajuda)")
    except ErroPA as e:
        print(f"  [{type(e).__name__}] {e}")
    except (IndexError, ValueError):
        print("  argumentos inválidos (digite ajuda)")


DEMO = """
cadastrar 11111111111 1985-03-10 Maria Souza
cadastrar 22222222222 1990-07-22 João Lima
cadastrar 33333333333 2001-11-05 Ana Costa
cadastrar 44444444444 1978-01-30 Pedro Alves
cadastrar 11111111111 1999-09-09 CPF Repetido
buscar 22222222222
buscar 99999999999
entrada 11111111111 4
entrada 22222222222 3
entrada 33333333333 3
entrada 44444444444 1
entrada 22222222222 2
entrada 99999999999 1
tamanho
chamar
chamar
desistir 33333333333
desistir 33333333333
chamar
chamar
relatorio insertion
relatorio merge
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fase", type=int, choices=[1, 3], default=3)
    ap.add_argument("--demo", action="store_true")
    args = ap.parse_args()
    pa = PAFase1() if args.fase == 1 else PAFase3()
    print(f"Pronto Atendimento — Fase {args.fase}")
    if args.demo:
        for linha in DEMO.strip().splitlines():
            print(f"> {linha}")
            executar(pa, linha)
        return
    print("digite 'ajuda' para ver os comandos")
    while True:
        try:
            linha = input("> ")
        except EOFError:
            break
        if linha.strip().lower() in ("sair", "exit", "quit"):
            break
        executar(pa, linha)


if __name__ == "__main__":
    main()
