# Problema 1 — Triagem no Pronto Atendimento

Sistema de fila de triagem do PA da ESCS com classificação de risco de 5
níveis, desempate por ordem de chegada, desistência e relatório diário
ordenado por tempo de espera.

O repositório guarda as duas versões pedidas:

| | Cadastros (R1, R2) | Fila de espera (R3–R6) | Relatório (R7) |
|---|---|---|---|
| **Fase 1** (`pronto_atendimento/fase1`) | lista, busca sequencial | lista na ordem de chegada, varredura para achar o próximo | insertion sort ou merge sort |
| **Fase 3** (`pronto_atendimento/fase3`) | tabela hash própria (encadeamento, FNV-1a, α ≤ 0,75) | heap binário próprio + índice hash por CPF + remoção preguiçosa | insertion sort ou merge sort |

Nenhuma estrutura pronta da linguagem é usada no núcleo (sem `dict`, `set`,
`heapq`, `collections`, `sorted()` ou `.sort()`). Tudo é construído sobre
listas Python usadas como vetor. As estruturas prontas aparecem só nos
testes e nos experimentos, como referência.

## Requisitos

Python 3.9 ou mais novo. Não há dependências externas. As medições do
relatório foram feitas com Python 3.12.

## Estrutura

```
pronto_atendimento/
  modelo.py           Paciente, Entrada, Atendimento e exceções (comum às fases)
  ordenacao.py        insertion_sort e merge_sort (do zero, estáveis)
  fase1/sistema.py    versão com listas simples
  fase3/tabela_hash.py
  fase3/heap.py
  fase3/fila_espera.py  heap + hash + remoção preguiçosa (R5)
  fase3/sistema.py    versão final
experimentos/
  gerador_carga.py    cria N cadastros e a sequência de operações
  bench_operacoes.py  Fase 2.1 e 3.4: R1..R5 cronometrados, Fase 1 x Fase 3
  bench_ordenacao.py  Fase 2.2: insertion x merge x sorted()
  medir_memoria.py    memória dos cadastros e qualidade da dispersão
  resultados/         CSVs e logs das execuções usadas no relatório
tests/                testes unitários + teste diferencial Fase 1 x Fase 3 x referência
cli.py                operação manual do sistema
relatorio/            relatório técnico (artigo)
registros/            registros do redator
```

## Como reproduzir

Todos os comandos a partir da raiz do repositório.

**Testes** (47 casos, menos de 1 s):

```bash
python3 -m unittest discover -s tests -t . -v
```

**Usar o sistema na mão:**

```bash
python3 cli.py            # Fase 3
python3 cli.py --fase 1   # Fase 1
python3 cli.py --demo     # roteiro pronto mostrando todas as operações e erros
```

**Medições da Fase 2.1 / 3.4** (alguns minutos, quase todo o tempo é a Fase 1 com N = 100.000):

```bash
python3 -m experimentos.bench_operacoes
```

Versão curta para conferir se está tudo funcionando:

```bash
python3 -m experimentos.bench_operacoes --rapido
```

**Medições da Fase 2.2** (o insertion sort com M = 100.000 leva perto de 2 minutos):

```bash
python3 -m experimentos.bench_ordenacao
```

**Memória e distribuição da tabela hash:**

```bash
python3 -m experimentos.medir_memoria
```

Os resultados vão para `experimentos/resultados/` (CSVs e logs).

## Decisões principais

* **Contador de eventos.** Cada operação que altera a fila e dá certo
  (`dar_entrada`, `chamar_proximo`, `desistir`) incrementa o contador interno.
  O tempo de espera é o número de eventos estritamente entre a entrada e a
  chamada: `espera = evento_chamada − evento_entrada − 1`.
* **Desempate.** O valor do contador na entrada (`seq`) é único e crescente,
  então a chave da fila é o par `(risco, seq)`. Não existem chaves iguais e o
  desempate por chegada sai da comparação, sem depender de estabilidade do heap.
* **Desistência.** Remoção preguiçosa: o paciente sai do índice por CPF na
  hora (O(1) esperado) e vira "lápide" dentro do heap, descartada quando chega
  ao topo. Quando as lápides passam da metade do heap, ele é reconstruído em O(n).
* **Erros.** Buscas sem resultado devolvem `None`; as demais situações
  inválidas levantam exceções específicas (`CPFDuplicado`,
  `CadastroInexistente`, `PacienteJaNaFila`, `FilaVazia`,
  `PacienteForaDaFila`, `RiscoInvalido`).
