"""
Sessió 2 — Propagació d'Incendi Forestal amb Autòmat Cel·lular 2D
==================================================================
Model m:n-CA^k amb quatre capes:
  · Capa 1: Vegetació  (derivada dels polígons vegetation.vec / vegetation.dvc)
             Valor = hores que triga a cremar-se una cel·la
  · Capa 2: Humitat    (derivada de les categories Initialize.doc / Initialize.img)
             Valor = hores d'espera fins que el foc pot encendre's
  · Capa 3: Estat foc  (calculada internament)
             0 = pendent de cremar | 1 = cremant | 2 = cremat
  · Capa 4: Vent       (fitxer vectorial vegetation.vec / vegetation.dvc)
             Modifica la probabilitat de propagació per direcció

Dades reals llegides dels fitxers IDRISI proporcionats:
  · Initialize.doc → 10 categories de cobertura del sòl (Catalunya)
  · Initialize.img → codis: LL, CT, TE, GR, CC, AA, BS, BN, BC, CAT
  · vegetation.vec → 3 polígons en espai [0,100]²:
        Polígon 1 (fons):     rectangle complet → CT (Conreu Temporal)
        Polígon 2 (bosc):     zona irregular    → BS (Bosc, 12h combustió)
        Polígon 20 (arbreda): zona petita       → AA (Arbreda, 15h combustió)
  · vegetation.dvc → metadades del vec (espai [0,100]², polígons)

Condició de frontera: fixa (les cel·les de la vora no es cremen).
Veïnatge: Moore (8 veïns).
Unitat de temps: 1 hora.

Ús:
    pip install numpy matplotlib pillow
    python forest_fire_ca.py

    # Opcions addicionals:
    python forest_fire_ca.py --data-dir /ruta/als/fitxers
    python forest_fire_ca.py --wind-angle 90 --wind-speed 8
    python forest_fire_ca.py --rows 80 --cols 100 --steps 300
    python forest_fire_ca.py --no-anim   # salta la generació del GIF
"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.animation as animation


# =============================================================================
# DADES REALS LLEGIDES DELS FITXERS IDRISI
# =============================================================================

# --- Initialize.doc + Initialize.img ---
# 10 categories de cobertura del sòl de Catalunya
LAND_PROPS = {
    #  Codi : (veg_hores, hum_hores, color_hex,  nom_complet)
    'LL':  (0,   6,  '#2a5fa5', 'Llac / Llacuna'),
    'CT':  (3,   1,  '#c8b560', 'Conreu Temporal'),
    'TE':  (2,   0,  '#b89a6a', 'Terra Erma'),
    'GR':  (6,   1,  '#8fad5a', 'Garriga'),
    'CC':  (4,   1,  '#d4c040', 'Conreu Continu'),
    'AA':  (15,  2,  '#1a6b2a', 'Arbreda Aciculifòlia'),
    'BS':  (12,  2,  '#2d8a3e', 'Bosc'),
    'BN':  (14,  3,  '#1e7a30', 'Bosc Nadiu'),
    'BC':  (11,  2,  '#3a9a50', 'Bosc de Caducifolis'),
    'CAT': (0,   0,  '#444444', 'Frontera Catalunya'),
}

# --- vegetation.vec ---
# Tres polígons en espai normalitzat [0,100] x [0,100]
# Llegits directament del fitxer: id npoints \n x y \n ...
VEC_POLYGONS_DEFAULT = [
    {
        'id': 1,  'land_code': 'CT',
        'pts': np.array([[0,0],[0,100],[100,100],[100,0]], dtype=float),
    },
    {
        'id': 2,  'land_code': 'BS',
        'pts': np.array([[20,50],[30,60],[60,50],[60,10],[20,10]], dtype=float),
    },
    {
        'id': 20, 'land_code': 'AA',
        'pts': np.array([[30,20],[30,25],[40,30],[50,20]], dtype=float),
    },
]

# Vent derivat del primer segment del polígon 2 (BS):
#   punt (20,50) → punt (30,60): dx=10, dy=10 → angle = 45° NE
WIND_ANGLE_DEFAULT = 45.0   # graus (0°=Est, 90°=Nord)
WIND_SPEED_DEFAULT = 4.0    # escala 0–15


# =============================================================================
# LECTORS DE FORMAT IDRISI
# =============================================================================

def parse_idrisi_doc(filepath: str) -> dict:
    """Llegeix la capçalera d'un fitxer IDRISI32 (.doc)."""
    meta = {}
    with open(filepath, 'r', errors='ignore') as f:
        for line in f:
            if ':' in line:
                key, _, val = line.partition(':')
                meta[key.strip().lower()] = val.strip()
    return meta


