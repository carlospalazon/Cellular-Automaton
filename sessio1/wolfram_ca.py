"""
Autòmat Cel·lular Elementar de Wolfram
======================================
Implementació de les regles de Wolfram (0-255) per a autòmats cel·lulars elementals.
Inclou condicions de frontera periòdiques (toroïdal) i de valor fix (0 o 1).
També implementa la versió de "gra guixut" K=2 (coarse-graining).

Referència: https://mathworld.wolfram.com/ElementaryCellularAutomaton.html
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec


# =============================================================================
# FUNCIONS PRINCIPALS
# =============================================================================

def get_wolfram_rule(rule_number: int) -> dict:
    """
    Converteix el número de regla (0-255) en un diccionari de transicions.
    Cada patró de 3 cèl·les veïnes (esquerra, centre, dreta) mapeja a 0 o 1.
    """
    if not 0 <= rule_number <= 255:
        raise ValueError("El número de regla ha de ser entre 0 i 255.")
    
    # La regla en binari de 8 bits (MSB correspon al patró 111)
    bits = format(rule_number, '08b')
    
    rule = {}
    for i, pattern in enumerate(['111', '110', '101', '100', '011', '010', '001', '000']):
        rule[pattern] = int(bits[i])
    
    return rule


def apply_rule(state: np.ndarray, rule: dict, boundary: str = 'periodic') -> np.ndarray:
    """
    Aplica una regla de Wolfram a un estat 1D.
    
    Paràmetres:
        state    : Array 1D d'enters (0 o 1)
        rule     : Diccionari de transicions obtingut de get_wolfram_rule()
        boundary : 'periodic' (toroïdal), 'zero' (frontera fixa a 0), 'one' (frontera fixa a 1)
    
    Retorna:
        Nou estat 1D
    """
    n = len(state)
    new_state = np.zeros(n, dtype=int)
    
    for i in range(n):
        # Obtenim els veïns segons la condició de frontera
        if boundary == 'periodic':
            left  = state[(i - 1) % n]
            center = state[i]
            right = state[(i + 1) % n]
        elif boundary == 'zero':
            left  = state[i - 1] if i > 0 else 0
            center = state[i]
            right = state[i + 1] if i < n - 1 else 0
        elif boundary == 'one':
            left  = state[i - 1] if i > 0 else 1
            center = state[i]
            right = state[i + 1] if i < n - 1 else 1
        else:
            raise ValueError(f"Condició de frontera desconeguda: {boundary}")
        
        pattern = f"{left}{center}{right}"
        new_state[i] = rule[pattern]
    
    return new_state


def run_ca(rule_number: int, width: int = 101, steps: int = 100,
           initial: str = 'single', boundary: str = 'periodic') -> np.ndarray:
    """
    Executa l'autòmat cel·lular i retorna la matriu d'evolució temporal.
    
    Paràmetres:
        rule_number : Número de regla de Wolfram (0-255)
        width       : Amplada del sistema (nombre de cèl·les)
        steps       : Nombre de passos temporals
        initial     : 'single' (un 1 al centre), 'random' (estat aleatori)
        boundary    : Condició de frontera ('periodic', 'zero', 'one')
    
    Retorna:
        Matriu (steps+1) x width
    """
    rule = get_wolfram_rule(rule_number)
    history = np.zeros((steps + 1, width), dtype=int)
    
    # Condició inicial
    if initial == 'single':
        history[0, width // 2] = 1
    elif initial == 'random':
        np.random.seed(42)
        history[0] = np.random.randint(0, 2, width)
    else:
        raise ValueError(f"Condició inicial desconeguda: {initial}")
    
    # Evolució temporal
    for t in range(steps):
        history[t + 1] = apply_rule(history[t], rule, boundary)
    
    return history


# =============================================================================
# COARSE-GRAINING (GRANO GRUESO) K=2
# =============================================================================

def coarse_grain_k2(history: np.ndarray) -> np.ndarray:
    """
    Aplica el coarse-graining de 'gra guixut' amb K=2.
    Cada bloc de 2x2 cèl·les es substitueix per 1 si la majoria és 1, 0 altrament.
    Ignora files/columnes imparells si la mida no és parell.
    
    Retorna la matriu reduïda a la meitat de resolució.
    """
    rows, cols = history.shape
    # Assegurem dimensions parelles
    rows_even = (rows // 2) * 2
    cols_even = (cols // 2) * 2
    
    trimmed = history[:rows_even, :cols_even]
    # Reshape per tenir blocs 2x2
    blocked = trimmed.reshape(rows_even // 2, 2, cols_even // 2, 2)
    # Majoria: si la suma del bloc >= 2, llavors 1
    coarse = (blocked.sum(axis=(1, 3)) >= 2).astype(int)
    
    return coarse


# =============================================================================
# VISUALITZACIÓ
# =============================================================================

def plot_ca(history: np.ndarray, rule_number: int, title_extra: str = '',
            ax: plt.Axes = None, cmap: str = 'binary') -> plt.Axes:
    """Visualitza l'evolució de l'autòmat cel·lular."""
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.imshow(history, cmap=cmap, interpolation='nearest', aspect='auto')
    ax.set_title(f"Regla {rule_number}{title_extra}", fontsize=13, fontweight='bold')
    ax.set_xlabel("Posició de la cèl·la", fontsize=10)
    ax.set_ylabel("Pas temporal", fontsize=10)
    ax.set_xlim(-0.5, history.shape[1] - 0.5)
    ax.set_ylim(history.shape[0] - 0.5, -0.5)  # temps creix cap avall
    return ax


def plot_comparison(rule_number: int, width: int = 100, steps: int = 80,
                    boundary: str = 'periodic', initial: str = 'single'):
    """
    Mostra costat a costat l'autòmat original i la versió coarse-grained K=2.
    """
    history = run_ca(rule_number, width=width, steps=steps,
                     initial=initial, boundary=boundary)
    coarse = coarse_grain_k2(history)
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(
        f"Autòmat Cel·lular de Wolfram — Regla {rule_number}\n"
        f"Frontera: {boundary} | Condició inicial: {initial}",
        fontsize=14, fontweight='bold'
    )
    
    plot_ca(history, rule_number, " (original)", ax=axes[0])
    plot_ca(coarse, rule_number, f" (coarse-grain K=2, {coarse.shape[1]}×{coarse.shape[0]})",
            ax=axes[1], cmap='Blues')
    
    plt.tight_layout()
    plt.savefig(f"wolfram_rule{rule_number}_comparison.png", dpi=150, bbox_inches='tight')
    plt.show()
    print(f"Figura guardada: wolfram_rule{rule_number}_comparison.png")


def plot_multiple_rules(rule_numbers: list, width: int = 101, steps: int = 60,
                        boundary: str = 'periodic'):
    """
    Mostra múltiples regles en una sola figura per comparar comportaments.
    Classifica visualment per tipus (classes de Wolfram).
    """
    n = len(rule_numbers)
    cols = min(n, 4)
    rows = (n + cols - 1) // cols
    
    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 3.5))
    axes = np.array(axes).flatten()
    
    fig.suptitle("Comparació de múltiples regles de Wolfram", fontsize=15, fontweight='bold')
    
    for idx, rule_num in enumerate(rule_numbers):
        history = run_ca(rule_num, width=width, steps=steps, boundary=boundary)
        plot_ca(history, rule_num, ax=axes[idx])
    
    # Ocultem eixos sobrants
    for idx in range(len(rule_numbers), len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.savefig("wolfram_multiple_rules.png", dpi=150, bbox_inches='tight')
    plt.show()
    print("Figura guardada: wolfram_multiple_rules.png")


def analyze_similarity(rule_number: int, width: int = 100, steps: int = 80,
                        boundary: str = 'periodic') -> dict:
    """
    Compara estadísticament l'original i el coarse-grained.
    Retorna mètriques de similitud.
    """
    history = run_ca(rule_number, width=width, steps=steps, boundary=boundary)
    coarse  = coarse_grain_k2(history)
    
    # Redimensionem l'original per comparar pixel a pixel
    orig_small = coarse_grain_k2(history)  # Ja tenim el coarse
    
    density_orig   = history.mean()
    density_coarse = coarse.mean()
    
    # Correlació entre densitats per fila (evolució temporal)
    rows_orig  = history[:coarse.shape[0]*2:2, :coarse.shape[1]*2:2]
    # Agafem una fila de cada 2 i columna de cada 2 (submostral simple)
    row_density_orig   = history.mean(axis=1)[:coarse.shape[0]]
    row_density_coarse = coarse.mean(axis=1)
    
    correlation = np.corrcoef(row_density_orig, row_density_coarse)[0, 1]
    
    results = {
        'regla': rule_number,
        'densitat_original': density_orig,
        'densitat_coarse': density_coarse,
        'correlació_temporal': correlation,
        'mida_original': history.shape,
        'mida_coarse': coarse.shape,
    }
    
    print("\n=== Anàlisi de Similitud (Coarse-Graining K=2) ===")
    print(f"  Regla:                {rule_number}")
    print(f"  Densitat original:    {density_orig:.4f}")
    print(f"  Densitat coarse:      {density_coarse:.4f}")
    print(f"  Correlació temporal:  {correlation:.4f}")
    print(f"  Mida original:        {history.shape}")
    print(f"  Mida coarse:          {coarse.shape}")
    
    return results


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("  AUTÒMAT CEL·LULAR ELEMENTAR DE WOLFRAM")
    print("  Sessió 1 — Pràctica CA")
    print("=" * 60)
    
    # --- 1. Demostració de regles representatives (una per classe de Wolfram) ---
    # Classe 1 (estàtica): Regla 0, 8, 32
    # Classe 2 (periòdica): Regla 4, 108, 218
    # Classe 3 (caòtica): Regla 30, 45, 73
    # Classe 4 (complexa/vida): Regla 110, 124
    
    regles_demo = [0, 30, 90, 110]
    print("\n[1] Generant figura comparativa de 4 regles representatives...")
    plot_multiple_rules(regles_demo, width=101, steps=70, boundary='periodic')
    
    # --- 2. Regla 30 (caòtica) — original vs coarse-grain ---
    print("\n[2] Comparant Regla 30 (caòtica) original vs coarse-grain K=2...")
    plot_comparison(rule_number=30, width=100, steps=80,
                    boundary='periodic', initial='single')
    analyze_similarity(30, width=100, steps=80)
    
    # --- 3. Regla 110 (complexa) — original vs coarse-grain ---
    print("\n[3] Comparant Regla 110 (complexa) original vs coarse-grain K=2...")
    plot_comparison(rule_number=110, width=100, steps=80,
                    boundary='periodic', initial='single')
    analyze_similarity(110, width=100, steps=80)
    
    # --- 4. Regla 90 (fractal) — condició aleatòria ---
    print("\n[4] Regla 90 amb condició inicial aleatòria...")
    plot_comparison(rule_number=90, width=100, steps=80,
                    boundary='zero', initial='random')
    analyze_similarity(90, width=100, steps=80)
    
    print("\nFet! Tots els gràfics han estat generats.")
