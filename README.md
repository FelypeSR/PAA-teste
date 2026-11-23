# Problema da Mochila 0/1: Força Bruta x Heurística Gulosa

Trabalho 03 de Projeto e Análise de Algoritmos (IFMA Caxias, 2026).
Grupo: Carlos Eduardo, Felipe Santos e Narayane Chaves.

## Requisitos

- Python 3.10 ou mais recente
- matplotlib (`pip install matplotlib`)
- psutil (opcional, mostra a RAM e os núcleos físicos no Windows/macOS: `pip install psutil`)

## Como executar

```bash
python mochila.py ambiente   # hardware e software (slide "Ambiente dos experimentos")
python mochila.py estatica   # Teste 1: carga sintética estática + figura_estatica.png
python mochila.py dinamica   # Teste 2: carga sintética dinâmica + resultados_dinamica.csv + grafico_tempos.png
python mochila.py tudo       # os três em sequência
```

Opções da carga dinâmica (valores padrão):

```bash
python mochila.py dinamica --nmin 4 --nmax 22 --passo 2 --repeticoes 3 --seed 42
```

## O que cada teste faz

**Carga estática:** 8 itens fixos (cenário de um técnico com mochila de 15 kg).
Valida a corretude: a força bruta acha o ótimo (valor 143) e a gulosa acha 135 (94,4%).

**Carga dinâmica:** instâncias aleatórias com n = 4, 6, ..., 22 itens.
Pesos de 1 a 30, valores de 1 a 100, capacidade = 50% da soma dos pesos, seed 42.
Limite rígido em n = 22 para a força bruta não ficar inviável.
Saídas: tabela de tempos lado a lado em notação científica, tabela de qualidade (% do ótimo)
e gráfico em escala logarítmica.

## Ambiente dos experimentos

Os resultados e figuras foram gerados nesta máquina (saída de `python mochila.py ambiente`):

| Item         | Valor                                        |
|--------------|----------------------------------------------|
| Processador  | Intel Core i5-7300U @ 2.60GHz (7ª geração)   |
| Núcleos      | 4 lógicos (2 físicos)                        |
| Memória RAM  | 7.1 GB                                       |
| Sistema      | Linux 7.0.0-43-generic (Ubuntu)              |
| Python       | 3.14.4                                       |
| matplotlib   | 3.11.2                                       |

## Algoritmos

- `forca_bruta()`: testa as 2^n combinações. O(n·2^n). Garante o ótimo.
- `heuristica_gulosa()`: ordena por valor/peso, enche a mochila e compara com o melhor item
  isolado. O(n log n). Garante pelo menos 50% do ótimo.