def parse_vec_file(vec_path: str) -> list:
    """
    Llegeix un fitxer vectorial IDRISI31 (.vec).
    Format: cada polígon comença amb 'id npoints', després npoints parells x y.
    Retorna: [{'id': int, 'pts': np.ndarray, 'land_code': str}, ...]
    """
    id_to_code = {1: 'CT', 2: 'BS', 20: 'AA'}   # mapeig conegut dels fitxers
    with open(vec_path, 'r', errors='ignore') as f:
        lines = [l.strip() for l in f if l.strip()]
    polygons, i = [], 0
    while i < len(lines):
        parts = lines[i].split()
        if len(parts) == 2:
            try:
                pid, npts = int(parts[0]), int(parts[1])
                if npts > 0:
                    coords = []
                    for k in range(1, npts + 1):
                        if i + k < len(lines):
                            xy = lines[i + k].split()
                            coords.append([float(xy[0]), float(xy[1])])
                    polygons.append({
                        'id': pid,
                        'pts': np.array(coords, dtype=float),
                        'land_code': id_to_code.get(pid, 'CT'),
                    })
                    i += npts + 1
                    continue
            except (ValueError, IndexError):
                pass
        i += 1
    return polygons


def wind_from_vec(polygons: list) -> tuple:
    """
    Extreu direcció i intensitat de vent del primer segment del polígon BS (ID=2).
    Retorna: (angle_deg, speed)
    """
    for poly in polygons:
        if poly['id'] == 2 and len(poly['pts']) >= 2:
            dx = poly['pts'][1][0] - poly['pts'][0][0]
            dy = poly['pts'][1][1] - poly['pts'][0][1]
            if abs(dx) + abs(dy) > 1e-6:
                angle = float(np.degrees(np.arctan2(dy, dx)))
                speed = float(min(np.sqrt(dx**2 + dy**2) * 0.4, 15.0))
                return angle, speed
    return WIND_ANGLE_DEFAULT, WIND_SPEED_DEFAULT


# =============================================================================
# CONSTRUCCIÓ DEL TERRENY A PARTIR DELS POLÍGONS
# =============================================================================

def point_in_polygon(px: float, py: float, pts: np.ndarray) -> bool:
    """Ray-casting: True si (px,py) és dins el polígon convex o còncau."""
    n = len(pts)
    inside, j = False, n - 1
    for i in range(n):
        xi, yi = pts[i]
        xj, yj = pts[j]
        if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def build_terrain(rows: int, cols: int, polygons: list) -> tuple:
    """
    Rasteritza els polígons vectorials sobre un grid rows×cols.
    L'espai vectorial és [0,100]² i es mapeja linealment al grid.

    Retorna:
        vegetation (np.ndarray): hores de combustió per cel·la
        humidity   (np.ndarray): hores de retard d'ignició per cel·la
        land_map   (list[list]): codi de categoria per cel·la
    """
    vegetation = np.zeros((rows, cols), dtype=float)
    humidity   = np.zeros((rows, cols), dtype=float)
    land_map   = [['CT'] * cols for _ in range(rows)]

    for r in range(rows):
        for c in range(cols):
            x = (c / cols) * 100.0
            y = (r / rows) * 100.0
            code = 'CT'                        # categoria per defecte (fons)
            for poly in polygons:
                if point_in_polygon(x, y, poly['pts']):
                    code = poly['land_code']   # el darrer polígon guanya
            props = LAND_PROPS[code]
            vegetation[r][c] = props[0]
            humidity[r][c]   = props[1]
            land_map[r][c]   = code

    return vegetation, humidity, land_map


