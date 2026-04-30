"""
Simulador d'Incendi Forestal — Model m:n-CA^k
==============================================
Capes:
  L1 – Vegetació  : hores que triga a cremar-se una cel·la
  L2 – Humitat    : hores de retard fins que el foc s'inicia
  L3 – Propagació : 0=pendent | 1=eixugant | 2=cremant | 3=cremat
  L4 – Vent (opt) : vector direccional IDRISI31 (.vec/.dvc) — part opcional

Ús:
  python incendi_forestal.py
  python incendi_forestal.py --terrain mediterranean
  python incendi_forestal.py --veg veg.rst --hum hum.rst
  python incendi_forestal.py --veg veg.rst --hum hum.rst --wind vent.vec
  python incendi_forestal.py --wind-dir 45 --wind-strength 0.7
  python incendi_forestal.py --help
"""

import argparse
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
from matplotlib.widgets import Button
from matplotlib.animation import FuncAnimation
import sys, os, math

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
        aa = P[P[xi] + yi];     ab = P[P[xi] + yi + 1]
        ba = P[P[xi+1] + yi];   bb = P[P[xi+1] + yi + 1]
        return lerp(v,
                    lerp(u, grad(aa, xf, yf),   grad(ba, xf-1, yf)),
                    lerp(u, grad(ab, xf, yf-1), grad(bb, xf-1, yf-1)))

    def octave_noise(x, y, octs=4, persist=0.55):
        val = 0.0; mx = 0.0; amp = 1.0; freq = 1.0
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
            (0.15, 0,  0), (0.35, 1,  2), (0.60, 3,  6),
            (0.80, 6,  9), (1.00, 7, 11),
        ]
    ),
    "alpine": dict(
        label="Alpí", veg_max=20, hum_max=9, scale=2.5,
        river_count=2, lake_count=1,
        levels=[
            (0.08, 0,  0), (0.20, 1,  3), (0.45, 4,  8),
            (0.72, 9, 14), (1.00, 13, 20),
        ]
    ),
    "savanna": dict(
        label="Sabana", veg_max=8, hum_max=5, scale=4.0,
        river_count=1, lake_count=0,
        levels=[
            (0.20, 0, 0), (0.50, 1, 3), (0.72, 2, 5),
            (0.88, 4, 7), (1.00, 5, 8),
        ]
    ),
    "coastal": dict(
        label="Costaner", veg_max=14, hum_max=6, scale=3.0,
        river_count=1, lake_count=1,
        levels=[
            (0.12, 0,  0), (0.28, 1,  2), (0.50, 2,  5),
            (0.72, 5,  9), (1.00, 8, 14),
        ]
    ),
}


# ─── GENERADOR DE TERRENY ────────────────────────────────────────────────────
def generate_terrain(rows, cols, terrain="alpine", seed=None):
    """Genera capes de vegetació i humitat amb patrons geogràfics realistes."""
    if seed is None:
        seed = int(np.random.randint(1, 99999))
    preset = PRESETS[terrain]
    rng = np.random.default_rng(seed)
    noise = make_noise(seed)
    moist_noise = make_noise(seed + 7919)

    elev = np.zeros((rows, cols))
    scale = preset["scale"]
    for r in range(rows):
        for c in range(cols):
            nx = c / cols * scale
            ny = r / rows * scale
            e = noise(nx, ny, 4, 0.55)
            elev[r, c] = (e + 1) / 2

    moisture = np.zeros((rows, cols))
    for r in range(rows):
        for c in range(cols):
            mx = c / cols * 2.5
            my = r / rows * 2.5
            m = (moist_noise(mx, my, 3, 0.6) + 1) / 2
            valley_boost = max(0.0, (0.45 - elev[r, c]) * 2.0)
            moisture[r, c] = np.clip(m * 0.6 + valley_boost * 0.4, 0, 1)

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
        if   edge == 0: sr, sc = 0,        rng.integers(0, cols)
        elif edge == 1: sr, sc = rows-1,   rng.integers(0, cols)
        elif edge == 2: sr, sc = rng.integers(0, rows), 0
        else:           sr, sc = rng.integers(0, rows), cols-1
        carve_river(int(sr), int(sc))

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

    hum = np.zeros((rows, cols), dtype=int)
    veg_max = preset["veg_max"]
    hum_max = preset["hum_max"]
    for r in range(rows):
        for c in range(cols):
            if veg[r, c] > 0:
                vf = min(veg[r,c] / veg_max, 1.0)
                raw = moisture[r,c] * 0.75 + vf * 0.25
                h = round(raw * hum_max) + int(rng.integers(0, 2))
                hum[r, c] = int(np.clip(h, 0, hum_max))

    return veg, hum, seed


