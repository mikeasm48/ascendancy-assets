# building_meshes.py — общие процедурные помощники для зданий (pure numpy).
# Надстройка над device_meshes.py: земля — плоскость z=0, здания растут в +Z.
# Используется рецептами building_recipes_humans_*.py и превью/Blender-глю.
import numpy as np
import math

from device_meshes import (revolve, sphere, cyl, box, torus, tube, helix_coil,
                           arc_pipe, dome, ngon_prism, tf, merge, _quad_grid)

PI = math.pi


def combine(vfs):
    """Слить список (V,F) в один (V,F) без тегов."""
    Vs, Fs, off = [], [], 0
    for V, F in vfs:
        Vs.append(np.asarray(V, float))
        Fs.append(np.asarray(F, int) + off)
        off += len(V)
    return np.vstack(Vs), np.vstack(Fs)


def frustum(sx0, sy0, sx1, sy1, h, z0=0.0):
    """Усечённый параллелепипед: низ (sx0,sy0) на z0, верх (sx1,sy1) на z0+h."""
    x0, y0, x1, y1 = sx0 / 2, sy0 / 2, sx1 / 2, sy1 / 2
    V = np.array([[-x0, -y0, z0], [x0, -y0, z0], [x0, y0, z0], [-x0, y0, z0],
                  [-x1, -y1, z0 + h], [x1, -y1, z0 + h],
                  [x1, y1, z0 + h], [-x1, y1, z0 + h]], float)
    F = np.array([(0, 2, 1), (0, 3, 2), (4, 5, 6), (4, 6, 7),
                  (0, 1, 5), (0, 5, 4), (1, 2, 6), (1, 6, 5),
                  (2, 3, 7), (2, 7, 6), (3, 0, 4), (3, 4, 7)])
    return V, F


def loft_z(sections):
    """Вертикальный лофт: sections = [(z, [(x,y),...]), ...] снизу вверх,
    у всех секций одинаковое число точек (выпуклый контур), крышки с торцов."""
    n = len(sections[0][1])
    V, F = [], []
    for z, pts in sections:
        V += [(x, y, z) for x, y in pts]
    for i in range(len(sections) - 1):
        for j in range(n):
            a1 = i * n + j; b1 = i * n + (j + 1) % n
            a2 = (i + 1) * n + j; b2 = (i + 1) * n + (j + 1) % n
            F += [(a1, b2, a2), (a1, b1, b2)]
    c0 = len(V)
    V.append((sum(x for x, _ in sections[0][1]) / n,
              sum(y for _, y in sections[0][1]) / n, sections[0][0]))
    for j in range(n):
        F.append((j, (j + 1) % n, c0))
    c1 = len(V)
    V.append((sum(x for x, _ in sections[-1][1]) / n,
              sum(y for _, y in sections[-1][1]) / n, sections[-1][0]))
    off = (len(sections) - 1) * n
    for j in range(n):
        F.append((off + (j + 1) % n, off + j, c1))
    return np.array(V, float), np.array(F, int)


def hbarrel(w, l, h, seg=12):
    """Полуцилиндрический свод-теплица: ширина w (X), длина l (Y), высота h,
    основание на z=0, закрытые торцы и дно."""
    ts = np.linspace(0, PI, seg + 1)
    prof = [(w / 2 * math.cos(t), h * math.sin(t)) for t in ts]
    secs = [(-l / 2, prof), (l / 2, prof)]
    V, F = [], []
    n = len(prof)
    for y, pts in secs:
        V += [(x, y, z) for x, z in pts]
    for j in range(n - 1):
        F += [(j, j + 1, n + j + 1), (j, n + j + 1, n + j)]
    # дно
    F += [(0, n - 1, 2 * n - 1), (0, 2 * n - 1, n)]
    # торцы-веера
    c0 = len(V); V.append((0, -l / 2, 0))
    for j in range(n - 1):
        F.append((j + 1, j, c0))
    c1 = len(V); V.append((0, l / 2, 0))
    for j in range(n - 1):
        F.append((n + j, n + j + 1, c1))
    return np.array(V, float), np.array(F, int)


def cooling_tower(r_base, r_waist, r_top, h, seg=22):
    """Гиперболоидная градирня, основание на z=0."""
    zs = np.linspace(0, 1, 9)
    prof = []
    for t in zs[::-1]:
        # квадратичная интерполяция: талия на 70% высоты
        if t < 0.7:
            r = r_base + (r_waist - r_base) * (t / 0.7) ** 1.6
        else:
            r = r_waist + (r_top - r_waist) * ((t - 0.7) / 0.3) ** 1.2
        prof.append((r, t * h))
    prof.append((max(r_base * 0.98, 1e-4), 0.0))
    return revolve(prof, seg)