def build_land_color_image(land_map: list) -> np.ndarray:
    """Genera una imatge RGB del mapa de categories per a matplotlib."""
    rows = len(land_map)
    cols = len(land_map[0])
    img  = np.zeros((rows, cols, 3), dtype=float)
    for r in range(rows):
        for c in range(cols):
            img[r, c] = mcolors.to_rgb(LAND_PROPS[land_map[r][c]][2])
    return img


# =============================================================================
# MODEL DE L'AUTÒMAT CEL·LULAR
# =============================================================================

NEIGHBOR_OFFSETS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
EMPTY = 0;  BURNING = 1;  BURNED = 2


def wind_factor(dr: int, dc: int, wind_angle_deg: float, wind_speed: float) -> float:
    """
    Factor de propagació per al veí (dr, dc) tenint en compte el vent.
    > 1 si el veí és en la direcció del vent; < 1 en sentit contrari.
    """
    neighbor_angle = np.degrees(np.arctan2(-dr, dc))
    delta          = np.radians(neighbor_angle - wind_angle_deg)
    alignment      = np.cos(delta)
    base           = min(wind_speed / 8.0, 1.8)
    return max(0.05, 1.0 + base * alignment)


class ForestFireCA:
    """
    Autòmat Cel·lular 2D — Propagació d'incendi forestal.

    Regles de transició per cel·la (pas = 1 hora):
      BURNING + burn_left > 0  →  burn_left -= 1           (segueix cremant)
      BURNING + burn_left = 0  →  BURNED                   (exhaurit)
      EMPTY   + veí BURNING + humitat > 0  →  humitat -= 1 (s'asseca)
      EMPTY   + veí BURNING + humitat = 0  →  BURNING      (ignició, prob. vent)
    """

    def __init__(self, vegetation: np.ndarray, humidity: np.ndarray,
                 ignition: np.ndarray,
                 wind_angle: float = WIND_ANGLE_DEFAULT,
                 wind_speed: float = WIND_SPEED_DEFAULT,
                 land_map: list = None):

        self.rows, self.cols = vegetation.shape
        self.wind_angle      = wind_angle
        self.wind_speed      = wind_speed
        self.land_map        = land_map

        # Capes base (immutables)
        self.vegetation_base = vegetation.copy()
        self.humidity_base   = humidity.copy()

        # Estat dinàmic
        self.fire_state    = np.zeros((self.rows, self.cols), dtype=np.int8)
        self.humidity_left = humidity.copy().astype(float)
        self.burn_left     = vegetation.copy().astype(float)

        # Focus d'ignició inicial
        mask = ignition > 0
        self.fire_state[mask]    = BURNING
        self.humidity_left[mask] = 0.0

        # Historial i estadístiques
        self.history = [self.fire_state.copy()]
        self.time    = 0
        self.stats   = {'burned': [], 'burning': [], 'pending': []}
        self._record()

    def _record(self):
        self.stats['burned'].append(int((self.fire_state == BURNED).sum()))
        self.stats['burning'].append(int((self.fire_state == BURNING).sum()))
        self.stats['pending'].append(int((self.fire_state == EMPTY).sum()))

    def step(self) -> np.ndarray:
        """Avança un pas temporal (1 hora)."""
        nf = self.fire_state.copy()
        nh = self.humidity_left.copy()
        nb = self.burn_left.copy()

        for r in range(1, self.rows - 1):
            for c in range(1, self.cols - 1):
                s = self.fire_state[r, c]

                if s == BURNING:
                    if nb[r, c] > 0:
                        nb[r, c] -= 1.0
                    else:
                        nf[r, c] = BURNED

                elif s == EMPTY and self.vegetation_base[r, c] > 0:
                    burning_nb = [
                        (dr, dc) for dr, dc in NEIGHBOR_OFFSETS
                        if self.fire_state[r+dr, c+dc] == BURNING
                    ]
                    if burning_nb:
                        if nh[r, c] > 0:
                            nh[r, c] -= 1.0
                        else:
                            max_wf = max(
                                wind_factor(dr, dc, self.wind_angle, self.wind_speed)
                                for dr, dc in burning_nb
                            )
                            if np.random.random() < min(max_wf / 2.0, 1.0):
                                nf[r, c] = BURNING

        self.fire_state    = nf
        self.humidity_left = nh
        self.burn_left     = nb
        self.time         += 1
        self.history.append(self.fire_state.copy())
        self._record()
        return self.fire_state

    def run(self, max_steps: int = 200, stop_when_done: bool = True,
            verbose: bool = True):
        """Executa la simulació completa."""
        if verbose:
            print(f"\n  Grid: {self.rows}×{self.cols} | "
                  f"Vent: {self.wind_angle:.1f}° | "
                  f"Intensitat: {self.wind_speed:.1f}")
            print(f"  Focus inicial: {self.stats['burning'][0]} cel·les\n")
        for _ in range(max_steps):
            self.step()
            if verbose and self.time % 10 == 0:
                print(f"  t={self.time:4d}h | "
                      f"Cremant:{self.stats['burning'][-1]:5d} | "
                      f"Cremat:{self.stats['burned'][-1]:5d} | "
                      f"Pendent:{self.stats['pending'][-1]:5d}")
            if stop_when_done and self.stats['burning'][-1] == 0:
                if verbose:
                    print(f"\n  → Foc extingit a t={self.time}h")
                break
        if verbose:
            total  = self.rows * self.cols
            burned = self.stats['burned'][-1]
            print(f"\n  Simulació completada: {self.time}h | "
                  f"Cremat: {burned}/{total} ({burned/total*100:.1f}%)")


