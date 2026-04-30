"""
Simulador d'Incendi Forestal — Model m:n-CA^k
==============================================
Capes:
  L1 – Vegetació  : hores que triga a cremar-se una cel·la
  L2 – Humitat    : hores de retard fins que el foc s'inicia
  L3 – Propagació : 0=pendent | 1=eixugant | 2=cremant | 3=cremat

Ús:
  python incendi_forestal.py                         # genera terreny alpí aleatori
  python incendi_forestal.py --terrain mediterranean # tipus de terreny
  python incendi_forestal.py --veg veg.rst --hum hum.rst  # fitxers IDRISI32
  python incendi_forestal.py --seed 12345 --rows 40 --cols 50
  python incendi_forestal.py --help
"""

import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.widgets import Button, Slider
from matplotlib.animation import FuncAnimation
import sys, os

# ─── PERLIN-LIKE NOISE ────────────────────────────────────────────────────────
def make_noise(seed=None):
    rng = np.random.default_rng(seed)
    perm = rng.permutation(256).astype(int)
    P = np.tile(perm, 2)

    def fade(t): return t * t * t * (t * (t * 6 - 15) + 10)
    def lerp(t, a, b): return a + t * (b - a)

    def grad(h, x, y):
        h = h & 3
        u = x if h < 2 else y
        w = y if h < 2 else x
        return (u if (h & 1) == 0 else -u) + (w if (h & 2) == 0 else -w)

    def noise(x, y):
        xi, yi = int(np.floor(x)) & 255, int(np.floor(y)) & 255
        xf, yf = x - np.floor(x), y - np.floor(y)
        u, v = fade(xf), fade(yf)
        aa = P[P[xi] + yi]; ab = P[P[xi] + yi + 1]
        ba = P[P[xi+1] + yi]; bb = P[P[xi+1] + yi + 1]
        return lerp(v,
                    lerp(u, grad(aa, xf, yf),   grad(ba, xf-1, yf)),
                    lerp(u, grad(ab, xf, yf-1), grad(bb, xf-1, yf-1)))

    def octave_noise(x, y, octs=4, persist=0.55):
        val = amp = freq = 1.0
        val = 0.0; mx = 0.0
        for _ in range(octs):
            val += noise(x * freq, y * freq) * amp
            mx += amp; amp *= persist; freq *= 2
        return val / mx

    return octave_noise


# ─── TERRAIN PRESETS ─────────────────────────────────────────────────────────
PRESETS = {
    "mediterranean": dict(
        label="Mediterrani", veg_max=11, hum_max=4, scale=3.5,
        river_count=1, lake_count=0,
        levels=[
            (0.15, 0,     0),
            (0.35, 1,     2),
            (0.60, 3,     6),
            (0.80, 6,     9),
            (1.00, 7,    11),
        ]
    ),
    "alpine": dict(
        label="Alpí", veg_max=20, hum_max=9, scale=2.5,
        river_count=2, lake_count=1,
        levels=[
            (0.08, 0,     0),
            (0.20, 1,     3),
            (0.45, 4,     8),
            (0.72, 9,    14),
            (1.00, 13,   20),
        ]
    ),
    "savanna": dict(
        label="Sabana", veg_max=8, hum_max=5, scale=4.0,
        river_count=1, lake_count=0,
        levels=[
            (0.20, 0,     0),
            (0.50, 1,     3),
            (0.72, 2,     5),
            (0.88, 4,     7),
            (1.00, 5,     8),
        ]
    ),
    "coastal": dict(
        label="Costaner", veg_max=14, hum_max=6, scale=3.0,
        river_count=1, lake_count=1,
        levels=[
            (0.12, 0,     0),
            (0.28, 1,     2),
            (0.50, 2,     5),
            (0.72, 5,     9),
            (1.00, 8,    14),
        ]
    ),
}


