# Рецепты зданий HUMANS, стиль INDUSTRIAL — брутальный индустриальный бетон
# и сталь по refs/buildings/humans (Factory_1, ColonyBase_1, Laboratory_1, Farm_1):
# ступенчатые серые башни, трубы с ржавыми поясами, фермы, конвейерные мосты,
# бирюзовые экраны (screen), оранжевые технологические свечения (accent),
# красные габаритные огни (redline). Земля z=0, здания растут в +Z.

from building_meshes import *
import numpy as np, math
PI = math.pi


def _p(vf, tag):
    return (vf[0], vf[1], tag)


def _screens(P, x, y, z, w, h, rz=0.0, n=2, gap=0.05):
    """Полоса бирюзовых экранов на фасаде (лицом наружу по rz от +Y)."""
    for k in range(n):
        dx = (k - (n - 1) / 2) * (w + gap)
        c = np.array([x, y, z]) + np.array([math.cos(rz + PI / 2) * dx,
                                            math.sin(rz + PI / 2) * dx, 0])
        P.append(_p(tf(box(w, 0.03, h), t=tuple(c), rz=rz), 'screen'))


def _beacon(P, x, y, z, r=0.03):
    P.append(_p(tf(sphere(r, 6, 5), t=(x, y, z)), 'redline'))


def _mast(P, x, y, z, h, r=0.015):
    P.append(_p(tf(cyl(r, h, 6), t=(x, y, z + h / 2)), 'steel'))
    _beacon(P, x, y, z + h + 0.02)


# ============================================================ планетарные

def colony_base(level=0, seed=0):
    """Ступенчатая пирамида-зиккурат с трубами и угловыми баками
    (реф ColonyBase_humans-1)."""
    P = []
    P.append(_p(frustum(3.0, 3.0, 2.7, 2.7, 0.3), 'conc_d'))
    tiers = [(2.5, 2.3, 1.75, 1.55, 0.85, 0.30),
             (1.65, 1.45, 1.1, 0.95, 0.85, 1.15),
             (1.0, 0.9, 0.55, 0.5, 0.8, 2.0)]
    for sx0, sy0, sx1, sy1, h, z0 in tiers:
        P.append(_p(frustum(sx0, sy0, sx1, sy1, h, z0), 'conc'))
    # остеклённые полосы на ярусах (окна колонии)
    for (sy, z, w) in ((2.32, 0.7, 1.9), (1.42, 1.55, 1.15), (0.86, 2.35, 0.6)):
        for sgn in (-1, 1):
            P.append(_p(tf(box(w, 0.04, 0.18), t=(0, sgn * sy / 2, z)), 'glass'))
    _screens(P, 0, 1.28, 1.85, 0.22, 0.14, n=3)
    # трубы у задней грани
    for dx in (-0.55, 0.55):
        body, collars = chimney(0.14, 1.1, z0=1.0)
        P.append(_p(tf(body, t=(dx, 0.75, 0)), 'conc_l'))
        P.append(_p(tf(collars, t=(dx, 0.75, 0)), 'rust'))
    # угловые баки-хранилища
    for cx, cy in ((1.15, 1.15), (-1.15, 1.15), (1.15, -1.15), (-1.15, -1.15)):
        P.append(_p(tf(cyl(0.3, 0.5, 14), t=(cx, cy, 0.55)), 'steel'))
        P.append(_p(tf(torus(0.3, 0.03, 14, 6), t=(cx, cy, 0.62)), 'rust'))
        P.append(_p(tf(dome(0.3, 14, 5), t=(cx, cy, 0.8)), 'conc_l'))
    # вход с оранжевым зевом
    P.append(_p(tf(box(0.5, 0.3, 0.35), t=(0, -1.5, 0.35)), 'conc_d'))
    P.append(_p(tf(box(0.3, 0.05, 0.22), t=(0, -1.64, 0.32)), 'accent'))
    # антенное поле на вершине
    top = 2.8
    P.append(_p(tf(box(0.4, 0.35, 0.12), t=(0, 0, top + 0.06)), 'dark'))
    for dx, hh in ((-0.12, 0.5), (0.02, 0.7), (0.14, 0.4)):
        _mast(P, dx, 0.05, top + 0.12, hh)
    return merge(P)


def factory(level=0, seed=0):
    """Цех + башня + две трубы с ржавыми поясами + конвейерный мост
    (реф Factory_humans_1)."""
    P = []
    P.append(_p(tf(box(1.9, 1.25, 0.72), t=(0, 0, 0.36)), 'conc'))
    # башня-доминанта
    P.append(_p(frustum(1.1, 0.95, 0.75, 0.62, 1.6, 0.72), 'conc'))
    P.append(_p(frustum(0.8, 0.68, 0.72, 0.6, 0.24, 2.32), 'conc_d'))
    # вентблоки на крыше цеха
    for dx in (-0.6, -0.15, 0.35):
        P.append(_p(tf(box(0.3, 0.35, 0.16), t=(dx, -0.3, 0.8)), 'steel'))
        P.append(_p(tf(box(0.26, 0.31, 0.05), t=(dx, -0.3, 0.9)), 'dark'))
    # трубы
    for dx, hh in ((0.55, 1.9), (0.9, 1.55)):
        body, collars = chimney(0.13, hh, z0=0.72)
        P.append(_p(tf(body, t=(dx, 0.35, 0)), 'conc_l'))
        P.append(_p(tf(collars, t=(dx, 0.35, 0)), 'rust'))
    # боковой блок и конвейерный мост от башни
    P.append(_p(tf(box(0.7, 0.7, 0.9), t=(-1.55, 0.2, 0.45)), 'conc_d'))
    P.append(_p(tf(box(1.25, 0.22, 0.16), t=(-0.95, 0.2, 1.05)), 'steel'))
    for dx in (-1.25, -0.65):
        P.append(_p(tf(box(0.06, 0.06, 1.0), t=(dx, 0.2, 0.5)), 'dark'))
    # жерло печи (оранжевое свечение) на фасаде цеха
    P.append(_p(tf(box(0.5, 0.05, 0.3), t=(0.35, -0.64, 0.3)), 'accent'))
    _screens(P, -0.05, -0.5, 1.5, 0.24, 0.16, n=2)
    _mast(P, 0.1, 0.1, 2.44, 0.6)
    _mast(P, -0.2, -0.1, 2.44, 0.45)
    return merge(P)


