"""Memória ocupada pelos cadastros (Fase 1 x Fase 3) e qualidade da dispersão.

    python -m experimentos.medir_memoria

Para a Fase 1 os pacientes são colocados direto na lista (sem a verificação
de duplicado, que levaria ~1 min e não muda a memória). O objetivo é medir
só o espaço das estruturas, com tracemalloc.

Também compara o número de baldes ocupados com o valor previsto sob a
hipótese de dispersão uniforme: m · (1 − e^(−n/m)).
"""

import math
import tracemalloc

from pronto_atendimento.fase1 import ProntoAtendimento as PAFase1
from pronto_atendimento.fase3 import ProntoAtendimento as PAFase3
from pronto_atendimento.modelo import Paciente

from .gerador_carga import gerar_cadastros


def main(n=100_000):
    cadastros = gerar_cadastros(n)

    tracemalloc.start()
    s1 = PAFase1()
    for c in cadastros:
        s1._cadastros.append(Paciente(*c))
    m1 = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()

    tracemalloc.start()
    s3 = PAFase3()
    for c in cadastros:
        s3.cadastrar(*c)
    m3 = tracemalloc.get_traced_memory()[0]
    tracemalloc.stop()

    print(f"N = {n}")
    print(f"  Fase 1 (lista):       {m1 / 2**20:6.2f} MiB")
    print(f"  Fase 3 (tabela hash): {m3 / 2**20:6.2f} MiB")
    est = s3.estatisticas_hash()
    print(f"  {est}")
    previsto = est.baldes * (1 - math.exp(-est.itens / est.baldes))
    print(f"  baldes ocupados: medido {est.baldes_ocupados}, "
          f"previsto (dispersão uniforme) {previsto:.0f}")


if __name__ == "__main__":
    main()