def generate_terrain(rows, cols, terrain="alpine", seed=None):
    """Genera capes de vegetació i humitat amb patrons geogràfics realistes."""
    if seed is None:
        seed = int(np.random.randint(1, 99999))
    preset = PRESETS[terrain]
    rng = np.random.default_rng(seed)
    noise = make_noise(seed)
    moist_noise = make_noise(seed + 7919)

    # Mapa d'elevació (soroll Perlin 4 octaves)
    elev = np.zeros((rows, cols))
    scale = preset["scale"]
    for r in range(rows):
        for c in range(cols):
            nx = c / cols * scale
            ny = r / rows * scale
            e = noise(nx, ny, 4, 0.55)
            elev[r, c] = (e + 1) / 2   # normalitzat 0..1

    # Mapa de humitat base (soroll independent + boost per valls)
    moisture = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            mx = c / cols * 2.5
            my = r / rows * 2.5
            m = (moist_noise(mx, my, 3, 0.6) + 1) / 2
            valley_boost = max(0.0, (0.45 - elev[r, c]) * 2.0)
            moisture[r, c] = np.clip(m * 0.6 + valley_boost * 0.4, 0, 1)

    # Rius: segueixen el camí de mínima elevació des de la vora
    def carve_river(sr, sc):
        r, c = sr, sc
        visited = set()
        for _ in range(rows + cols):
            key = (r, c)
            if key in visited:
                break
            visited.add(key)
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                nr, nc = r+dr, c+dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    moisture[nr, nc] = max(moisture[nr, nc], 0.85)
            moisture[r, c] = 1.0
            neighbors = [(r+dr, c+dc) for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]
                         if 0<=r+dr<rows and 0<=c+dc<cols]
            neighbors.sort(key=lambda x: elev[x[0], x[1]])
            if not neighbors or elev[neighbors[0][0], neighbors[0][1]] >= elev[r, c]:
                break
            r, c = neighbors[0]

    for _ in range(preset["river_count"]):
        edge = rng.integers(0, 4)
        if edge == 0:   sr, sc = 0,        rng.integers(0, cols)
        elif edge == 1: sr, sc = rows-1,   rng.integers(0, cols)
        elif edge == 2: sr, sc = rng.integers(0, rows), 0
        else:           sr, sc = rng.integers(0, rows), cols-1
        carve_river(int(sr), int(sc))

    # Llacs: zones circulars de màxima humitat en valls
    for _ in range(preset["lake_count"]):
        candidates = [(elev[r,c], r, c) for r in range(rows) for c in range(cols)]
        candidates.sort()
        lk_r, lk_c = candidates[rng.integers(0, min(20, len(candidates)))][1:]
        rad = rng.integers(2, 5)
        for r in range(rows):
            for c in range(cols):
                d = np.sqrt((r-lk_r)**2 + (c-lk_c)**2)
                if d < rad:
                    moisture[r, c] = 1.0
                elif d < rad + 3:
                    moisture[r, c] = max(moisture[r, c], (1-(d-rad)/3)*0.9)

    # Capa de vegetació a partir dels nivells d'elevació
    veg = np.zeros((rows, cols), dtype=int)
    for r in range(rows):
        for c in range(cols):
            e = elev[r, c]
            for thresh, lo, hi in preset["levels"]:
                if e < thresh:
                    if lo == 0 and hi == 0:
                        veg[r, c] = 0
                    else:
                        base = rng.integers(lo, hi+1)
                        boosted = round(base * (1 + moisture[r,c] * 0.3))
                        veg[r, c] = int(np.clip(boosted, lo, round(hi * 1.4)))
                    break

    # Capa d'humitat correlada amb vegetació i moisture
    hum = np.zeros((rows, cols), dtype=int)
    veg_max = preset["veg_max"]
    hum_max = preset["hum_max"]
    for r in range(rows):
        for c in range(cols):
            if veg[r, c] > 0:
                vf = min(veg[r,c] / veg_max, 1.0)
                raw = moisture[r,c] * 0.75 + vf * 0.25
                h = round(raw * hum_max) + int(rng.integers(0, 2)) - 0  
                hum[r, c] = int(np.clip(h, 0, hum_max))

    return veg, hum, seed