def outpost(level=0, seed=0):
    """Круглая платформа с геокуполом и решётчатой мачтой
    (реф Outpost_humans_1)."""
    P = []
    P.append(_p(tf(cyl(1.25, 0.22, 24, r2=1.15), t=(0, 0, 0.11)), 'conc_d'))
    P.append(_p(tf(torus(1.18, 0.03, 24, 6), t=(0, 0, 0.24)), 'rust'))
    glass, frame = geodome(0.82)
    P.append(_p(tf(glass, t=(0, 0, 0.22)), 'glass'))
    P.append(_p(tf(frame, t=(0, 0, 0.22)), 'steel'))
    P.append(_p(tf(cyl(0.2, 0.3, 10), t=(0, 0, 0.22 + 0.82)), 'conc_l'))
    # шлюз и сервисные модули по кольцу
    P.append(_p(tf(box(0.4, 0.5, 0.32), t=(0, -1.0, 0.38)), 'conc'))
    P.append(_p(tf(box(0.22, 0.06, 0.2), t=(0, -1.26, 0.36)), 'accent'))
    for a in (0.7, 2.4, 3.8):
        x, y = 1.0 * math.cos(a), 1.0 * math.sin(a)
        P.append(_p(tf(box(0.36, 0.3, 0.26), t=(x, y, 0.35), rz=a), 'conc_l'))
    # мачта
    mast = lattice_mast(0.42, 0.16, 1.5)
    P.append(_p(tf(mast, t=(1.3, 0.5, 0)), 'steel'))
    d = dish_mesh(0.24)
    P.append(_p(tf(d, t=(1.3, 0.5, 1.35), rx=-PI / 3), 'conc_l'))
    _beacon(P, 1.3, 0.5, 1.56)
    _screens(P, 0, -0.72, 0.5, 0.18, 0.12, n=2)
    return merge(P)


def farm(level=0, seed=0):
    """Ряд сводчатых теплиц + сервисный блок + водонапорный бак
    (реф Farm_humans_1)."""
    P = []
    for dx in (-0.78, 0.0, 0.78):
        P.append(_p(tf(hbarrel(0.62, 1.7, 0.4), t=(dx, 0, 0)), 'glass_g'))
        # грядки внутри
        P.append(_p(tf(box(0.44, 1.5, 0.1), t=(dx, 0, 0.06)), 'green'))
        # торцевые рамы
        for sy in (-0.86, 0.86):
            P.append(_p(tf(box(0.66, 0.05, 0.16), t=(dx, sy, 0.08)), 'conc_d'))
    # сервисный блок
    P.append(_p(tf(box(1.1, 0.55, 0.55), t=(-0.35, -1.25, 0.28)), 'conc'))
    P.append(_p(tf(box(0.3, 0.3, 0.2), t=(-0.1, -1.25, 0.65)), 'steel'))
    _screens(P, -0.35, -1.54, 0.35, 0.2, 0.13, n=2)
    # водонапорный бак на ногах
    for cx, cy in ((0.85, -1.2),):
        for a in np.linspace(0, 2 * PI, 4, endpoint=False):
            P.append(_p(tf(cyl(0.03, 0.7, 6),
                           t=(cx + 0.18 * math.cos(a), cy + 0.18 * math.sin(a),
                              0.35)), 'dark'))
        P.append(_p(tf(cyl(0.26, 0.35, 12), t=(cx, cy, 0.85)), 'steel'))
        P.append(_p(tf(dome(0.26, 12, 5), t=(cx, cy, 1.02)), 'rust'))
        # труба к теплицам
        P.append(_p(arc_pipe((cx, cy, 0.75), (0.78, -0.4, 0.2),
                             (0, 0, 0.15), 0.03), 'steel'))
    return merge(P)


def laboratory(level=0, seed=0):
    """Ступенчатые модули с большим остеклением и трубами по крыше
    (реф Laboratory_humans_1)."""
    P = []
    P.append(_p(tf(box(1.7, 1.25, 0.62), t=(0, 0, 0.31)), 'conc'))
    P.append(_p(tf(box(1.25, 1.05, 0.55), t=(-0.15, 0.05, 0.9)), 'conc'))
    P.append(_p(tf(box(0.8, 0.8, 0.5), t=(-0.3, 0.1, 1.42)), 'conc_d'))
    # большое остекление лаборатории (панорамное окно с рамой)
    P.append(_p(tf(box(0.9, 0.06, 0.4), t=(-0.15, -0.5, 0.9)), 'dark'))
    P.append(_p(tf(box(0.82, 0.05, 0.32), t=(-0.15, -0.52, 0.9)), 'glass'))
    P.append(_p(tf(box(0.5, 0.05, 0.26), t=(0.3, -0.66, 0.35)), 'glass'))
    # трубопровод по крыше: изгиб вдоль модулей
    path = np.array([(0.7, 0.45, 0.66), (0.2, 0.45, 0.7), (-0.2, 0.42, 1.2),
                     (-0.5, 0.4, 1.25), (-0.6, 0.2, 1.7), (-0.45, 0.0, 1.72)])
    P.append(_p(tube(path, 0.05, 8), 'steel'))
    P.append(_p(tf(sphere(0.08, 8, 6), t=(0.7, 0.45, 0.66)), 'rust'))
    # пара тонких вытяжных труб
    for dx, dy in ((0.55, 0.3), (0.75, 0.15)):
        P.append(_p(tf(cyl(0.05, 0.9, 8), t=(dx, dy, 1.05)), 'conc_l'))
        P.append(_p(tf(torus(0.05, 0.015, 8, 5), t=(dx, dy, 1.42)), 'rust'))
    # тарелка и экраны
    d = dish_mesh(0.2)
    P.append(_p(tf(d, t=(-0.3, 0.1, 1.67), rx=-PI / 4, rz=0.6), 'conc_l'))
    _screens(P, -0.3, -0.31, 1.42, 0.2, 0.14, n=2)
    _beacon(P, -0.55, 0.35, 1.7)
    return merge(P)