# ─── IDRISI32 RASTER PARSER ───────────────────────────────────────────────────
def load_idrisi_header(rdc_path):
    """Llegeix el fitxer de capçalera IDRISI32 (.rdc)."""
    meta = {}
    with open(rdc_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if ":" not in line:
                continue
            key, _, val = line.partition(":")
            key = key.strip().lower().replace(" ", "_").replace(".", "_")
            val = val.strip()
            meta[key] = val

    def get(keys, cast=str, default=None):
        for k in keys:
            if k in meta:
                try:
                    return cast(meta[k])
                except (ValueError, TypeError):
                    return default
        return default

    return {
        "rows":       get(["rows", "nrows", "lines"],               cast=int,   default=None),
        "cols":       get(["columns", "cols", "ncols", "samples"],  cast=int,   default=None),
        "data_type":  get(["data_type", "datatype"],                cast=str,   default="integer").lower(),
        "file_type":  get(["file_type", "filetype"],                cast=str,   default="ascii").lower(),
        "min_value":  get(["min__value", "min_value", "minval"],    cast=float, default=None),
        "max_value":  get(["max__value", "max_value", "maxval"],    cast=float, default=None),
        "title":      get(["file_title", "title"],                  cast=str,   default=""),
        "ref_system": get(["ref__system", "ref_system"],            cast=str,   default="plane"),
    }


def load_idrisi(rst_path, rows=None, cols=None):
    """
    Carrega un fitxer raster IDRISI32 (.rst), llegint la capçalera (.rdc)
    automàticament si existeix. Suporta ASCII i binari (byte/integer/real).
    Retorna (array 2D d'enters, dict de metadades).
    """
    base = os.path.splitext(rst_path)[0]
    rdc_path = base + ".rdc"
    if not os.path.exists(rdc_path):
        rdc_path = base + ".RDC"

    meta = {}
    if os.path.exists(rdc_path):
        meta = load_idrisi_header(rdc_path)
        print(f"[IDRISI32] Capçalera llegida: {rdc_path}")
        if meta.get("title"):
            print(f"           Títol : {meta['title']}")
        if meta.get("rows"):
            print(f"           Mida  : {meta['rows']} files × {meta['cols']} columnes")
        if meta.get("min_value") is not None:
            print(f"           Rang  : {meta['min_value']} – {meta['max_value']}")
    else:
        print(f"[IDRISI32] Sense .rdc per a '{rst_path}'. S'usaran --rows/--cols.")

    r = meta.get("rows") or rows
    c = meta.get("cols") or cols
    if r is None or c is None:
        raise ValueError(
            f"No s'han pogut determinar les dimensions de '{rst_path}'.\n"
            "Proporciona --rows i --cols, o assegura't que existeix el fitxer .rdc."
        )
    rows, cols = int(r), int(c)

    file_type = meta.get("file_type", "ascii")
    data_type = meta.get("data_type", "integer")

    if "binary" in file_type or "bin" in file_type:
        dtype_map = {"byte": np.uint8, "integer": np.int16,
                     "real": np.float32, "rgb24": np.uint8}
        dtype = dtype_map.get(data_type, np.int16)
        with open(rst_path, "rb") as f:
            raw = f.read()
        expected = rows * cols * np.dtype(dtype).itemsize
        if len(raw) < expected:
            raise ValueError(
                f"Fitxer binari massa curt: {len(raw)} bytes, s'esperaven {expected}.")
        arr = np.frombuffer(raw[:expected], dtype=dtype).reshape(rows, cols)
    else:
        with open(rst_path, "r", encoding="utf-8", errors="ignore") as f:
            nums = [float(x) for x in f.read().split() if x.strip()]
        if len(nums) < rows * cols:
            raise ValueError(
                f"Fitxer ASCII amb {len(nums)} valors, s'esperaven {rows*cols}.")
        arr = np.array(nums[:rows * cols], dtype=float).reshape(rows, cols)

    return arr.astype(int), meta


# ─── IDRISI31 VECTOR PARSER (part opcional: vent) ────────────────────────────
def load_idrisi_vec(vec_path):
    """
    Llegeix un fitxer vectorial IDRISI31 (.vec) i retorna una llista d'objectes.
    Cada objecte és un dict amb:
      - 'id'     : identificador
      - 'points' : llista de tuples (x, y)
      - 'type'   : 'line' o 'polygon' (llegit del .dvc si existeix)

    Format .vec (text pla):
      <id> <num_punts>
      x1 y1
      x2 y2
      ...
      0 0          ← marca de final d'objecte

    El fitxer .dvc (capçalera) indica si és 'line' o 'polygon'.
    """
    base = os.path.splitext(vec_path)[0]
    dvc_path = base + ".dvc"
    if not os.path.exists(dvc_path):
        dvc_path = base + ".DVC"

    obj_type = "line"
    if os.path.exists(dvc_path):
        with open(dvc_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if "object" in line.lower() and "type" in line.lower():
                    obj_type = line.partition(":")[2].strip().lower()
                    break
        print(f"[IDRISI31] Capçalera llegida: {dvc_path}  →  tipus: {obj_type}")

    objects = []
    with open(vec_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [l.strip() for l in f if l.strip()]

    i = 0
    while i < len(lines):
        parts = lines[i].split()
        if len(parts) < 2:
            i += 1
            continue
        try:
            obj_id = int(parts[0])
            num_pts = int(parts[1])
        except ValueError:
            i += 1
            continue

        i += 1
        points = []
        while i < len(lines):
            coords = lines[i].split()
            if len(coords) >= 2:
                x, y = float(coords[0]), float(coords[1])
                if x == 0.0 and y == 0.0 and len(points) >= 2:
                    i += 1
                    break
                points.append((x, y))
            i += 1

        if len(points) >= 2:
            objects.append({"id": obj_id, "points": points, "type": obj_type})

    print(f"[IDRISI31] {vec_path}: {len(objects)} objecte(s) llegit(s).")
    return objects


def wind_vector_from_vec(vec_path):
    """
    Extreu el vector de vent (dx, dy) normalitzat a partir del primer
    objecte de tipus 'line' del fitxer .vec.

    Un 'line' de dos punts (x1,y1) → (x2,y2) defineix la direcció del vent.
    Retorna (dx, dy) normalitzat, o None si no es pot llegir.
    """
    try:
        objects = load_idrisi_vec(vec_path)
    except Exception as e:
        print(f"[Vent] Error llegint {vec_path}: {e}")
        return None

    for obj in objects:
        pts = obj["points"]
        if len(pts) >= 2:
            dx = pts[1][0] - pts[0][0]
            dy = pts[1][1] - pts[0][1]
            norm = math.sqrt(dx*dx + dy*dy)
            if norm > 0:
                dx, dy = dx / norm, dy / norm
                ang = math.degrees(math.atan2(dy, dx))
                print(f"[Vent] Direcció extreta del .vec: ({dx:.3f}, {dy:.3f})  "
                      f"→  {ang:.1f}°")
                return (dx, dy)

    print("[Vent] No s'ha trobat cap línia de direcció vàlida al fitxer .vec.")
    return None


def wind_vector_from_angle(degrees):
    """
    Converteix un angle en graus (convenció meteorològica: 0°=Nord, 90°=Est)
    a un vector unitari (dx, dy) en coordenades de graella (columna, fila).
    """
    rad = math.radians(degrees)
    dx =  math.sin(rad)   # component columna (→ Est)
    dy = -math.cos(rad)   # component fila    (↓ Sud, perquè les files creixen cap avall)
    return (dx, dy)


# ─── CA MODEL ────────────────────────────────────────────────────────────────
class ForestFireCA:
    """
    Model m:n-CA^k per a la propagació d'incendis forestals.

    Capes:
      veg_layer  (L1): hores de combustió per cel·la
      hum_layer  (L2): hores de retard (humitat)
      fire_layer (L3): 0=pendent, 1=eixugant, 2=cremant, 3=cremat
      wind       (L4): vector de vent (dx, dy) normalitzat — opcional

    Efecte del vent:
      - Les cel·les en la direcció del vent (sotavent) perden humitat
        fins a (1 + wind_strength) unitats per pas, accelerant l'encesa.
      - Les cel·les en contra del vent (sobrevent) perden humitat
        min(0, 1 - wind_strength) unitats, alentint o bloquejant l'encesa.
    """
    UNBURNED = 0
    DRYING   = 1
    BURNING  = 2
    BURNED   = 3

    def __init__(self, veg_layer, hum_layer,
                 neighborhood="moore",
                 wind_dir=None, wind_strength=0.6):
        self.rows, self.cols = veg_layer.shape
        self.veg  = veg_layer.copy()
        self.hum  = hum_layer.copy()
        self.neighborhood  = neighborhood
        self.wind_dir      = wind_dir        # (dx, dy) normalitzat o None
        self.wind_strength = wind_strength   # 0.0 (cap efecte) – 1.0 (molt fort)
        self.reset()

    def reset(self):
        self.fire    = np.zeros((self.rows, self.cols), dtype=int)
        self.hum_cd  = self.hum.copy().astype(int)
        self.burn_cd = np.zeros((self.rows, self.cols), dtype=int)
        self.step    = 0

    def ignite(self, r, c):
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

    def _wind_factor(self, from_r, from_c, to_r, to_c):
        """
        Retorna un factor [-1, 1] que indica quant afavoreix el vent
        la propagació de (from_r, from_c) cap a (to_r, to_c).
          +1 → completament sotavent (màxima acceleració)
          -1 → completament sobrevent (màxima resistència)
           0 → perpendicular (sense efecte)
        """
        if self.wind_dir is None:
            return 0.0
        dx = to_c - from_c
        dy = to_r - from_r
        norm = math.sqrt(dx*dx + dy*dy)
        if norm == 0:
            return 0.0
        dx /= norm; dy /= norm
        return dx * self.wind_dir[0] + dy * self.wind_dir[1]

    def advance(self):
        """Executa un pas de temps (una hora)."""
        new_fire = self.fire.copy()
        new_hum  = self.hum_cd.copy()
        new_burn = self.burn_cd.copy()

        for r in range(self.rows):
            for c in range(self.cols):
                if self.veg[r, c] == 0:
                    continue
                fs = self.fire[r, c]

                if fs == self.UNBURNED:
                    # Comprova si algun veí crema i quant afavoreix el vent
                    for nr, nc in self._neighbors(r, c):
                        if self.fire[nr, nc] == self.BURNING:
                            wf = self._wind_factor(nr, nc, r, c)
                            # wf > 0 → sotavent → s'encén més fàcilment
                            # wf < 0 → sobrevent → resisteix
                            wind_bias = wf * self.wind_strength
                            if wind_bias < -0.99:
                                # Vent totalment en contra: no es propaga
                                continue
                            if self.hum_cd[r, c] > 0:
                                new_fire[r, c] = self.DRYING
                            else:
                                new_fire[r, c] = self.BURNING
                                new_burn[r, c] = self.veg[r, c]
                            break

                elif fs == self.DRYING:
                    # Calcula quanta humitat s'evapora aquest pas
                    # (el vent accelera o frena l'assecament)
                    best_wf = 0.0
                    for nr, nc in self._neighbors(r, c):
                        if self.fire[nr, nc] == self.BURNING:
                            wf = self._wind_factor(nr, nc, r, c)
                            if wf > best_wf:
                                best_wf = wf

                    evap = max(1, round(1 + best_wf * self.wind_strength * 2))
                    new_hum[r, c] = max(0, self.hum_cd[r, c] - evap)
                    if new_hum[r, c] <= 0:
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
        mask     = self.veg > 0
        total    = int(mask.sum())
        unburned = int(((self.fire == self.UNBURNED) & mask).sum())
        drying   = int(((self.fire == self.DRYING)   & mask).sum())
        burning  = int(((self.fire == self.BURNING)  & mask).sum())
        burned   = int(((self.fire == self.BURNED)   & mask).sum())
        return dict(total=total, unburned=unburned, drying=drying,
                    burning=burning, burned=burned)


# ─── COLORMAPS ────────────────────────────────────────────────────────────────
def make_veg_cmap():
    return mcolors.LinearSegmentedColormap.from_list("veg", [
        (0.03, 0.03, 0.02), (0.10, 0.25, 0.05),
        (0.15, 0.40, 0.08), (0.20, 0.58, 0.12),
        (0.25, 0.78, 0.18),
    ], N=256)

def make_hum_cmap():
    return mcolors.LinearSegmentedColormap.from_list("hum", [
        (0.22, 0.16, 0.09), (0.35, 0.30, 0.15),
        (0.15, 0.45, 0.35), (0.10, 0.58, 0.54),
        (0.08, 0.60, 0.82),
    ], N=256)

def make_fire_cmap():
    return mcolors.ListedColormap([
        (0.12, 0.38, 0.07), (0.18, 0.55, 0.75),
        (0.95, 0.48, 0.08), (0.15, 0.13, 0.11),
    ])


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

    def _wind_arrow_label(self):
        if self.ca.wind_dir is None:
            return "Sense vent"
        dx, dy = self.ca.wind_dir
        ang = math.degrees(math.atan2(dy, dx))
        dirs = ["→E","↗NE","↑N","↖NO","←O","↙SO","↓S","↘SE"]
        idx = round(ang / 45) % 8
        return f"Vent {dirs[idx]}  (força {self.ca.wind_strength:.0%})"

    def _setup_figure(self):
        matplotlib.rcParams.update({
            'figure.facecolor': '#0e0e0c', 'axes.facecolor': '#0e0e0c',
            'text.color': '#e8e6df',       'axes.labelcolor': '#7a7870',
            'xtick.color': '#4a4942',      'ytick.color': '#4a4942',
            'axes.edgecolor': '#2a2924',   'font.family': 'monospace',
        })

        self.fig = plt.figure(figsize=(14, 8), facecolor='#0e0e0c')
        self.fig.canvas.manager.set_window_title("Simulador d'Incendi Forestal — CA Model")

        gs = self.fig.add_gridspec(
            6, 3, left=0.03, right=0.97, top=0.93, bottom=0.10,
            wspace=0.25, hspace=0.6, width_ratios=[2.8, 0.01, 1]
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
            self._get_display_data(), cmap=self.cmap_fire,
            vmin=0, vmax=3, interpolation='nearest', aspect='auto'
        )

        wind_label = self._wind_arrow_label()
        self.ax_grid.set_title(
            f"Propagació  —  {self.terrain_label}  |  {wind_label}",
            color='#e8e6df', fontsize=9, pad=6
        )
        self.ax_grid.tick_params(labelsize=7)

        # Fletxa de vent sobre la graella
        self._draw_wind_arrow()

        patches = [
            mpatches.Patch(color='#1f6112', label='Vegetació intacta (L1)'),
            mpatches.Patch(color='#2e8cbf', label='Eixugant humitat (L2→L3)'),
            mpatches.Patch(color='#f07820', label='En flames (L3=2)'),
            mpatches.Patch(color='#261e1c', label='Cremat (L3=3)'),
        ]
        self.ax_grid.legend(handles=patches, loc='lower right', fontsize=7,
                            facecolor='#1a1a16', edgecolor='#333228',
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

    def _draw_wind_arrow(self):
        """Dibuixa una fletxa gran sobre la graella indicant la direcció del vent."""
        if self.ca.wind_dir is None:
            return
        dx, dy = self.ca.wind_dir
        cx = self.ca.cols * 0.12
        cy = self.ca.rows * 0.12
        scale = min(self.ca.rows, self.ca.cols) * 0.10
        self.ax_grid.annotate(
            "", xy=(cx + dx*scale, cy + dy*scale), xytext=(cx, cy),
            arrowprops=dict(
                arrowstyle="-|>", color='#87ceeb',
                lw=2.5, mutation_scale=18,
            )
        )
        self.ax_grid.text(
            cx + dx*scale*1.5, cy + dy*scale*1.5,
            "vent", color='#87ceeb', fontsize=7, ha='center', va='center'
        )

    def _init_stats_panel(self):
        ax = self.ax_stats
        ax.set_xlim(0, 1); ax.set_ylim(-0.5, 3.5)
        ax.set_xticks([]); ax.set_yticks([])
        labels = ["Intactes", "Eixugant", "En flames", "Cremades"]
        colors = ['#2d7018', '#2e8cbf', '#f07820', '#4a4240']
        self._stat_bars  = []
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
                tname = (["pendent","eixugant","cremant","cremat"][self.ca.fire[r,c]]
                         if veg > 0 else "sense vegetació")
                print(f"[Info] ({r},{c})  estat={tname}  veg={veg}h  humitat={hum}h")
            fs_names  = ["Pendent","Eixugant","Cremant","Cremat"]
            veg_type  = ("—" if veg==0 else "Prat" if veg<=3 else
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

        self.btn_start = Button(ax_start, '▶  Iniciar',    **btn_style)
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
            f"{labels[layer]}  —  {self.terrain_label}  |  {self._wind_arrow_label()}",
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
    # Capes raster
    parser.add_argument("--veg",     help="Fitxer IDRISI32 de vegetació (.rst)")
    parser.add_argument("--hum",     help="Fitxer IDRISI32 d'humitat (.rst)")
    parser.add_argument("--terrain", default="alpine", choices=list(PRESETS.keys()))
    parser.add_argument("--rows",    type=int, default=None)
    parser.add_argument("--cols",    type=int, default=None)
    parser.add_argument("--seed",    type=int, default=None)
    parser.add_argument("--neighborhood", default="moore",
                        choices=["moore", "von_neumann"])
    # Capa de vent (opcional) — dues maneres d'especificar-la:
    parser.add_argument("--wind",
                        help="Fitxer vectorial IDRISI31 (.vec) amb la línia de direcció del vent")
    parser.add_argument("--wind-dir",    type=float, default=None,
                        help="Direcció del vent en graus (0=Nord, 90=Est, 180=Sud, 270=Oest)")
    parser.add_argument("--wind-strength", type=float, default=0.6,
                        help="Força del vent, 0.0–1.0 (default: 0.6)")
    args = parser.parse_args()

    seed = args.seed

    # ── Capes raster ──
    if args.veg and args.hum:
        for path in [args.veg, args.hum]:
            if not os.path.exists(path):
                print(f"Error: fitxer no trobat: {path}"); sys.exit(1)
        veg, meta_veg = load_idrisi(args.veg, rows=args.rows, cols=args.cols)
        rows, cols = veg.shape
        hum, _     = load_idrisi(args.hum, rows=rows, cols=cols)
        label = "Fitxer IDRISI32"
        print(f"[Dades] Carregat: {args.veg}  +  {args.hum}")
    else:
        rows = args.rows or 100
        cols = args.cols or 100
        veg, hum, seed = generate_terrain(rows, cols, args.terrain, seed)
        label = PRESETS[args.terrain]["label"]
        print(f"[Dades] Terreny procedural '{label}' generat (seed={seed})")

    # ── Capa de vent (opcional) ──
    wind_dir = None
    if args.wind:
        if not os.path.exists(args.wind):
            print(f"[Vent] Fitxer no trobat: {args.wind}")
        else:
            wind_dir = wind_vector_from_vec(args.wind)
    elif args.wind_dir is not None:
        wind_dir = wind_vector_from_angle(args.wind_dir)
        print(f"[Vent] Direcció manual: {args.wind_dir}°  "
              f"→  vector ({wind_dir[0]:.3f}, {wind_dir[1]:.3f})")

    if wind_dir is not None:
        print(f"[Vent] Força: {args.wind_strength:.0%}")
    else:
        print("[Vent] Sense vent (usa --wind o --wind-dir per activar-lo)")

    print(f"[Model] Graella {rows}×{cols}  |  Veïnatge: {args.neighborhood}")
    print(f"[Info]  Vegetació: {veg.min()}–{veg.max()}h  |  Humitat: {hum.min()}–{hum.max()}h")
    print("[Instruccions] Clica qualsevol cel·la per iniciar un focus d'ignició.\n")

    ca = ForestFireCA(veg, hum, neighborhood=args.neighborhood,
                    wind_dir=wind_vector_from_angle(45),
                    wind_strength=0.7)
    gui = SimulatorGUI(ca, terrain_label=label, seed=seed)
    gui.show()


if __name__ == "__main__":
    main()