# =============================================================================
# VISUALITZACIONS
# =============================================================================

def _dark(fig):
    fig.patch.set_facecolor('#0c0f0a')
    return fig

def _ax(ax):
    ax.set_facecolor('#111')
    ax.tick_params(colors='#555')
    for sp in ax.spines.values():
        sp.set_edgecolor('#222')


def plot_initial_layers(vegetation, humidity, fire_state, land_map,
                        wind_angle, wind_speed, polygons,
                        save='fire_layers_initial.png'):
    """Quatre subplots: categories, vegetació, humitat, estat inicial."""
    fig, axes = plt.subplots(1, 4, figsize=(18, 5))
    _dark(fig)
    fig.suptitle("Capes inicials — Incendi Forestal (dades IDRISI)",
                 color='#ff8c42', fontsize=13, fontweight='bold')

    rows, cols = vegetation.shape

    # 1. Mapa de categories + contorns polígons
    axes[0].imshow(build_land_color_image(land_map),
                   interpolation='nearest', aspect='auto')
    for poly in polygons:
        if poly['id'] == 1:
            continue
        px = poly['pts'][:, 0] / 100 * cols
        py = poly['pts'][:, 1] / 100 * rows
        col = '#64e696' if poly['id'] == 2 else '#ffd166'
        axes[0].plot(np.append(px, px[0]), np.append(py, py[0]),
                     '-', color=col, lw=1.5, label=poly['land_code'])
    axes[0].legend(fontsize=7, facecolor='#111', labelcolor='white', loc='lower right')
    axes[0].set_title("Cobertura del sòl\n(categories + polígons vec)", color='#ccc', fontsize=9)

    # 2. Vegetació
    im1 = axes[1].imshow(vegetation, cmap='YlGn', aspect='auto',
                          vmin=0, vmax=16, interpolation='nearest')
    axes[1].set_title("Vegetació\n(hores combustió)", color='#ccc', fontsize=9)
    plt.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)

    # 3. Humitat
    im2 = axes[2].imshow(humidity, cmap='Blues', aspect='auto',
                          vmin=0, vmax=6, interpolation='nearest')
    axes[2].set_title("Humitat\n(hores retard)", color='#ccc', fontsize=9)
    plt.colorbar(im2, ax=axes[2], fraction=0.046, pad=0.04)

    # 4. Estat inicial + vent
    fcmap = mcolors.ListedColormap(['#1a3a1a', '#ff4500', '#2a2a2a'])
    fnorm = mcolors.BoundaryNorm([0, 1, 2, 3], fcmap.N)
    axes[3].imshow(fire_state, cmap=fcmap, norm=fnorm,
                   aspect='auto', interpolation='nearest')
    cy, cx = rows * 0.1, cols * 0.85
    dx =  np.cos(np.radians(wind_angle)) * wind_speed * 1.5
    dy = -np.sin(np.radians(wind_angle)) * wind_speed * 1.5
    axes[3].annotate('', xy=(cx+dx, cy+dy), xytext=(cx, cy),
        arrowprops=dict(arrowstyle='->', color='cyan', lw=2))
    axes[3].text(cx, cy-2, f'Vent\n{wind_angle:.0f}°', color='cyan',
                 fontsize=7, ha='center')
    axes[3].set_title("Estat inicial\n+ Vent (vec)", color='#ccc', fontsize=9)
    axes[3].legend(handles=[
        mpatches.Patch(color='#1a3a1a', label='Pendent'),
        mpatches.Patch(color='#ff4500', label='Cremant'),
    ], fontsize=7, facecolor='#111', labelcolor='white', loc='lower right')

    for ax in axes:
        _ax(ax)
    plt.tight_layout()
    plt.savefig(save, dpi=150, bbox_inches='tight', facecolor='#0c0f0a')
    print(f"  Guardat: {save}")
    plt.show()