def research_campus(level=0, seed=0):
    """Центральная башня + три лабблока, связанные крытыми переходами."""
    P = []
    P.append(_p(frustum(1.15, 1.15, 0.8, 0.8, 1.9, 0.0), 'conc'))
    P.append(_p(frustum(0.9, 0.9, 0.85, 0.85, 0.18, 1.9), 'conc_d'))
    _screens(P, 0, 0.47, 1.35, 0.2, 0.35, n=3)
    for a in (PI / 6, PI * 5 / 6, PI * 3 / 2):
        x, y = 1.35 * math.cos(a), 1.35 * math.sin(a)
        P.append(_p(tf(box(0.85, 0.65, 0.55), t=(x, y, 0.28), rz=a), 'conc'))
        P.append(_p(tf(box(0.55, 0.45, 0.3), t=(x, y, 0.7), rz=a), 'conc_d'))
        P.append(_p(bridge_tube((x * 0.55, y * 0.55, 0.42), (x * 0.35, y * 0.35, 0.42),
                                r=0.11, flat=0.65), 'conc_l'))
        P.append(_p(tf(box(0.3, 0.04, 0.18),
                       t=(x - 0.34 * math.sin(a), y + 0.34 * math.cos(a), 0.75),
                       rz=a), 'glass'))
    # приборная площадка на башне
    d = dish_mesh(0.3)
    P.append(_p(tf(d, t=(0.2, 0.2, 2.12), rx=-PI / 3.4, rz=PI / 4), 'conc_l'))
    _mast(P, -0.25, -0.2, 2.08, 0.7)
    _mast(P, 0.05, -0.3, 2.08, 0.45)
    return merge(P)


def megafactory(level=0, seed=0):
    """Двухбашенный гигацех: 4 трубы, надземный конвейер, печные зевы."""
    P = []
    P.append(_p(tf(box(2.9, 1.5, 0.62), t=(0, 0, 0.31)), 'conc'))
    for sgn in (-1, 1):
        P.append(_p(tf(frustum(1.05, 1.1, 0.7, 0.75, 1.75, 0.0),
                       t=(sgn * 0.92, 0.1, 0.62)), 'conc'))
        P.append(_p(tf(box(0.75, 0.8, 0.2), t=(sgn * 0.92, 0.1, 2.45)), 'conc_d'))
    # конвейерная галерея между башнями
    P.append(_p(tf(box(1.5, 0.24, 0.18), t=(0, 0.1, 1.75)), 'steel'))
    P.append(_p(tf(box(0.08, 0.08, 1.0), t=(0, 0.1, 1.2)), 'dark'))
    # 4 трубы
    for k, (dx, dy, hh) in enumerate(((-1.5, 0.55, 1.7), (-1.15, 0.62, 1.4),
                                      (1.2, 0.6, 1.85), (1.55, 0.5, 1.5))):
        body, collars = chimney(0.12, hh, z0=0.62)
        P.append(_p(tf(body, t=(dx, dy, 0)), 'conc_l'))
        P.append(_p(tf(collars, t=(dx, dy, 0)), 'rust'))
    # печные зевы по фасаду
    for dx in (-0.9, -0.3, 0.3, 0.9):
        P.append(_p(tf(box(0.34, 0.05, 0.26), t=(dx, -0.77, 0.3)), 'accent'))
    _screens(P, -0.92, -0.46, 1.9, 0.22, 0.16, n=2)
    _screens(P, 0.92, -0.46, 1.9, 0.22, 0.16, n=2)
    _mast(P, 0.92, 0.3, 2.55, 0.65)
    return merge(P)


def habitat(level=0, seed=0):
    """Террасные жилые блоки с оконными полосами и купольной оранжереей."""
    P = []
    steps = [(2.1, 1.0, 0.55, 0.0, 0.35), (1.7, 0.95, 0.5, 0.55, 0.15),
             (1.3, 0.9, 0.5, 1.05, -0.05), (0.9, 0.85, 0.45, 1.55, -0.25)]
    for sx, sy, h, z0, xoff in steps:
        P.append(_p(tf(box(sx, sy, h), t=(xoff, 0, z0 + h / 2)), 'conc'))
        # оконные полосы
        P.append(_p(tf(box(sx * 0.85, 0.04, 0.14),
                       t=(xoff, -sy / 2 - 0.01, z0 + h * 0.55)), 'glass'))
    # оранжерея на верхней террасе
    P.append(_p(tf(hbarrel(0.5, 0.7, 0.3), t=(0.55, 0.05, 1.6)), 'glass_g'))
    P.append(_p(tf(box(0.4, 0.6, 0.06), t=(0.55, 0.05, 1.62)), 'green'))
    # лифтовая башня и бак
    P.append(_p(tf(cyl(0.18, 2.2, 10), t=(-1.15, 0.3, 1.1)), 'conc_d'))
    P.append(_p(tf(cyl(0.24, 0.3, 10), t=(-1.15, 0.3, 2.3)), 'steel'))
    P.append(_p(tf(dome(0.24, 10, 5), t=(-1.15, 0.3, 2.45)), 'rust'))
    P.append(_p(bridge_tube((-1.0, 0.3, 1.75), (-0.6, 0.2, 1.75), r=0.1,
                            flat=0.7), 'conc_l'))
    _screens(P, 0.35, -0.44, 1.3, 0.16, 0.12, n=2)
    _beacon(P, -0.25, 0.3, 1.85)
    return merge(P)