# ─── IDRISI32 PARSER ─────────────────────────────────────────────────────────
def load_idrisi(path, rows, cols):
    """Carrega un fitxer IDRISI32 (valors en text pla)."""
    with open(path, "r") as f:
        nums = [float(x) for x in f.read().split() if x.strip()]
    arr = np.array(nums[:rows*cols], dtype=float).reshape(rows, cols)
    return arr.astype(int)


# ─── CA MODEL ────────────────────────────────────────────────────────────────
class ForestFireCA:
    """
    Model m:n-CA^k per a la propagació d'incendis forestals.

    Capes:
      veg_layer  (L1): hores de combustió per cel·la
      hum_layer  (L2): hores de retard (humitat)
      fire_layer (L3): 0=pendent, 1=eixugant, 2=cremant, 3=cremat
    """

    UNBURNED  = 0
    DRYING    = 1
    BURNING   = 2
    BURNED    = 3

    def __init__(self, veg_layer, hum_layer, neighborhood="moore"):
        self.rows, self.cols = veg_layer.shape
        self.veg  = veg_layer.copy()
        self.hum  = hum_layer.copy()
        self.neighborhood = neighborhood
        self.reset()

    def reset(self):
        self.fire       = np.zeros((self.rows, self.cols), dtype=int)
        self.hum_cd     = self.hum.copy().astype(int)
        self.burn_cd    = np.zeros((self.rows, self.cols), dtype=int)
        self.step       = 0

    def ignite(self, r, c):
        """Inicia un focus d'ignició a la cel·la (r, c)."""
        if self.veg[r, c] == 0 or self.fire[r, c] != self.UNBURNED:
            return False
        if self.hum_cd[r, c] > 0:
            self.fire[r, c] = self.DRYING
        else:
            self.fire[r, c] = self.BURNING
            self.burn_cd[r, c] = self.veg[r, c]
        return True

    def _neighbors(self, r, c):
        dirs = (
            [(-1,0),(1,0),(0,-1),(0,1)]
            if self.neighborhood == "von_neumann"
            else [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
        )
        return [(r+dr, c+dc) for dr,dc in dirs
                if 0 <= r+dr < self.rows and 0 <= c+dc < self.cols]

    def advance(self):
        """Executa un pas de temps (una hora)."""
        new_fire  = self.fire.copy()
        new_hum   = self.hum_cd.copy()
        new_burn  = self.burn_cd.copy()

        for r in range(self.rows):
            for c in range(self.cols):
                if self.veg[r, c] == 0:
                    continue
                fs = self.fire[r, c]

                if fs == self.UNBURNED:
                    if any(self.fire[nr, nc] == self.BURNING
                           for nr, nc in self._neighbors(r, c)):
                        if self.hum_cd[r, c] > 0:
                            new_fire[r, c] = self.DRYING
                        else:
                            new_fire[r, c] = self.BURNING
                            new_burn[r, c] = self.veg[r, c]

                elif fs == self.DRYING:
                    new_hum[r, c] -= 1
                    if new_hum[r, c] <= 0:
                        new_hum[r, c] = 0
                        new_fire[r, c] = self.BURNING
                        new_burn[r, c] = self.veg[r, c]

                elif fs == self.BURNING:
                    new_burn[r, c] -= 1
                    if new_burn[r, c] <= 0:
                        new_fire[r, c] = self.BURNED
                        new_burn[r, c] = 0

        self.fire    = new_fire
        self.hum_cd  = new_hum
        self.burn_cd = new_burn
        self.step   += 1

    @property
    def is_active(self):
        return bool(np.any((self.fire == self.DRYING) | (self.fire == self.BURNING)))

    def stats(self):
        mask = self.veg > 0
        total    = int(mask.sum())
        unburned = int(((self.fire == self.UNBURNED) & mask).sum())
        drying   = int(((self.fire == self.DRYING)   & mask).sum())
        burning  = int(((self.fire == self.BURNING)  & mask).sum())
        burned   = int(((self.fire == self.BURNED)   & mask).sum())
        return dict(total=total, unburned=unburned, drying=drying,
                    burning=burning, burned=burned)


# ─── COLORMAPS ────────────────────────────────────────────────────────────────
def make_veg_cmap():
    colors_list = [
        (0.03, 0.03, 0.02),
        (0.10, 0.25, 0.05),
        (0.15, 0.40, 0.08),
        (0.20, 0.58, 0.12),
        (0.25, 0.78, 0.18),
    ]
    return mcolors.LinearSegmentedColormap.from_list("veg", colors_list, N=256)

def make_hum_cmap():
    colors_list = [
        (0.22, 0.16, 0.09),
        (0.35, 0.30, 0.15),
        (0.15, 0.45, 0.35),
        (0.10, 0.58, 0.54),
        (0.08, 0.60, 0.82),
    ]
    return mcolors.LinearSegmentedColormap.from_list("hum", colors_list, N=256)

def make_fire_cmap():
    colors_list = [
        (0.12, 0.38, 0.07),
        (0.18, 0.55, 0.75),
        (0.95, 0.48, 0.08),
        (0.15, 0.13, 0.11),
    ]
    return mcolors.ListedColormap(colors_list)


# ─── VISUALITZADOR ────────────────────────────────────────────────────────────
class SimulatorGUI:
    def __init__(self, ca: ForestFireCA, terrain_label="Alpí", seed=None):
        self.ca = ca
        self.terrain_label = terrain_label
        self.seed = seed
        self.running = False
        self.layer = "fire"
        self._anim = None
        self._setup_figure()

    def _setup_figure(self):
        matplotlib.rcParams.update({
            'figure.facecolor': '#0e0e0c',
            'axes.facecolor':   '#0e0e0c',
            'text.color':       '#e8e6df',
            'axes.labelcolor':  '#7a7870',
            'xtick.color':      '#4a4942',
            'ytick.color':      '#4a4942',
            'axes.edgecolor':   '#2a2924',
            'font.family':      'monospace',
        })

        self.fig = plt.figure(figsize=(14, 8), facecolor='#0e0e0c')
        self.fig.canvas.manager.set_window_title("Simulador d'Incendi Forestal — CA Model")

        gs = self.fig.add_gridspec(
            6, 3,
            left=0.03, right=0.97, top=0.93, bottom=0.10,
            wspace=0.25, hspace=0.6,
            width_ratios=[2.8, 0.01, 1]
        )

        self.ax_grid  = self.fig.add_subplot(gs[:, 0])
        self.ax_stats = self.fig.add_subplot(gs[0:3, 2])
        self.ax_veg   = self.fig.add_subplot(gs[3, 2])
        self.ax_hum   = self.fig.add_subplot(gs[4, 2])
        self.ax_info  = self.fig.add_subplot(gs[5, 2])

        for ax in [self.ax_stats, self.ax_veg, self.ax_hum, self.ax_info]:
            ax.set_facecolor('#141411')
            for spine in ax.spines.values():
                spine.set_edgecolor('#2a2924')

        self.ax_grid.set_facecolor('#080806')
        for spine in self.ax_grid.spines.values():
            spine.set_edgecolor('#333228')

        self.cmap_fire = make_fire_cmap()
        self.cmap_veg  = make_veg_cmap()
        self.cmap_hum  = make_hum_cmap()

        self.im = self.ax_grid.imshow(
            self._get_display_data(),
            cmap=self.cmap_fire,
            vmin=0, vmax=3,
            interpolation='nearest',
            aspect='auto'
        )
        self.ax_grid.set_title(
            f"Propagació de l'incendi  —  Terreny: {self.terrain_label}  (seed: {self.seed})",
            color='#e8e6df', fontsize=9, pad=6
        )
        self.ax_grid.tick_params(labelsize=7)

        patches = [
            mpatches.Patch(color='#1f6112', label='Vegetació intacta (L1)'),
            mpatches.Patch(color='#2e8cbf', label='Eixugant humitat (L2→L3)'),
            mpatches.Patch(color='#f07820', label='En flames (L3=2)'),
            mpatches.Patch(color='#261e1c', label='Cremat (L3=3)'),
        ]
        self.ax_grid.legend(handles=patches, loc='lower right',
                            fontsize=7, facecolor='#1a1a16', edgecolor='#333228',
                            labelcolor='#c8c6bf', framealpha=0.9)

        self._init_stats_panel()
        self._init_mini_maps()
        self._init_info_panel()

        self.fig.text(0.755, 0.915, "Estadístiques en temps real",
                      color='#7a7870', fontsize=7.5, fontweight='bold')
        self.fig.text(0.755, 0.595, "L1 — Vegetació",
                      color='#7a7870', fontsize=7, fontweight='bold')
        self.fig.text(0.755, 0.435, "L2 — Humitat",
                      color='#7a7870', fontsize=7, fontweight='bold')

        self._add_buttons()

        self.fig.suptitle(
            "Model m:n-CA\u1d4f  ·  Incendi Forestal  ·  "
            "Clica la graella per iniciar un focus d'ignició",
            color='#e8e6df', fontsize=10, y=0.98
        )

        self.step_text = self.fig.text(
            0.03, 0.96, "Pas: 0  |  Hora: 0h",
            color='#f07820', fontsize=9, fontfamily='monospace'
        )

        self.fig.canvas.mpl_connect('button_press_event', self._on_click)
        self._update_display()

    def _init_stats_panel(self):
        ax = self.ax_stats
        ax.set_xlim(0, 1); ax.set_ylim(-0.5, 3.5)
        ax.set_xticks([]); ax.set_yticks([])
        labels = ["Intactes", "Eixugant", "En flames", "Cremades"]
        colors = ['#2d7018', '#2e8cbf', '#f07820', '#4a4240']
        self._stat_bars = []
        self._stat_texts = []
        for i, (lbl, col) in enumerate(zip(labels, colors)):
            y = 3 - i
            ax.barh(y, 1.0, height=0.55, color='#222219', left=0)
            bar = ax.barh(y, 0.0, height=0.55, color=col, left=0)
            self._stat_bars.append(bar)
            ax.text(0.02, y, lbl, va='center', ha='left', fontsize=7.5, color='#c8c6bf')
            pct = ax.text(0.98, y, "0%", va='center', ha='right',
                          fontsize=7.5, color=col, fontfamily='monospace')
            self._stat_texts.append(pct)

    def _init_mini_maps(self):
        self.im_veg = self.ax_veg.imshow(
            self.ca.veg, cmap=self.cmap_veg,
            vmin=0, vmax=20, interpolation='nearest', aspect='auto'
        )
        self.ax_veg.set_xticks([]); self.ax_veg.set_yticks([])

        self.im_hum = self.ax_hum.imshow(
            self.ca.hum, cmap=self.cmap_hum,
            vmin=0, vmax=9, interpolation='nearest', aspect='auto'
        )
        self.ax_hum.set_xticks([]); self.ax_hum.set_yticks([])

    def _init_info_panel(self):
        ax = self.ax_info
        ax.set_xticks([]); ax.set_yticks([])
        self._info_text = ax.text(
            0.05, 0.5, "Clica la graella\nper veure detalls",
            va='center', ha='left', fontsize=7,
            color='#7a7870', transform=ax.transAxes
        )

    def _get_display_data(self):
        data = self.ca.fire.copy().astype(float)
        data[self.ca.veg == 0] = -1
        return data

    def _update_display(self):
        if self.layer == 'veg':
            self.im.set_data(self.ca.veg)
            self.im.set_cmap(self.cmap_veg); self.im.set_clim(0, 20)
        elif self.layer == 'hum':
            self.im.set_data(self.ca.hum)
            self.im.set_cmap(self.cmap_hum); self.im.set_clim(0, 9)
        else:
            self.im.set_data(self._get_display_data())
            self.im.set_cmap(self.cmap_fire); self.im.set_clim(0, 3)

        s = self.ca.stats()
        tot = s['total'] or 1
        vals = [s['unburned'], s['drying'], s['burning'], s['burned']]
        for i, (bar, v) in enumerate(zip(self._stat_bars, vals)):
            pct = v / tot
            bar[0].set_width(pct)
            self._stat_texts[i].set_text(f"{v} ({pct*100:.0f}%)")

        self.step_text.set_text(f"Pas: {self.ca.step}  |  Hora: {self.ca.step}h")
        self.fig.canvas.draw_idle()

    def _on_click(self, event):
        if event.inaxes != self.ax_grid:
            return
        c = int(round(event.xdata)) if event.xdata is not None else -1
        r = int(round(event.ydata)) if event.ydata is not None else -1
        if 0 <= r < self.ca.rows and 0 <= c < self.ca.cols:
            ok = self.ca.ignite(r, c)
            veg = self.ca.veg[r, c]
            hum = self.ca.hum[r, c]
            if ok:
                print(f"[Ignició] ({r},{c})  veg={veg}h  humitat={hum}h")
            else:
                tname = ["pendent","eixugant","cremant","cremat"][self.ca.fire[r,c]] if veg>0 else "sense vegetació"
                print(f"[Info] ({r},{c})  estat={tname}  veg={veg}h  humitat={hum}h")
            fs_names = ["Pendent","Eixugant","Cremant","Cremat"]
            veg_type = ("—" if veg==0 else "Prat" if veg<=3 else
                        "Arbust" if veg<=7 else "Bosc clar" if veg<=12 else "Bosc dens")
            self._info_text.set_text(
                f"Cel·la ({r}, {c})\n"
                f"Estat: {fs_names[self.ca.fire[r,c]] if veg>0 else 'Buit'}\n"
                f"Vegetació: {veg}h ({veg_type})\n"
                f"Humitat: {hum}h\n"
                f"Hum restant: {self.ca.hum_cd[r,c]}h\n"
                f"Combustió: {self.ca.burn_cd[r,c]}h"
            )
            self._info_text.set_color('#c8c6bf')
            self._update_display()

    def _add_buttons(self):
        btn_style = dict(color='#1a1a16', hovercolor='#2a2924')
        txt_col   = '#e8e6df'

        ax_start = self.fig.add_axes([0.03, 0.03, 0.10, 0.045])
        ax_pause = self.fig.add_axes([0.14, 0.03, 0.10, 0.045])
        ax_step  = self.fig.add_axes([0.25, 0.03, 0.10, 0.045])
        ax_reset = self.fig.add_axes([0.36, 0.03, 0.10, 0.045])
        ax_lfire = self.fig.add_axes([0.50, 0.03, 0.12, 0.045])
        ax_lveg  = self.fig.add_axes([0.63, 0.03, 0.12, 0.045])
        ax_lhum  = self.fig.add_axes([0.76, 0.03, 0.12, 0.045])

        self.btn_start = Button(ax_start, '▶  Iniciar',     **btn_style)
        self.btn_pause = Button(ax_pause, '⏸  Pausa',      **btn_style)
        self.btn_step  = Button(ax_step,  '⏭  Pas',        **btn_style)
        self.btn_reset = Button(ax_reset, '↺  Reset',      **btn_style)
        self.btn_lfire = Button(ax_lfire, '🔥 Propagació', **btn_style)
        self.btn_lveg  = Button(ax_lveg,  '🌿 Vegetació',  **btn_style)
        self.btn_lhum  = Button(ax_lhum,  '💧 Humitat',    **btn_style)

        for btn in [self.btn_start, self.btn_pause, self.btn_step, self.btn_reset,
                    self.btn_lfire, self.btn_lveg, self.btn_lhum]:
            btn.label.set_color(txt_col)
            btn.label.set_fontsize(8)

        self.btn_start.on_clicked(lambda e: self._start())
        self.btn_pause.on_clicked(lambda e: self._pause())
        self.btn_step.on_clicked( lambda e: self._step())
        self.btn_reset.on_clicked(lambda e: self._reset())
        self.btn_lfire.on_clicked(lambda e: self._set_layer('fire'))
        self.btn_lveg.on_clicked( lambda e: self._set_layer('veg'))
        self.btn_lhum.on_clicked( lambda e: self._set_layer('hum'))

    def _start(self):
        if not self.running:
            self.running = True
            self._anim = FuncAnimation(
                self.fig, self._anim_step, interval=350, cache_frame_data=False
            )
            plt.draw()
            print("[Simulació] Iniciada")

    def _pause(self):
        if self.running and self._anim:
            self._anim.event_source.stop()
            self.running = False
            print(f"[Simulació] Pausada al pas {self.ca.step}")

    def _step(self):
        if self.running:
            self._anim.event_source.stop()
            self.running = False
        self.ca.advance()
        self._update_display()
        if not self.ca.is_active and self.ca.step > 0:
            s = self.ca.stats()
            print(f"[Simulació] Incendi extingit al pas {self.ca.step}. "
                  f"Àrea cremada: {s['burned']}/{s['total']} "
                  f"({s['burned']/max(s['total'],1)*100:.1f}%)")

    def _reset(self):
        if self.running and self._anim:
            self._anim.event_source.stop()
        self.running = False
        self.ca.reset()
        self._info_text.set_text("Clica la graella\nper veure detalls")
        self._info_text.set_color('#7a7870')
        self._update_display()
        print("[Simulació] Reset")

    def _set_layer(self, layer):
        self.layer = layer
        labels = {'fire': 'Propagació (L3)', 'veg': 'Vegetació (L1)', 'hum': 'Humitat (L2)'}
        self.ax_grid.set_title(
            f"{labels[layer]}  —  Terreny: {self.terrain_label}  (seed: {self.seed})",
            color='#e8e6df', fontsize=9, pad=6
        )
        self._update_display()

    def _anim_step(self, frame):
        if self.ca.is_active:
            self.ca.advance()
            self._update_display()
        else:
            if self._anim:
                self._anim.event_source.stop()
            self.running = False
            s = self.ca.stats()
            print(f"[Simulació] Incendi extingit al pas {self.ca.step}. "
                  f"Àrea cremada: {s['burned']}/{s['total']} "
                  f"({s['burned']/max(s['total'],1)*100:.1f}%)")

    def show(self):
        plt.show()


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Simulador d'incendi forestal — Model m:n-CA^k",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("--veg",     help="Fitxer IDRISI32 de vegetació (.rst/.txt)")
    parser.add_argument("--hum",     help="Fitxer IDRISI32 d'humitat (.rst/.txt)")
    parser.add_argument("--terrain", default="alpine",
                        choices=list(PRESETS.keys()),
                        help="Tipus de terreny procedural (default: alpine)")
    parser.add_argument("--rows",    type=int, default=100,  help="Files de la graella")
    parser.add_argument("--cols",    type=int, default=100,  help="Columnes de la graella")
    parser.add_argument("--seed",    type=int, default=None, help="Seed per a la generació")
    parser.add_argument("--neighborhood", default="moore",
                        choices=["moore","von_neumann"],
                        help="Tipus de veïnatge (default: moore)")
    args = parser.parse_args()

    rows, cols = args.rows, args.cols
    seed = args.seed

    if args.veg and args.hum:
        if not os.path.exists(args.veg):
            print(f"Error: fitxer no trobat: {args.veg}"); sys.exit(1)
        if not os.path.exists(args.hum):
            print(f"Error: fitxer no trobat: {args.hum}"); sys.exit(1)
        veg = load_idrisi(args.veg, rows, cols)
        hum = load_idrisi(args.hum, rows, cols)
        label = "Fitxer IDRISI32"
        print(f"[Dades] Carregat des de fitxers: {args.veg}, {args.hum}")
    else:
        veg, hum, seed = generate_terrain(rows, cols, args.terrain, seed)
        label = PRESETS[args.terrain]["label"]
        print(f"[Dades] Terreny procedural '{label}' generat (seed={seed})")

    print(f"[Model] Graella {rows}×{cols}  |  Veïnatge: {args.neighborhood}")
    print(f"[Info]  Vegetació: {veg.min()}–{veg.max()}h  |  Humitat: {hum.min()}–{hum.max()}h")
    print("[Instruccions] Clica qualsevol cel·la de la graella per iniciar un focus d'ignició.")
    print("               Usa els botons per controlar la simulació.\n")

    ca  = ForestFireCA(veg, hum, neighborhood=args.neighborhood)
    gui = SimulatorGUI(ca, terrain_label=label, seed=seed)
    gui.show()


if __name__ == "__main__":
    main()