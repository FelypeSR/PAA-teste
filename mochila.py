"""
Trabalho 03 - Problemas NP (PAA)
Problema da Mochila 0/1: Força Bruta x Heurística Gulosa (densidade valor/peso)

Grupo: Carlos Eduardo, Felipe Santos e Narayane Chaves

Uso:
    python mochila.py ambiente      # imprime hardware/software (slide de ambiente)
    python mochila.py estatica      # teste com carga sintética estática (+ figura)
    python mochila.py dinamica      # teste com carga sintética dinâmica (+ tabelas e gráfico)
    python mochila.py tudo          # executa os três, nessa ordem

Opções da carga dinâmica:
    --nmin 4 --nmax 22 --passo 2 --repeticoes 3 --seed 42
"""

import argparse
import itertools
import os
import platform
import random
import sys
import time

# ---------------------------------------------------------------------------
# 1. Algoritmo exato (baseline): Força Bruta
# ---------------------------------------------------------------------------

def gerar_combinacoes(n):
    """Gera todas as 2^n combinações (0 = fora, 1 = dentro da mochila)."""
    return itertools.product((0, 1), repeat=n)


def verificar_combinacao(combinacao, pesos, capacidade):
    """Retorna (valida, peso_total). Válida se o peso não excede a capacidade."""
    peso_total = 0
    for x, w in zip(combinacao, pesos):
        if x:
            peso_total += w
            if peso_total > capacidade:
                return False, peso_total
    return True, peso_total


def forca_bruta(itens, capacidade):
    """Testa todas as 2^n combinações e devolve a de maior valor.
    Complexidade: O(n * 2^n)."""
    pesos = [it["peso"] for it in itens]
    valores = [it["valor"] for it in itens]
    melhor_valor, melhor_comb = 0, (0,) * len(itens)
    for comb in gerar_combinacoes(len(itens)):
        valida, _ = verificar_combinacao(comb, pesos, capacidade)
        if valida:
            valor = sum(v for x, v in zip(comb, valores) if x)
            if valor > melhor_valor:
                melhor_valor, melhor_comb = valor, comb
    escolhidos = [itens[i]["nome"] for i, x in enumerate(melhor_comb) if x]
    return escolhidos, melhor_valor


# ---------------------------------------------------------------------------
# 2. Heurística: Gulosa por densidade (valor/peso) + melhor item isolado
# ---------------------------------------------------------------------------

def ordenar_por_densidade(itens):
    """Ordena os itens pela razão valor/peso, do maior para o menor."""
    return sorted(itens, key=lambda it: it["valor"] / it["peso"], reverse=True)


def preencher_mochila(itens_ordenados, capacidade):
    """Percorre os itens ordenados e coloca cada um que ainda couber."""
    escolhidos, peso, valor = [], 0, 0
    for it in itens_ordenados:
        if peso + it["peso"] <= capacidade:
            escolhidos.append(it["nome"])
            peso += it["peso"]
            valor += it["valor"]
    return escolhidos, valor


def heuristica_gulosa(itens, capacidade):
    """Gulosa por densidade. Compara com o melhor item que cabe sozinho e
    devolve o melhor dos dois (garante pelo menos 50% do ótimo).
    Complexidade: O(n log n) (dominada pela ordenação)."""
    escolhidos, valor = preencher_mochila(ordenar_por_densidade(itens), capacidade)
    cabem = [it for it in itens if it["peso"] <= capacidade]
    if cabem:
        melhor = max(cabem, key=lambda it: it["valor"])
        if melhor["valor"] > valor:
            return [melhor["nome"]], melhor["valor"]
    return escolhidos, valor


# ---------------------------------------------------------------------------
# 3. Ambiente dos experimentos
# ---------------------------------------------------------------------------