def hydroponifier(level=0, seed=0):
    """Стеллаж гидропоники: стойки, три стеклянных яруса с грядками,
    горизонтальный бак и насосная обвязка."""
    P = []
    P.append(_p(tf(box(2.1, 1.05, 0.18), t=(0, 0, 0.09)), 'conc_d'))
    for cx, cy in ((-0.95, -0.42), (0.95, -0.42), (-0.95, 0.42), (0.95, 0.42)):
        P.append(_p(tf(box(0.14, 0.14, 1.7), t=(cx, cy, 0.95)), 'conc'))
    for k, z0 in enumerate((0.35, 0.85, 1.35)):
        P.append(_p(tf(box(2.0, 0.95, 0.3), t=(0, 0, z0 + 0.15)), 'glass_g'))
        P.append(_p(tf(box(1.9, 0.85, 0.07), t=(0, 0, z0 + 0.05)), 'green'))
        P.append(_p(tf(box(2.04, 0.99, 0.05), t=(0, 0, z0 + 0.31)), 'steel'))
    # крышный бак на ложементах
    P.append(_p(tf(tf(cyl(0.24, 1.2, 12), rx=PI / 2), t=(-0.3, 0, 1.98)), 'steel'))
    P.append(_p(tf(torus(0.24, 0.025, 12, 6), t=(-0.3, 0.3, 1.98), rx=PI / 2), 'rust'))
    P.append(_p(tf(torus(0.24, 0.025, 12, 6), t=(-0.3, -0.3, 1.98), rx=PI / 2), 'rust'))
    # насосный блок + трубы вниз по торцу
    P.append(_p(tf(box(0.4, 0.5, 0.45), t=(1.25, 0, 0.22)), 'conc'))
    path = np.array([(1.25, 0, 0.5), (1.25, 0, 1.98), (0.4, 0, 1.98)])
    P.append(_p(tube(path, 0.04, 6), 'steel'))
    _screens(P, 1.25, -0.26, 0.32, 0.16, 0.12, n=1)
    _beacon(P, -0.95, 0.42, 1.85)
    return merge(P)


def metroplex(level=0, seed=0):
    """Кластер ступенчатых башен с мостами (реф Factory_humans_1 city)."""
    P = []
    P.append(_p(tf(box(3.2, 3.2, 0.3), t=(0, 0, 0.15)), 'conc_d'))
    towers = [(-0.9, -0.7, 1.0, 2.9), (0.35, -0.95, 0.85, 2.2),
              (0.95, 0.1, 0.9, 3.3), (-0.15, 0.35, 0.8, 2.5),
              (-1.05, 0.85, 0.75, 1.9)]
    rng = np.random.default_rng(seed + 3)
    for x, y, w, h in towers:
        P.append(_p(tf(frustum(w, w * 0.85, w * 0.6, w * 0.52, h, 0.3),
                       t=(x, y, 0)), 'conc'))
        P.append(_p(tf(frustum(w * 0.62, w * 0.54, w * 0.56, w * 0.5, 0.12,
                               0.3 + h), t=(x, y, 0)), 'conc_d'))
        # оконные полосы на двух фасадах
        for zf in (0.4, 0.62, 0.84):
            P.append(_p(tf(box(w * 0.5, 0.03, 0.1),
                           t=(x, y - w * (0.85 - 0.33 * zf) / 2 - 0.02,
                              0.3 + h * zf)), 'glass'))
    # мосты между башнями
    links = [(0, 2, 1.35), (0, 3, 0.95), (2, 3, 1.7), (1, 2, 0.8), (3, 4, 1.1)]
    for i, j, z in links:
        xi, yi = towers[i][0], towers[i][1]
        xj, yj = towers[j][0], towers[j][1]
        P.append(_p(bridge_tube((xi, yi, z), (xj, yj, z), r=0.09, flat=0.6),
                    'conc_l'))
    # шпили и экраны на двух высших
    _mast(P, 0.95, 0.1, 3.72, 0.75)
    _mast(P, -0.9, -0.7, 3.32, 0.6)
    _screens(P, 0.95, -0.19, 2.9, 0.18, 0.3, n=1)
    _screens(P, -0.9, -1.0, 2.4, 0.18, 0.3, n=1)
    return merge(P)


def power_plant(level=0, seed=0):
    """Две градирни + машзал + реакторный купол + труба."""
    P = []
    for dx in (-0.8, 0.85):
        P.append(_p(tf(cooling_tower(0.55, 0.35, 0.4, 1.75), t=(dx, 0.5, 0)),
                    'conc'))
        P.append(_p(tf(torus(0.4, 0.03, 20, 6), t=(dx, 0.5, 1.74)), 'rust'))
        _beacon(P, dx + 0.4, 0.5, 1.78)
    # машзал
    P.append(_p(tf(box(2.3, 1.0, 0.6), t=(0, -0.85, 0.3)), 'conc'))
    for dx in (-0.9, -0.45, 0.0, 0.45, 0.9):
        P.append(_p(tf(box(0.28, 0.04, 0.2), t=(dx, -1.36, 0.32)), 'accent'))
    # реакторный купол
    P.append(_p(tf(cyl(0.5, 0.4, 18), t=(0, 0.35, 0.2)), 'conc_d'))
    P.append(_p(tf(dome(0.5, 18, 7), t=(0, 0.35, 0.4)), 'conc_l'))
    # трубопроводы градирни <-> машзал
    for dx in (-0.8, 0.85):
        P.append(_p(arc_pipe((dx, 0.15, 0.5), (dx * 0.5, -0.6, 0.55),
                             (0, 0, 0.25), 0.05), 'steel'))
    body, collars = chimney(0.11, 1.3, z0=0.6)
    P.append(_p(tf(body, t=(1.05, -0.85, 0)), 'conc_l'))
    P.append(_p(tf(collars, t=(1.05, -0.85, 0)), 'rust'))
    _screens(P, -0.7, -1.36, 0.52, 0.2, 0.13, n=2)
    return merge(P)