def plot_final_comparison(ca, save='fire_final_state.png'):
    """Panell inicial vs final amb estadístiques."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    _dark(fig)
    fig.suptitle("Propagació de l'incendi — Inicial vs Final",
                 color='#ff8c42', fontsize=14, fontweight='bold')

    fcmap = mcolors.ListedColormap(['#1a3a1a', '#ff4500', '#141208'])
    fnorm = mcolors.BoundaryNorm([0, 1, 2, 3], fcmap.N)

    for ax, frame, title in [
        (axes[0], ca.history[0],  "t = 0h (Inici)"),
        (axes[1], ca.history[-1], f"t = {ca.time}h (Final)"),
    ]:
        vshow = ca.vegetation_base.copy()
        vshow[frame == BURNED] = 0
        ax.imshow(vshow, cmap='YlGn', vmin=0, vmax=ca.vegetation_base.max(),
                  aspect='auto', interpolation='nearest', alpha=0.55)
        ax.imshow(frame, cmap=fcmap, norm=fnorm,
                  aspect='auto', interpolation='nearest', alpha=0.85)
        ax.set_title(title, color='#ccc', fontsize=12)
        _ax(ax)

    # Fletxa vent
    rows, cols = ca.history[-1].shape
    cx, cy = cols * 0.87, rows * 0.08
    dx =  np.cos(np.radians(ca.wind_angle)) * ca.wind_speed * 2
    dy = -np.sin(np.radians(ca.wind_angle)) * ca.wind_speed * 2
    axes[1].annotate('', xy=(cx+dx, cy+dy), xytext=(cx, cy),
        arrowprops=dict(arrowstyle='->', color='cyan', lw=2.5))
    axes[1].text(cx, cy-3, f'Vent {ca.wind_angle:.0f}°\n{ca.wind_speed:.1f}u/h',
                 color='cyan', fontsize=7, ha='center')

    total, burned = ca.rows * ca.cols, ca.stats['burned'][-1]
    axes[1].text(0.02, 0.97,
                 f"Cremat: {burned} ({burned/total*100:.1f}%)\nDurada: {ca.time}h",
                 transform=axes[1].transAxes, color='#ff8c42', fontsize=9, va='top',
                 bbox=dict(boxstyle='round,pad=0.4', facecolor='#111', alpha=0.8))
    axes[1].legend(handles=[
        mpatches.Patch(color='#2a7a2a', label='Vegetació'),
        mpatches.Patch(color='#ff4500', label='Cremant'),
        mpatches.Patch(color='#141208', label='Cremat'),
    ], facecolor='#111', labelcolor='white', fontsize=9, loc='lower right')

    plt.tight_layout()
    plt.savefig(save, dpi=150, bbox_inches='tight', facecolor='#0c0f0a')
    print(f"  Guardat: {save}")
    plt.show()


def plot_evolution_stats(ca, save='fire_stats.png'):
    """Dos subplots: front actiu i àrea total cremada."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    _dark(fig)
    fig.suptitle("Evolució temporal de l'incendi forestal",
                 color='#ff8c42', fontsize=13, fontweight='bold')

    t = list(range(len(ca.stats['burned'])))
    ax1.fill_between(t, ca.stats['burning'], color='#ff4500', alpha=0.75,
                     label='Front actiu (cremant)')
    ax1.plot(t, ca.stats['burning'], color='#ff6600', lw=1.5)
    ax1.set_ylabel("Cel·les cremant", color='#aaa')
    ax1.legend(facecolor='#1a1a1a', labelcolor='white', fontsize=10)
    _ax(ax1)
    ax1.grid(color='#1e1e1e', linestyle='--', alpha=0.5)

    ax2.fill_between(t, ca.stats['burned'], color='#555', alpha=0.7,
                     label='Total cremat (acumulat)')
    ax2.plot(t, ca.stats['burned'], color='#888', lw=1.5)
    t_max = ca.stats['burning'].index(max(ca.stats['burning']))
    ax2.axvline(t_max, color='#ff4500', lw=1, ls='--', alpha=0.5,
                label=f'Màxim front (t={t_max}h)')
    ax2.set_xlabel("Temps (hores)", color='#aaa')
    ax2.set_ylabel("Cel·les cremades (total)", color='#aaa')
    ax2.legend(facecolor='#1a1a1a', labelcolor='white', fontsize=10)
    _ax(ax2)
    ax2.grid(color='#1e1e1e', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(save, dpi=150, bbox_inches='tight', facecolor='#0c0f0a')
    print(f"  Guardat: {save}")
    plt.show()


def generate_animation(ca, output='fire_animation.gif', fps=8, step_skip=2):
    """Animació GIF de la propagació."""
    frames = ca.history[::step_skip]
    print(f"  Generant {len(frames)} frames @ {fps} fps...")

    fig, ax = plt.subplots(figsize=(9, 7))
    _dark(fig);  _ax(ax)
    veg_norm = plt.Normalize(0, max(ca.vegetation_base.max(), 1))

    def draw(i):
        ax.clear();  _ax(ax)
        frame = frames[i]
        t_lbl = i * step_skip
        vshow = ca.vegetation_base.copy().astype(float)
        vshow[frame == BURNED] = 0
        ax.imshow(vshow, cmap='YlGn', norm=veg_norm,
                  aspect='auto', interpolation='nearest', alpha=0.5)
        fire_rgba = np.zeros((*frame.shape, 4))
        fire_rgba[frame == BURNING] = [1.0, 0.27, 0.0, 0.95]
        fire_rgba[frame == BURNED]  = [0.08, 0.07, 0.04, 0.90]
        ax.imshow(fire_rgba, aspect='auto', interpolation='nearest')
        rows, cols = frame.shape
        cx, cy = cols * 0.87, rows * 0.08
        dx =  np.cos(np.radians(ca.wind_angle)) * ca.wind_speed * 1.8
        dy = -np.sin(np.radians(ca.wind_angle)) * ca.wind_speed * 1.8
        ax.annotate('', xy=(cx+dx, cy+dy), xytext=(cx, cy),
            arrowprops=dict(arrowstyle='->', color='cyan', lw=2))
        ax.text(cx, cy-3, f'{ca.wind_angle:.0f}°', color='cyan',
                fontsize=8, ha='center')
        ax.set_title(
            f"t = {t_lbl}h  |  🔥 {int((frame==BURNING).sum())} cremant  |"
            f"  ⬛ {int((frame==BURNED).sum())} cremat",
            color='#ff8c42', fontsize=11, fontweight='bold', pad=6)

    ani = animation.FuncAnimation(fig, draw, frames=len(frames),
                                  interval=1000//fps, repeat=True)
    ani.save(output, writer='pillow', fps=fps,
             savefig_kwargs={'facecolor': '#0c0f0a'})
    plt.close(fig)
    print(f"  Guardat: {output}")


def plot_land_legend(save='fire_legend.png'):
    """Llegenda de les 10 categories IDRISI."""
    fig, ax = plt.subplots(figsize=(7, 4))
    _dark(fig);  ax.axis('off')
    ax.set_title("Categories IDRISI (Initialize.doc)",
                 color='#ff8c42', fontsize=12, fontweight='bold')
    for i, (code, props) in enumerate(LAND_PROPS.items()):
        veg, hum, color, name = props
        y = 1 - (i + 0.5) / len(LAND_PROPS)
        ax.add_patch(mpatches.FancyBboxPatch(
            (0.01, y - 0.035), 0.06, 0.06,
            boxstyle="round,pad=0.005", facecolor=color, edgecolor='#333'))
        ax.text(0.10, y, f"{code:5s} — {name}",
                color='#ccc', fontsize=10, va='center', fontfamily='monospace')
        ax.text(0.65, y, f"Veg:{veg:2d}h  Hum:{hum}h",
                color='#888', fontsize=9, va='center', fontfamily='monospace')
    plt.tight_layout()
    plt.savefig(save, dpi=150, bbox_inches='tight', facecolor='#0c0f0a')
    print(f"  Guardat: {save}")
    plt.show()


# =============================================================================
# PROGRAMA PRINCIPAL
# =============================================================================

def main():
    ap = argparse.ArgumentParser(
        description="Simulació d'incendi forestal CA 2D (Sessió 2)")
    ap.add_argument('--data-dir',   default='.',
                    help='Directori amb els fitxers IDRISI (default: .)')
    ap.add_argument('--rows',       type=int,   default=60)
    ap.add_argument('--cols',       type=int,   default=80)
    ap.add_argument('--steps',      type=int,   default=200)
    ap.add_argument('--wind-angle', type=float, default=None,
                    help='Angle del vent en graus (0=Est, 90=Nord)')
    ap.add_argument('--wind-speed', type=float, default=None,
                    help='Intensitat del vent 0–15')
    ap.add_argument('--no-anim',    action='store_true',
                    help='No generar animació GIF')
    ap.add_argument('--seed',       type=int,   default=42)
    args = ap.parse_args()

    np.random.seed(args.seed)

    print("=" * 65)
    print("  SESSIÓ 2 — PROPAGACIÓ D'INCENDI FORESTAL AMB CA 2D")
    print("  Model m:n-CA^k  ·  Dades IDRISI32/31 (Catalunya)")
    print("=" * 65)

    # ── 1. Polígons vec ──────────────────────────────────────────────────────
    vec_path = os.path.join(args.data_dir, 'vegetation.vec')
    if os.path.exists(vec_path):
        print(f"\n[1] Llegint {vec_path}")
        polygons = parse_vec_file(vec_path)
        print(f"   {len(polygons)} polígons llegits:")
        for p in polygons:
            bb = (p['pts'][:,0].min(), p['pts'][:,0].max(),
                  p['pts'][:,1].min(), p['pts'][:,1].max())
            print(f"   ID={p['id']:2d} ({p['land_code']}) "
                  f"{len(p['pts'])} vèrtexs  X[{bb[0]:.0f},{bb[1]:.0f}] Y[{bb[2]:.0f},{bb[3]:.0f}]")
    else:
        print("\n[1] vegetation.vec no trobat → polígons hardcoded")
        polygons = VEC_POLYGONS_DEFAULT

    # ── 2. Vent ──────────────────────────────────────────────────────────────
    w_ang, w_spd = wind_from_vec(polygons)
    wind_angle = args.wind_angle if args.wind_angle is not None else w_ang
    wind_speed = args.wind_speed if args.wind_speed is not None else w_spd
    dirs = ["E","NE","N","NO","O","SO","S","SE"]
    dname = dirs[round(((wind_angle % 360)+360) % 360 / 45) % 8]
    print(f"\n[2] Vent: {wind_angle:.1f}° ({dname}), intensitat {wind_speed:.1f}")

    # ── 3. Terreny ───────────────────────────────────────────────────────────
    print(f"\n[3] Rasteritzant polígons → grid {args.rows}×{args.cols}...")
    vegetation, humidity, land_map = build_terrain(args.rows, args.cols, polygons)

    ignition = np.zeros((args.rows, args.cols), dtype=int)
    ignition[1:4, 1:4] = 1   # focus a la cantonada superior-esquerra (CT)

    print(f"   Veg  [{vegetation.min():.0f}–{vegetation.max():.0f}]h  "
          f"mitjana={vegetation.mean():.1f}h")
    print(f"   Hum  [{humidity.min():.0f}–{humidity.max():.0f}]h  "
          f"mitjana={humidity.mean():.1f}h")

    # Resum categories
    print("\n[4] Categories presents:")
    codes_present = sorted({land_map[r][c]
                             for r in range(args.rows) for c in range(args.cols)})
    for code in codes_present:
        n = sum(land_map[r][c] == code
                for r in range(args.rows) for c in range(args.cols))
        p = LAND_PROPS[code]
        print(f"   {code:5s}  {p[3]:30s}  {n:5d} cel·les  "
              f"veg={p[0]:2d}h  hum={p[1]}h")

    # ── 5. Visualitzar capes ─────────────────────────────────────────────────
    print("\n[5] Visualitzant capes inicials...")
    plot_land_legend()
    plot_initial_layers(vegetation, humidity, ignition, land_map,
                        wind_angle, wind_speed, polygons)

    # ── 6. Simulació ─────────────────────────────────────────────────────────
    print(f"\n[6] Executant simulació (màxim {args.steps} passos)...")
    ca = ForestFireCA(vegetation, humidity, ignition,
                     wind_angle, wind_speed, land_map)
    ca.run(max_steps=args.steps, stop_when_done=True, verbose=True)

    # ── 7. Resultats ─────────────────────────────────────────────────────────
    print("\n[7] Generant gràfics finals...")
    plot_final_comparison(ca)
    plot_evolution_stats(ca)

    # ── 8. Animació ──────────────────────────────────────────────────────────
    if not args.no_anim:
        print("\n[8] Generant animació GIF...")
        generate_animation(ca)
    else:
        print("\n[8] Animació omesa (--no-anim)")

    # ── 9. Resum ─────────────────────────────────────────────────────────────
    total  = ca.rows * ca.cols
    burned = ca.stats['burned'][-1]
    t_max  = ca.stats['burning'].index(max(ca.stats['burning']))

    print("\n" + "=" * 65)
    print("  RESUM FINAL")
    print(f"  Durada simulació:   {ca.time} hores")
    print(f"  Àrea cremada:       {burned}/{total} cel·les ({burned/total*100:.1f}%)")
    print(f"  Màxim front actiu:  t={t_max}h ({max(ca.stats['burning'])} cel·les)")
    print(f"  Vent:               {wind_angle:.1f}° ({dname}), intensitat {wind_speed:.1f}")
    print(f"  Grid:               {args.rows}×{args.cols}")
    print("=" * 65)
    print("\nFitxers generats:")
    print("  fire_legend.png          — Llegenda categories IDRISI")
    print("  fire_layers_initial.png  — 4 capes inicials")
    print("  fire_final_state.png     — Inicial vs Final")
    print("  fire_stats.png           — Evolució temporal")
    if not args.no_anim:
        print("  fire_animation.gif       — Animació de la propagació")


if __name__ == "__main__":
    main()