def info_ambiente():
    cpu = platform.processor() or platform.machine()
    ram = "desconhecida"
    try:
        import psutil  # opcional
        ram = f"{psutil.virtual_memory().total / 1024**3:.1f} GB"
        nucleos_fis = psutil.cpu_count(logical=False)
    except ImportError:
        nucleos_fis = None
        if sys.platform.startswith("linux"):
            with open("/proc/meminfo") as f:
                kb = int(f.readline().split()[1])
                ram = f"{kb / 1024**2:.1f} GB"
    if sys.platform.startswith("linux"):
        # platform.processor() usa `uname -p`, que costuma vir vazio ou
        # "desconhecido"; o nome real do modelo está em /proc/cpuinfo.
        try:
            with open("/proc/cpuinfo") as f:
                for linha in f:
                    if linha.startswith("model name"):
                        cpu = linha.split(":", 1)[1].strip()
                        break
        except OSError:
            pass
    if sys.platform == "win32":
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                               r"HARDWARE\DESCRIPTION\System\CentralProcessor\0")
            cpu = winreg.QueryValueEx(k, "ProcessorNameString")[0].strip()
        except Exception:
            pass
    print("=" * 60)
    print("AMBIENTE DOS EXPERIMENTOS")
    print("=" * 60)
    print(f"Processador      : {cpu}")
    print(f"Núcleos lógicos  : {os.cpu_count()}"
          + (f" (físicos: {nucleos_fis})" if nucleos_fis else ""))
    print(f"Memória RAM      : {ram}")
    print(f"Sistema          : {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Python           : {platform.python_version()}")
    try:
        import matplotlib
        print(f"matplotlib       : {matplotlib.__version__}")
    except ImportError:
        pass
    print()


# ---------------------------------------------------------------------------
# 4. Teste com Carga Sintética Estática
# ---------------------------------------------------------------------------

# Cenário: um técnico vai fazer um atendimento e só pode levar 15 kg de
# equipamentos na mochila. Cada item tem peso (kg) e utilidade (pontos).
ITENS_ESTATICOS = [
    {"nome": "Notebook",        "peso": 3, "valor": 40},
    {"nome": "Multímetro",      "peso": 2, "valor": 25},
    {"nome": "Kit de chaves",   "peso": 4, "valor": 30},
    {"nome": "Furadeira",       "peso": 6, "valor": 46},
    {"nome": "Cabos de rede",   "peso": 3, "valor": 22},
    {"nome": "Roteador reserva","peso": 4, "valor": 32},
    {"nome": "Alicate"        , "peso": 1, "valor": 8},
    {"nome": "Lanterna",        "peso": 2, "valor": 15},
]
CAPACIDADE_ESTATICA = 15


def teste_estatico(salvar_figura=True):
    print("=" * 60)
    print("TESTE 1 - CARGA SINTÉTICA ESTÁTICA")
    print("=" * 60)
    print(f"Capacidade da mochila: {CAPACIDADE_ESTATICA} kg | {len(ITENS_ESTATICOS)} itens "
          f"| {2 ** len(ITENS_ESTATICOS)} combinações\n")
    print(f"{'Item':<18}{'Peso':>6}{'Valor':>7}{'Valor/Peso':>12}")
    for it in ITENS_ESTATICOS:
        print(f"{it['nome']:<18}{it['peso']:>6}{it['valor']:>7}{it['valor']/it['peso']:>12.2f}")
    print()

    t0 = time.perf_counter()
    fb_itens, fb_valor = forca_bruta(ITENS_ESTATICOS, CAPACIDADE_ESTATICA)
    t_fb = time.perf_counter() - t0

    t0 = time.perf_counter()
    h_itens, h_valor = heuristica_gulosa(ITENS_ESTATICOS, CAPACIDADE_ESTATICA)
    t_h = time.perf_counter() - t0

    peso = {it["nome"]: it["peso"] for it in ITENS_ESTATICOS}
    for nome, its, val, t in (("Força Bruta", fb_itens, fb_valor, t_fb),
                              ("Heurística Gulosa", h_itens, h_valor, t_h)):
        print(f"[{nome}]")
        print(f"  Itens escolhidos : {', '.join(its)}")
        print(f"  Peso total       : {sum(peso[i] for i in its)} / {CAPACIDADE_ESTATICA} kg")
        print(f"  Valor total      : {val}")
        print(f"  Tempo            : {t:.2e} s\n")
    print(f"Qualidade da heurística: {100 * h_valor / fb_valor:.1f}% do ótimo\n")

    if salvar_figura:
        desenhar_solucoes(fb_itens, fb_valor, t_fb, h_itens, h_valor, t_h)
    return fb_itens, fb_valor, t_fb, h_itens, h_valor, t_h