def sky_net(level=0, seed=0):
    """Большая решётчатая антенная мачта на бункере + три тарелки."""
    P = []
    P.append(_p(frustum(1.5, 1.5, 1.15, 1.15, 0.55, 0.0), 'conc'))
    P.append(_p(frustum(0.9, 0.9, 0.75, 0.75, 0.25, 0.55), 'conc_d'))
    mast = lattice_mast(0.7, 0.22, 2.6, bays=5, r=0.022)
    P.append(_p(tf(mast, t=(0, 0, 0.8)), 'steel'))
    # тарелки на разной высоте, смотрят в разные стороны
    for z, a, r in ((1.6, 0.4, 0.34), (2.2, 2.4, 0.3), (2.8, 4.4, 0.26)):
        arm_end = (0.35 * math.cos(a), 0.35 * math.sin(a), z)
        P.append(_p(tube(np.array([(0, 0, z), arm_end]), 0.03, 6), 'steel'))
        P.append(_p(tf(dish_mesh(r), t=arm_end, ry=PI / 2.4, rz=a), 'conc_l'))
    # растяжки к якорям
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        ax, ay = 1.35 * math.cos(a), 1.35 * math.sin(a)
        P.append(_p(tube(np.array([(0.1 * math.cos(a), 0.1 * math.sin(a), 3.1),
                                   (ax, ay, 0.1)]), 0.012, 4), 'dark'))
        P.append(_p(tf(box(0.16, 0.16, 0.12), t=(ax, ay, 0.06)), 'conc_d'))
    _beacon(P, 0, 0, 3.48, r=0.045)
    _screens(P, 0, -0.76, 0.32, 0.24, 0.16, n=2)
    return merge(P)


def eco_booster(level=0, seed=0):
    """Геокупол-биом с зелёным нутром + башни-скрубберы с обвязкой."""
    P = []
    P.append(_p(tf(cyl(1.15, 0.18, 24, r2=1.08), t=(0, 0, 0.09)), 'conc_d'))
    glass, frame = geodome(1.0)
    P.append(_p(tf(glass, t=(0, 0, 0.18)), 'glass_g'))
    P.append(_p(tf(frame, t=(0, 0, 0.18)), 'steel'))
    # зелёные холмы внутри купола
    rng = np.random.default_rng(seed + 11)
    for _ in range(5):
        x, y = rng.uniform(-0.55, 0.55, 2)
        r = rng.uniform(0.16, 0.3)
        P.append(_p(tf(sphere(r, 10, 6), t=(x, y, 0.18), s=(1, 1, 0.55)), 'green'))
    # башни-скрубберы
    for dx in (-1.5, 1.5):
        P.append(_p(tf(cyl(0.2, 1.25, 12), t=(dx, -0.3, 0.62)), 'conc_l'))
        for zf in (0.45, 0.75, 1.05):
            P.append(_p(tf(torus(0.2, 0.025, 12, 6), t=(dx, -0.3, zf)), 'rust'))
        P.append(_p(tf(cyl(0.23, 0.1, 12), t=(dx, -0.3, 1.28)), 'dark'))
        P.append(_p(arc_pipe((dx, -0.3, 1.0), (dx * 0.45, -0.15, 0.6),
                             (0, 0, 0.35), 0.045), 'steel'))
    P.append(_p(tf(box(0.5, 0.4, 0.3), t=(0, -1.25, 0.15)), 'conc'))
    _screens(P, 0, -1.46, 0.2, 0.18, 0.12, n=2)
    return merge(P)


def terraforming(level=0, seed=0):
    """Атмосферный процессор: гигантская воронка-вихревик на машинном
    основании, контрфорсные трубы, кольцо паровых стояков."""
    P = []
    P.append(_p(frustum(1.9, 1.9, 1.5, 1.5, 0.6, 0.0), 'conc'))
    P.append(_p(frustum(1.3, 1.3, 1.05, 1.05, 0.3, 0.6), 'conc_d'))
    # воронка (раструб вверх)
    funnel = revolve([(1.05, 2.4), (0.95, 2.35), (0.5, 1.6), (0.42, 1.15),
                      (0.5, 0.9)], 22)
    P.append(_p(funnel, 'conc_l'))
    P.append(_p(tf(torus(1.02, 0.05, 22, 7), t=(0, 0, 2.4)), 'steel'))
    # оранжевое свечение в жерле
    P.append(_p(tf(cyl(0.88, 0.06, 20), t=(0, 0, 2.3)), 'accent'))
    # контрфорсные трубы в жерло
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        x0, y0 = 1.15 * math.cos(a), 1.15 * math.sin(a)
        x1, y1 = 0.62 * math.cos(a), 0.62 * math.sin(a)
        P.append(_p(tube(np.array([(x0, y0, 0.3), (x0 * 0.95, y0 * 0.95, 1.5),
                                   (x1, y1, 2.15)]), 0.09, 8), 'steel'))
    # кольцо паровых стояков
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        x, y = 1.35 * math.cos(a), 1.35 * math.sin(a)
        P.append(_p(tf(cyl(0.08, 0.9, 8), t=(x, y, 1.05)), 'conc_l'))
        P.append(_p(tf(torus(0.08, 0.018, 8, 5), t=(x, y, 1.4)), 'rust'))
    _screens(P, 0, -0.96, 0.75, 0.24, 0.18, n=3)
    _beacon(P, 0.99, 0, 2.48)
    _beacon(P, -0.99, 0, 2.48)
    return merge(P)