def lattice_mast(w0, w1, h, bays=4, r=0.018, z0=0.0):
    """Решётчатая мачта: 4 сужающиеся ноги + пояса + диагонали (трубки)."""
    parts = []
    zs = np.linspace(z0, z0 + h, bays + 1)
    ws = np.linspace(w0 / 2, w1 / 2, bays + 1)
    corners = [(1, 1), (1, -1), (-1, -1), (-1, 1)]
    for cx, cy in corners:
        path = np.array([(cx * w, cy * w, z) for w, z in zip(ws, zs)])
        parts.append(tube(path, r, 6))
    for k in range(bays + 1):
        w, z = ws[k], zs[k]
        ring = [(cx * w, cy * w, z) for cx, cy in corners] + [(w, w, z)]
        parts.append(tube(np.array(ring), r * 0.8, 5))
    for k in range(bays):
        wa, za, wb, zb = ws[k], zs[k], ws[k + 1], zs[k + 1]
        for (ax, ay), (bx, by) in zip(corners, corners[1:] + corners[:1]):
            parts.append(tube(np.array([(ax * wa, ay * wa, za),
                                        (bx * wb, by * wb, zb)]), r * 0.7, 5))
    return combine(parts)


def dish_mesh(r, depth=0.22, seg=24):
    """Параболическая тарелка, ось +Z, вершина в origin."""
    ts = np.linspace(0.06, 1.0, 6)
    prof = [(r * t, depth * r * t * t) for t in ts[::-1]]
    prof += [(r * t * 0.97, depth * r * t * t + 0.03 * r) for t in ts]
    return revolve(prof, seg)


def geodome(r, seg=18, rings=7):
    """Геокупол: (стеклянная сфера-купол, каркас из трубок)."""
    glass = dome(r, seg, rings)
    parts = []
    for k, rr in enumerate(np.linspace(0.98, 0.35, 4)):
        z = r * math.sqrt(max(1 - rr * rr, 0))
        parts.append(tf(torus(rr * r, 0.012 * r + 0.006, 24, 5), t=(0, 0, z)))
    for a in np.linspace(0, 2 * PI, 8, endpoint=False):
        path = [(r * math.cos(t) * math.cos(a), r * math.cos(t) * math.sin(a),
                 r * math.sin(t)) for t in np.linspace(0.04, PI / 2, 9)]
        parts.append(tube(np.array(path), 0.012 * r + 0.006, 5))
    return glass, combine(parts)


def chimney(r, h, z0=0.0, seg=14):
    """Труба с воротником и утолщённым низом: (ствол, воротник-кольца)."""
    body = revolve([(0.72 * r, z0 + h), (0.8 * r, z0 + 0.7 * h),
                    (r, z0 + 0.25 * h), (1.15 * r, z0)], seg)
    collars = combine([tf(torus(0.78 * r, 0.05 * r, seg, 6), t=(0, 0, z0 + h * f))
                       for f in (0.82, 0.92)])
    return body, collars


def ring_instances(vf, R, n, z=0.0, rz_extra=0.0, phase=0.0):
    """n копий (V,F) по окружности радиуса R, повёрнутых лицом от центра."""
    out = []
    for a in np.linspace(phase, phase + 2 * PI, n, endpoint=False):
        out.append(tf(vf, t=(R * math.cos(a), R * math.sin(a), z),
                      rz=a + rz_extra))
    return out


def box_ring(R, n, sx, sy, sz, z=0.0, phase=0.0):
    """Кольцо из n боксов-сегментов станции: sx — радиальная толщина,
    sy — длина по касательной."""
    return ring_instances(box(sx, sy, sz), R, n, z=z, phase=phase)


def scatter_boxes(seed, n, spread, smin, smax, hmax=None):
    """Хаотичные контейнеры: список (V,F,центр) без тегов."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        sx, sy, sz = rng.uniform(smin, smax, 3)
        if hmax:
            sz = min(sz, hmax)
        x, y = rng.uniform(-spread, spread, 2)
        a = rng.uniform(0, PI)
        out.append(tf(box(sx, sy, sz), t=(x, y, sz / 2), rz=a))
    return out


def octahedron(r, squash=1.0):
    """Октаэдр (алмаз): вершины на осях, вертикаль растянута squash."""
    V = np.array([[r, 0, 0], [-r, 0, 0], [0, r, 0], [0, -r, 0],
                  [0, 0, r * squash], [0, 0, -r * squash]], float)
    F = np.array([(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4),
                  (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)])
    return V, F


def bridge_tube(p0, p1, r=0.05, flat=0.5):
    """Крытый переход между корпусами: сплюснутая труба."""
    V, F = tube(np.array([p0, p1]), r, 8)
    V = V.copy()
    V[:, 2] = (V[:, 2] - (p0[2] + p1[2]) / 2) * flat + (p0[2] + p1[2]) / 2
    return V, F


def spire(r_base, h, seg=16, bulges=()):
    """Сужающийся шпиль: профиль сверху вниз, утолщения [(f_height, f_radius)]
    задают радиус r_base*f_radius на высоте h*f_height."""
    prof = [(1e-4, h)]
    for fh, fr in sorted(bulges, key=lambda b: -b[0]):
        prof.append((r_base * fr, h * fh))
    prof.append((r_base, 0.0))
    return revolve(prof, seg)