def desenhar_solucoes(fb_itens, fb_valor, t_fb, h_itens, h_valor, t_h,
                      arquivo="figura_estatica.png"):
    """Representação visual: cada mochila é uma barra de 15 kg preenchida
    pelos itens escolhidos (largura = peso)."""
    import matplotlib.pyplot as plt
    cores = plt.cm.tab10.colors
    cor = {it["nome"]: cores[i % 10] for i, it in enumerate(ITENS_ESTATICOS)}
    dados = {it["nome"]: it for it in ITENS_ESTATICOS}

    fig, ax = plt.subplots(figsize=(11, 3.6))
    linhas = [(f"Força Bruta\nvalor {fb_valor}  |  {t_fb:.1e} s", fb_itens),
              (f"Heurística Gulosa\nvalor {h_valor}  |  {t_h:.1e} s", h_itens)]
    for y, (rotulo, its) in enumerate(reversed(linhas)):
        x = 0
        for nome in its:
            w = dados[nome]["peso"]
            ax.barh(y, w, left=x, color=cor[nome], edgecolor="white", height=0.6)
            ax.text(x + w / 2, y, f"{nome}\n{w} kg | {dados[nome]['valor']}",
                    ha="center", va="center", fontsize=8, color="white", weight="bold")
            x += w
        ax.barh(y, CAPACIDADE_ESTATICA - x, left=x, color="#e5e5e5", height=0.6)
    ax.set_yticks([0, 1])
    ax.set_yticklabels([l[0] for l in reversed(linhas)])
    ax.set_xlim(0, CAPACIDADE_ESTATICA)
    ax.set_xlabel("Capacidade da mochila (kg)")
    ax.axvline(CAPACIDADE_ESTATICA, color="black", lw=1.5)
    ax.set_title("Carga estática: itens escolhidos por cada algoritmo (W = 15 kg)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    plt.tight_layout()
    plt.savefig(arquivo, dpi=200)
    print(f"Figura salva em {arquivo}\n")
    if os.environ.get("MOSTRAR", "1") == "1" and sys.stdout.isatty():
        plt.show()
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Teste com Carga Sintética Dinâmica
# ---------------------------------------------------------------------------

def gerar_instancia(n, rng):
    """Instância aleatória realista: pesos 1..30 kg, valores 1..100 e
    capacidade = 50% da soma dos pesos (nem tudo cabe, nem quase nada cabe)."""
    itens = [{"nome": f"item{i}", "peso": rng.randint(1, 30), "valor": rng.randint(1, 100)}
             for i in range(n)]
    capacidade = sum(it["peso"] for it in itens) // 2
    return itens, capacidade


def medir(funcao, itens, capacidade, repeticoes):
    melhor_t, resultado = float("inf"), None
    for _ in range(repeticoes):
        t0 = time.perf_counter()
        resultado = funcao(itens, capacidade)
        melhor_t = min(melhor_t, time.perf_counter() - t0)
    return resultado, melhor_t


def teste_dinamico(nmin=4, nmax=22, passo=2, repeticoes=3, seed=42):
    print("=" * 60)
    print("TESTE 2 - CARGA SINTÉTICA DINÂMICA")
    print("=" * 60)
    print(f"n de {nmin} a {nmax} (passo {passo}) | limite rígido da Força Bruta: n = {nmax}")
    print(f"pesos 1-30, valores 1-100, W = 50% da soma dos pesos | seed = {seed} "
          f"| menor tempo de {repeticoes} execuções\n")
    rng = random.Random(seed)
    linhas = []
    print(f"{'Itens':>6} | {'T. Força Bruta (s)':>18} | {'T. Heurística (s)':>17} | "
          f"{'V. ótimo':>8} | {'V. heur.':>8} | {'% ótimo':>7}")
    print("-" * 80)
    for n in range(nmin, nmax + 1, passo):
        itens, cap = gerar_instancia(n, rng)
        rep_fb = repeticoes if n <= 16 else 1   # n grande: 1 execução basta
        (_, v_fb), t_fb = medir(forca_bruta, itens, cap, rep_fb)
        (_, v_h), t_h = medir(heuristica_gulosa, itens, cap, repeticoes)
        pct = 100 * v_h / v_fb if v_fb else 100.0
        linhas.append((n, t_fb, t_h, v_fb, v_h, pct))
        print(f"{n:>6} | {t_fb:>18.2e} | {t_h:>17.2e} | {v_fb:>8} | {v_h:>8} | {pct:>6.1f}%",
              flush=True)
    print()
    salvar_csv(linhas)
    desenhar_grafico(linhas)
    return linhas


def salvar_csv(linhas, arquivo="resultados_dinamica.csv"):
    with open(arquivo, "w", encoding="utf-8") as f:
        f.write("itens,tempo_forca_bruta_s,tempo_heuristica_s,valor_otimo,valor_heuristica,pct_otimo\n")
        for n, t_fb, t_h, v_fb, v_h, pct in linhas:
            f.write(f"{n},{t_fb:.3e},{t_h:.3e},{v_fb},{v_h},{pct:.1f}\n")
    print(f"Tabela salva em {arquivo}")


def desenhar_grafico(linhas, arquivo="grafico_tempos.png"):
    import matplotlib.pyplot as plt
    ns = [l[0] for l in linhas]
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(ns, [l[1] for l in linhas], "o-", label="Força Bruta  O(n·2ⁿ)", color="#c0392b", lw=2)
    ax.plot(ns, [l[2] for l in linhas], "s-", label="Heurística Gulosa  O(n log n)", color="#2471a3", lw=2)
    ax.set_yscale("log")
    ax.set_xlabel("Número de itens (n)")
    ax.set_ylabel("Tempo de execução (s) — escala log")
    ax.set_title("Comparação dos Tempos de Execução")
    ax.set_xticks(ns)
    ax.grid(True, which="both", ls=":", alpha=0.6)
    ax.legend()
    plt.tight_layout()
    plt.savefig(arquivo, dpi=200)
    print(f"Gráfico salvo em {arquivo}\n")
    if os.environ.get("MOSTRAR", "1") == "1" and sys.stdout.isatty():
        plt.show()
    plt.close(fig)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Mochila 0/1: Força Bruta x Heurística")
    p.add_argument("teste", choices=["ambiente", "estatica", "dinamica", "tudo"], nargs="?", default="tudo")
    p.add_argument("--nmin", type=int, default=4)
    p.add_argument("--nmax", type=int, default=22)
    p.add_argument("--passo", type=int, default=2)
    p.add_argument("--repeticoes", type=int, default=3)
    p.add_argument("--seed", type=int, default=42)
    a = p.parse_args()
    if a.teste in ("ambiente", "tudo"):
        info_ambiente()
    if a.teste in ("estatica", "tudo"):
        teste_estatico()
    if a.teste in ("dinamica", "tudo"):
        teste_dinamico(a.nmin, a.nmax, a.passo, a.repeticoes, a.seed)