# ============================================================ орбитальные
# Центр конструкции ~z=1.0, диаметр растёт с уровнем. Ось «вниз к планете»
# для орудий — +Y (как «лицо» устройств кораблей).

def _ring_greebles(P, R, z, seed, n=10, tags=('steel', 'conc_d', 'rust')):
    rng = np.random.default_rng(seed)
    for _ in range(n):
        a = rng.uniform(0, 2 * PI)
        s = rng.uniform(0.06, 0.16)
        P.append(_p(tf(box(s, s * rng.uniform(0.6, 1.6), s),
                       t=(R * math.cos(a), R * math.sin(a),
                          z + rng.uniform(-0.05, 0.12)), rz=a),
                    tags[rng.integers(0, len(tags))]))


def orb_dock(level=1, seed=0):
    """Гранёное кольцо-верфь с доковыми пилонами (реф SpaceDock_humans_1)."""
    P = []
    s = 0.72 + 0.16 * level
    zc = 1.0
    R = 0.85 * s
    n = 8
    # кольцо из сегментов
    for vf in box_ring(R, n, 0.26 * s, 0.62 * s, 0.3 * s, z=zc):
        P.append(_p(vf, 'conc'))
    for vf in box_ring(R, n, 0.1 * s, 0.3 * s, 0.34 * s, z=zc,
                       phase=PI / n):
        P.append(_p(vf, 'conc_d'))
    # угловые доковые пилоны с оранжевыми огнями
    for k, a in enumerate(np.linspace(PI / 4, 2 * PI + PI / 4, 4,
                                      endpoint=False)):
        x, y = (R + 0.28 * s) * math.cos(a), (R + 0.28 * s) * math.sin(a)
        P.append(_p(tf(box(0.34 * s, 0.5 * s, 0.42 * s), t=(x, y, zc), rz=a),
                    'conc_l'))
        P.append(_p(tf(box(0.1 * s, 0.1 * s, 0.5 * s), t=(x, y, zc), rz=a),
                    'dark'))
        P.append(_p(tf(sphere(0.035 * s, 6, 5),
                       t=(x, y, zc + 0.28 * s)), 'accent'))
    # центральная балка-траверса с причальными зажимами
    P.append(_p(tf(box(2 * R, 0.18 * s, 0.14 * s), t=(0, 0, zc)), 'steel'))
    P.append(_p(tf(box(0.34 * s, 0.3 * s, 0.24 * s), t=(0, 0, zc)), 'conc_d'))
    for sgn in (-1, 1):
        P.append(_p(tf(box(0.1 * s, 0.4 * s, 0.08 * s),
                       t=(sgn * 0.45 * R, 0, zc + 0.12 * s)), 'steel'))
    if level >= 3:  # вторая балка крестом
        P.append(_p(tf(box(2 * R, 0.14 * s, 0.12 * s), t=(0, 0, zc), rz=PI / 2),
                    'steel'))
    if level >= 4:  # второй ярус кольца
        for vf in box_ring(R * 0.98, n, 0.2 * s, 0.5 * s, 0.22 * s,
                           z=zc + 0.42 * s, phase=PI / n):
            P.append(_p(vf, 'conc_l'))
    _ring_greebles(P, R, zc + 0.16 * s, seed + level, n=8 + 3 * level)
    return merge(P)


def orb_shield(level=1, seed=0):
    """Колесо-щит: обод с панелями, спицы, хаб с эмиттерами
    (реф SpaceShield_humans_1)."""
    P = []
    s = 0.78 + 0.14 * level
    zc = 1.0
    R = 0.95 * s
    P.append(_p(tf(torus(R, 0.085 * s, 30, 9), t=(0, 0, zc)), 'conc'))
    # панельные плиты по ободу (солнечные — тёмные)
    for k, vf in enumerate(box_ring(R, 12, 0.3 * s, 0.42 * s, 0.05 * s, z=zc)):
        P.append(_p(vf, 'dark' if k % 3 == 0 else 'conc_d'))
    # спицы и хаб
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        P.append(_p(tube(np.array([(0.2 * s * math.cos(a), 0.2 * s * math.sin(a), zc),
                                   (R * math.cos(a), R * math.sin(a), zc)]),
                         0.035 * s, 6), 'steel'))
    P.append(_p(tf(sphere(0.26 * s, 16, 9), t=(0, 0, zc)), 'conc_l'))
    # эмиттерные кольца по уровню
    for k in range(level):
        P.append(_p(tf(torus((0.3 + 0.09 * k) * s, 0.022 * s, 18, 6),
                       t=(0, 0, zc), rx=PI / 2), 'bglow'))
    P.append(_p(tf(sphere(0.09 * s, 8, 6), t=(0, 0, zc + 0.3 * s)), 'bglow'))
    _ring_greebles(P, R, zc + 0.06 * s, seed + 20 + level, n=6 + 2 * level)
    return merge(P)


def orb_laser(level=1, seed=0):
    """Кольцевая лазерная платформа: хаб со стволом в +Y, фокус-кольца
    (реф OrbitalLaser_humans_1)."""
    P = []
    s = 0.75 + 0.14 * level
    zc = 1.0
    R = 0.8 * s
    P.append(_p(tf(torus(R, 0.07 * s, 26, 8), t=(0, 0, zc), rx=PI / 2), 'conc'))
    for k, vf in enumerate(box_ring(R, 8, 0.24 * s, 0.34 * s, 0.05 * s, z=0)):
        V, F, tag = vf[0], vf[1], ('conc_d' if k % 2 else 'conc_l')
        # кольцо стоит вертикально (плоскость XZ): поворот вокруг X
        V = (tf((V, F), rx=PI / 2)[0] + np.array([0, 0, zc]))
        P.append((V, F, tag))
    # спицы к хабу
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        x, z = R * math.cos(a), R * math.sin(a)
        P.append(_p(tube(np.array([(x * 0.25, 0, zc + z * 0.25),
                                   (x, 0, zc + z)]), 0.03 * s, 6), 'steel'))
    # хаб + ствол
    P.append(_p(tf(cyl(0.24 * s, 0.4 * s, 14), t=(0, 0, zc), rx=PI / 2), 'conc_l'))
    L = (0.55 + 0.12 * level) * s
    P.append(_p(tf(cyl(0.09 * s, L, 10), t=(0, 0.2 * s + L / 2, zc), rx=PI / 2),
                'steel'))
    for k in range(level + 1):
        P.append(_p(tf(torus(0.13 * s, 0.02 * s, 14, 6),
                       t=(0, (0.3 + 0.16 * k) * s, zc), rx=PI / 2), 'redline'))
    P.append(_p(tf(cyl(0.05 * s, 0.06 * s, 8), t=(0, 0.22 * s + L, zc),
                   rx=PI / 2), 'accent'))
    # тыльный радиатор
    P.append(_p(tf(box(0.4 * s, 0.2 * s, 0.5 * s), t=(0, -0.3 * s, zc)), 'dark'))
    _beacon(P, 0, 0, zc + R + 0.08 * s, r=0.03 * s)
    _beacon(P, 0, 0, zc - R - 0.08 * s, r=0.03 * s)
    return merge(P)


def orb_phazer(level=1, seed=0):
    """Орудийная платформа: гранёная плита + тяжёлая счетверённая турель
    с синими линзами (реф OrbitalPhaser_humans_1)."""
    P = []
    s = 0.8 + 0.13 * level
    zc = 0.75
    P.append(_p(tf(cyl(0.8 * s, 0.12 * s, 8), t=(0, 0, zc)), 'conc_d'))
    P.append(_p(tf(cyl(0.55 * s, 0.1 * s, 8, r2=0.66 * s),
                   t=(0, 0, zc + 0.1 * s)), 'conc'))
    # ферма под плитой
    m = lattice_mast(0.7 * s, 0.4 * s, 0.4 * s, bays=2, r=0.015 * s,
                     z0=zc - 0.5 * s)
    P.append(_p(m, 'steel'))
    # турель: тумба + качающийся блок с подами
    P.append(_p(tf(cyl(0.24 * s, 0.26 * s, 12), t=(0, 0, zc + 0.24 * s)),
                'conc_l'))
    tilt = 0.6
    dirv = np.array([0, math.cos(tilt), math.sin(tilt)])
    ux = np.array([1.0, 0, 0])
    uz = np.cross(ux, dirv)
    hc = np.array([0, 0, zc + 0.45 * s])
    P.append(_p(tf(box(0.5 * s, 0.4 * s, 0.3 * s), t=tuple(hc), rx=-(PI / 2 - tilt) * 0.4),
                'conc'))
    n_pods = 1 + level
    xs = np.linspace(-0.16 * s * (n_pods - 1), 0.16 * s * (n_pods - 1), n_pods)
    for dx in xs:
        base = hc + ux * dx + dirv * 0.18 * s
        plen = 0.55 * s
        c = base + dirv * plen / 2
        P.append(_p(tf(cyl(0.1 * s, plen, 10), t=tuple(c),
                       rx=-(PI / 2 - tilt)), 'steel'))
        face = base + dirv * (plen + 0.02 * s)
        P.append(_p(tf(cyl(0.08 * s, 0.05 * s, 10), t=tuple(face),
                       rx=-(PI / 2 - tilt)), 'bglow'))
    # кабель-дуги к тумбе
    P.append(_p(arc_pipe((0.3 * s, -0.3 * s, zc + 0.1 * s),
                         tuple(hc + np.array([0.1 * s, -0.2 * s, 0])),
                         (0, 0, 0.1 * s), 0.02 * s), 'rust'))
    _beacon(P, 0.78 * s, 0, zc + 0.1 * s, r=0.03 * s)
    _beacon(P, -0.78 * s, 0, zc + 0.1 * s, r=0.03 * s)
    return merge(P)


def orb_phazer_rapid(level=1, seed=0):
    """Скорострельная орбитальная турель: две роторные кассеты стволов."""
    P = []
    s = 0.85 + 0.13 * level
    zc = 0.75
    P.append(_p(tf(cyl(0.7 * s, 0.1 * s, 8), t=(0, 0, zc)), 'conc_d'))
    m = lattice_mast(0.6 * s, 0.35 * s, 0.35 * s, bays=2, r=0.014 * s,
                     z0=zc - 0.45 * s)
    P.append(_p(m, 'steel'))
    P.append(_p(tf(cyl(0.22 * s, 0.2 * s, 12), t=(0, 0, zc + 0.15 * s)), 'conc'))
    tilt = 0.55
    dirv = np.array([0, math.cos(tilt), math.sin(tilt)])
    ux = np.array([1.0, 0, 0])
    hc = np.array([0, 0, zc + 0.38 * s])
    P.append(_p(tf(box(0.55 * s, 0.35 * s, 0.26 * s), t=tuple(hc),
                   rx=-(PI / 2 - tilt) * 0.35), 'conc_l'))
    # две кассеты по 4 ствола (уровень 2 — по 6)
    n_b = 4 + (level - 1) * 2
    for sgn in (-1, 1):
        pod = hc + ux * sgn * 0.22 * s + dirv * 0.16 * s
        plen = 0.42 * s
        P.append(_p(tf(cyl(0.11 * s, 0.3 * s, 10), t=tuple(pod),
                       rx=-(PI / 2 - tilt)), 'conc_d'))
        for a in np.linspace(0, 2 * PI, n_b, endpoint=False):
            off = (ux * math.cos(a) + np.cross(dirv, ux) * math.sin(a)) * 0.06 * s
            c = pod + off + dirv * (0.15 * s + plen / 2)
            P.append(_p(tf(cyl(0.022 * s, plen, 6), t=tuple(c),
                           rx=-(PI / 2 - tilt)), 'steel'))
        face = pod + dirv * (0.15 * s + plen)
        P.append(_p(tf(sphere(0.045 * s, 8, 6), t=tuple(face)), 'bglow'))
    # магазины-короба по бокам
    for sgn in (-1, 1):
        P.append(_p(tf(box(0.16 * s, 0.3 * s, 0.22 * s),
                       t=(sgn * 0.42 * s, -0.15 * s, zc + 0.3 * s)), 'rust'))
    _beacon(P, 0, -0.68 * s, zc + 0.05 * s, r=0.03 * s)
    return merge(P)


# ============================================================ пропсы

def prop_blocks(variant=1, seed=0):
    """Хаотичные контейнеры-блоки (аналог Random blocks старого сета)."""
    P = []
    tags = ('rust', 'conc', 'steel', 'conc_d', 'dark')
    boxes = scatter_boxes(seed + variant * 17, 6 + variant * 2, 0.5,
                          0.14, 0.34, hmax=0.26)
    for k, vf in enumerate(boxes):
        P.append(_p(vf, tags[k % len(tags)]))
    return merge(P)


def prop_tanks(level=0, seed=0):
    """Группа баков-хранилищ с обвязкой."""
    P = []
    for (x, y, r, h) in ((-0.3, 0.15, 0.2, 0.55), (0.15, 0.25, 0.16, 0.42),
                         (0.0, -0.2, 0.13, 0.35)):
        P.append(_p(tf(cyl(r, h, 12), t=(x, y, h / 2)), 'steel'))
        P.append(_p(tf(dome(r, 12, 4), t=(x, y, h)), 'rust'))
    # горизонтальная цистерна на ложементах
    P.append(_p(tf(tf(cyl(0.13, 0.55, 10), rx=PI / 2), t=(0.42, -0.05, 0.16)),
                'conc_l'))
    for dy in (-0.18, 0.18):
        P.append(_p(tf(box(0.2, 0.06, 0.12), t=(0.42, -0.05 + dy, 0.06)), 'conc_d'))
    P.append(_p(arc_pipe((-0.3, 0.15, 0.5), (0.42, -0.05, 0.3), (0, 0, 0.15),
                         0.018), 'steel'))
    return merge(P)


def prop_pipes(level=0, seed=0):
    """Наземный трубопровод на опорах с вентилем и вентблоком."""
    P = []
    path = np.array([(-0.55, -0.1, 0.14), (-0.2, -0.1, 0.14), (0.0, 0.0, 0.14),
                     (0.3, 0.1, 0.14), (0.3, 0.1, 0.4), (0.55, 0.15, 0.4)])
    P.append(_p(tube(path, 0.045, 8), 'steel'))
    for x, y in ((-0.4, -0.1), (0.1, 0.03)):
        P.append(_p(tf(box(0.08, 0.08, 0.12), t=(x, y, 0.055)), 'conc_d'))
    P.append(_p(tf(sphere(0.06, 8, 6), t=(0.0, 0.0, 0.2)), 'rust'))
    P.append(_p(tf(cyl(0.015, 0.1, 6), t=(0.0, 0.0, 0.28)), 'dark'))
    P.append(_p(tf(box(0.24, 0.28, 0.2), t=(-0.5, 0.25, 0.1)), 'conc_l'))
    P.append(_p(tf(box(0.2, 0.24, 0.05), t=(-0.5, 0.25, 0.22)), 'dark'))
    return merge(P)


def prop_mast(level=0, seed=0):
    """Связная мачта с тарелкой и аппаратным боксом."""
    P = []
    P.append(_p(lattice_mast(0.26, 0.1, 1.15), 'steel'))
    P.append(_p(tf(dish_mesh(0.14), t=(0.06, 0.06, 0.85), rx=-PI / 3, rz=PI / 4),
                'conc_l'))
    P.append(_p(tf(box(0.2, 0.16, 0.18), t=(0.22, -0.12, 0.09)), 'conc_d'))
    _beacon(P, 0, 0, 1.2)
    return merge(P)


def prop_pad(level=0, seed=0):
    """Посадочная площадка с габаритными огнями."""
    P = []
    P.append(_p(tf(cyl(0.62, 0.07, 8), t=(0, 0, 0.035)), 'conc_d'))
    P.append(_p(tf(cyl(0.5, 0.02, 8), t=(0, 0, 0.08)), 'conc'))
    for a in np.linspace(PI / 8, 2 * PI, 8, endpoint=False):
        P.append(_p(tf(sphere(0.025, 6, 5),
                       t=(0.56 * math.cos(a), 0.56 * math.sin(a), 0.09)),
                    'accent'))
    P.append(_p(tf(box(0.14, 0.18, 0.16), t=(0.62, 0.35, 0.08)), 'conc_l'))
    _mast(P, 0.68, -0.3, 0.07, 0.32, r=0.012)
    return merge(P)
