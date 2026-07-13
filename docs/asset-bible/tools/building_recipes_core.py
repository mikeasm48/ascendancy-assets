# Рецепты зданий CORE — набор «по умолчанию» для рас без своих китов.
# Стиль по refs/buildings/core: диорама на плите-основании (белый борт +
# газон/техпокрытие), белый и серебристый металл, стеклянные купола и
# теплицы, цветные трубы (золото/бирюза/зелень), серебристые баки,
# красно-белые полосатые трубы, солнечные панели, оранжевые (accent) и
# синие (bglow) свечения. Земля z=0, плита ~0.19, строения растут в +Z.
#
# Список: 14 BuildingType + 4 наземных спецпозиции по рефам
# (Engineering Retreat, Surface Shield, Surface Megashield, Alien Ruins)
# + 6 пропсов-расширителей. Порядок фиксирует building_catalog_core.py.

from building_meshes import *
import numpy as np, math
PI = math.pi


def _p(vf, tag):
    return (vf[0], vf[1], tag)


# --------------------------------------------------------------- helpers

def _plate(P, size=3.2, top='grass', shape='square'):
    """Плита-основание диорамы; возвращает z поверхности."""
    if shape == 'square':
        P.append(_p(tf(box(size, size, 0.14), t=(0, 0, 0.07)), 'plate'))
        if top:
            P.append(_p(tf(box(size * 0.93, size * 0.93, 0.05),
                           t=(0, 0, 0.165)), top))
    elif shape == 'hex':
        P.append(_p(tf(cyl(size / 2, 0.14, 6), t=(0, 0, 0.07), rz=PI / 6),
                    'plate'))
        if top:
            P.append(_p(tf(cyl(size / 2 * 0.93, 0.05, 6),
                           t=(0, 0, 0.165), rz=PI / 6), top))
    else:  # round
        P.append(_p(tf(cyl(size / 2, 0.14, 28), t=(0, 0, 0.07)), 'plate'))
        if top:
            P.append(_p(tf(cyl(size / 2 * 0.93, 0.05, 28),
                           t=(0, 0, 0.165)), top))
    return 0.19


def _beacon(P, x, y, z, r=0.03):
    P.append(_p(tf(sphere(r, 6, 5), t=(x, y, z)), 'redline'))


def _mast(P, x, y, z, h, r=0.015, tag='silver'):
    P.append(_p(tf(cyl(r, h, 6), t=(x, y, z + h / 2)), tag))
    _beacon(P, x, y, z + h + 0.02)


def _screens(P, x, y, z, w, h, rz=0.0, n=2, gap=0.05):
    for k in range(n):
        dx = (k - (n - 1) / 2) * (w + gap)
        c = np.array([x, y, z]) + np.array([math.cos(rz + PI / 2) * dx,
                                            math.sin(rz + PI / 2) * dx, 0])
        P.append(_p(tf(box(w, 0.03, h), t=tuple(c), rz=rz), 'screen'))


def _solar(P, x, y, z, w=0.34, l=0.46, rz=0.0, tilt=0.28):
    """Солнечная панель на низкой стойке."""
    P.append(_p(tf(box(0.05, 0.05, 0.07), t=(x, y, z + 0.035)), 'dark'))
    P.append(_p(tf(tf(box(w, l, 0.03), rx=tilt), t=(x, y, z + 0.1), rz=rz),
                'solar'))


def _tank(P, x, y, r, h, z0, body='silver', cap='silver'):
    """Вертикальный бак: корпус + пояс + купол."""
    P.append(_p(tf(cyl(r, h, 14), t=(x, y, z0 + h / 2)), body))
    P.append(_p(tf(torus(r, 0.028, 14, 6), t=(x, y, z0 + h * 0.75)), 'steel'))
    P.append(_p(tf(dome(r, 14, 5), t=(x, y, z0 + h)), cap))


def _pot_tank(P, x, y, r, h, z0):
    """Приземистый серебристый чан с крышкой-блином и пипкой (Agriplot)."""
    P.append(_p(tf(cyl(r, h, 16), t=(x, y, z0 + h / 2)), 'silver'))
    P.append(_p(tf(cyl(r * 1.06, 0.05, 16), t=(x, y, z0 + h + 0.025)),
                'silver'))
    P.append(_p(tf(cyl(r * 0.2, 0.06, 10), t=(x, y, z0 + h + 0.08)), 'steel'))


def _striped_chimney(P, x, y, r, h, z0, bands=5):
    """Красно-белая полосатая труба."""
    bh = h / bands
    for k in range(bands):
        tag = 'red' if k % 2 else 'white'
        P.append(_p(tf(cyl(r * (1 - 0.06 * k / bands), bh, 12),
                       t=(x, y, z0 + bh * (k + 0.5))), tag))
    P.append(_p(tf(torus(r * 0.94, 0.02, 12, 5), t=(x, y, z0 + h)), 'dark'))


def _glassdome(P, x, y, r, z0, glass='glass', frame='silver'):
    g, f = geodome(r)
    P.append(_p(tf(g, t=(x, y, z0)), glass))
    P.append(_p(tf(f, t=(x, y, z0)), frame))


def _dish(P, x, y, z, r, tilt=-PI / 3, rz=0.0, tag='white'):
    P.append(_p(tf(dish_mesh(r), t=(x, y, z), rx=tilt, rz=rz), tag))


def _gold_pipe(P, p0, p1, lift=0.35, r=0.075):
    P.append(_p(arc_pipe(p0, p1, (0, 0, lift), r), 'gold'))
    for pt in (p0, p1):
        P.append(_p(tf(sphere(r * 1.35, 8, 6), t=pt), 'steel'))


# ========================================================== BuildingType

def colony_base(level=0, seed=0):
    """Купол-жилблок + пакет реактора с оранжевыми стержнями + серый блок
    + зелёная вентбашня, всё обвязано золотыми трубами (реф ColonyBase)."""
    P = []
    Z = _plate(P, 3.3, top='grass')
    # бирюзовый жилой купол на кольце
    P.append(_p(tf(cyl(0.92, 0.1, 22), t=(-0.75, -0.62, Z + 0.05)), 'white'))
    P.append(_p(tf(dome(0.85, 22, 9), t=(-0.75, -0.62, Z + 0.1)), 'teal'))
    for a in (-0.5, 0.2, 0.9):
        P.append(_p(tf(box(0.26, 0.04, 0.12),
                       t=(-0.75 + 0.8 * math.sin(a), -0.62 - 0.8 * math.cos(a),
                          Z + 0.38), rz=a), 'glass'))
    # пакет реактора: стопка серебристых барабанов
    rx, ry = -0.05, 0.55
    for k in range(4):
        P.append(_p(tf(cyl(0.5 - 0.01 * k, 0.3, 18),
                       t=(rx, ry, Z + 0.15 + 0.32 * k)), 'silver'))
        P.append(_p(tf(torus(0.5 - 0.01 * k, 0.035, 18, 6),
                       t=(rx, ry, Z + 0.3 + 0.32 * k)), 'steel'))
    P.append(_p(tf(cyl(0.42, 0.12, 18), t=(rx, ry, Z + 1.48)), 'dark'))
    for a in np.linspace(0, 2 * PI, 4, endpoint=False):
        P.append(_p(tf(cyl(0.055, 0.5, 8),
                       t=(rx + 0.2 * math.cos(a), ry + 0.2 * math.sin(a),
                          Z + 1.75)), 'accent'))
    # серый ступенчатый техблок с солнечными панелями
    P.append(_p(tf(box(1.05, 0.95, 1.15), t=(1.0, 0.55, Z + 0.575)), 'conc'))
    P.append(_p(tf(box(0.85, 0.8, 0.45), t=(1.0, 0.55, Z + 1.35)), 'conc_d'))
    _solar(P, 0.85, 0.45, Z + 1.58, rz=0.3)
    _screens(P, 0.62, 0.07, Z + 0.75, 0.2, 0.14, n=2)
    # зелёная вентбашня
    P.append(_p(tf(cyl(0.34, 1.05, 14), t=(1.05, -0.72, Z + 0.525)), 'green'))
    P.append(_p(tf(dome(0.34, 14, 5), t=(1.05, -0.72, Z + 1.05)), 'green'))
    for z in np.linspace(Z + 1.08, Z + 1.28, 4):
        P.append(_p(tf(torus(0.24, 0.016, 12, 5), t=(1.05, -0.72, z)), 'dark'))
    P.append(_p(tf(box(0.1, 0.28, 0.7), t=(0.78, -0.72, Z + 0.4)), 'dark'))
    # золотая обвязка
    _gold_pipe(P, (rx + 0.3, ry - 0.2, Z + 0.9), (0.95, -0.35, Z + 0.6),
               lift=0.45, r=0.085)
    _gold_pipe(P, (rx + 0.42, ry + 0.15, Z + 0.6), (0.9, 0.35, Z + 0.7),
               lift=0.3, r=0.07)
    P.append(_p(arc_pipe((0.35, -0.9, Z + 0.05), (0.9, -0.5, Z + 0.35),
                         (0, 0, 0.12), 0.05), 'teal'))
    # флагшток с бирюзовым флагом
    fx, fy = -1.32, 0.95
    P.append(_p(tf(cyl(0.022, 1.7, 8), t=(fx, fy, Z + 0.85)), 'silver'))
    P.append(_p(tf(sphere(0.04, 8, 6), t=(fx, fy, Z + 1.72)), 'silver'))
    P.append(_p(tf(box(0.5, 0.025, 0.3), t=(fx + 0.26, fy, Z + 1.5)), 'screen'))
    return merge(P)


def factory(level=0, seed=0):
    """Бетонный цех с пилястрами, 3 полосатые трубы, шаровые баки,
    офисный блок (реф Factory, гекс-плита)."""
    P = []
    Z = _plate(P, 3.5, top='grass', shape='hex')
    # главный цех
    P.append(_p(tf(box(1.55, 1.1, 0.85), t=(-0.45, 0.35, Z + 0.425)), 'conc'))
    for dx in np.linspace(-1.05, 0.15, 6):
        P.append(_p(tf(box(0.1, 1.16, 0.7), t=(dx, 0.35, Z + 0.35)), 'conc_l'))
    P.append(_p(tf(box(1.0, 0.9, 0.28), t=(-0.45, 0.3, Z + 0.99)), 'conc_l'))
    # полосатые трубы на цехе
    for dx, hh in ((-0.85, 1.9), (-0.45, 2.1), (-0.05, 1.75)):
        _striped_chimney(P, dx, 0.55, 0.13, hh, Z + 0.8)
    # шаровые баки на опорах
    for k, (bx, by) in enumerate(((-1.15, -0.75), (-0.6, -1.0),
                                  (-0.05, -0.8), (0.45, -1.05))):
        P.append(_p(tf(cyl(0.05, 0.22, 6), t=(bx, by, Z + 0.11)), 'steel'))
        P.append(_p(tf(sphere(0.27, 14, 9), t=(bx, by, Z + 0.42)), 'silver'))
        P.append(_p(tf(torus(0.27, 0.018, 14, 5), t=(bx, by, Z + 0.42)),
                    'steel'))
    P.append(_p(tube(np.array([(-1.15, -0.75, Z + 0.62),
                               (-0.05, -0.8, Z + 0.62),
                               (0.45, -1.05, Z + 0.62)]), 0.03, 6), 'steel'))
    # офисный блок с остеклением
    P.append(_p(tf(box(1.0, 0.85, 0.75), t=(0.95, 0.55, Z + 0.375)), 'conc_l'))
    P.append(_p(tf(box(1.06, 0.6, 0.14), t=(0.95, 0.55, Z + 0.55)), 'glass'))
    P.append(_p(tf(box(0.5, 0.5, 0.2), t=(0.95, 0.55, Z + 0.85)), 'steel'))
    # низкий склад + печной зев
    P.append(_p(tf(box(0.8, 0.55, 0.4), t=(0.85, -0.5, Z + 0.2)), 'conc_d'))
    P.append(_p(tf(box(0.4, 0.04, 0.2), t=(0.85, -0.79, Z + 0.18)), 'accent'))
    _screens(P, -0.45, -0.22, Z + 0.6, 0.2, 0.14, n=2)
    _mast(P, 1.25, 0.85, Z + 0.95, 0.5)
    return merge(P)


def outpost(level=0, seed=0):
    """Техплатформа: центральный геокупол-оранжерея, солнечное поле,
    тарелка и угловые манипуляторы (реф Outpost)."""
    P = []
    Z = _plate(P, 3.3, top='conc_l')
    # панельная разметка плиты
    for dx in (-0.83, 0.83):
        P.append(_p(tf(box(0.02, 3.05, 0.055), t=(dx, 0, Z - 0.02)), 'plate'))
        P.append(_p(tf(box(3.05, 0.02, 0.055), t=(0, dx, Z - 0.02)), 'plate'))
    # центральный купол
    P.append(_p(tf(cyl(0.98, 0.12, 22), t=(0, 0, Z + 0.06)), 'white'))
    _glassdome(P, 0, 0, 0.9, Z + 0.12)
    rng = np.random.default_rng(seed + 5)
    for _ in range(4):
        x, y = rng.uniform(-0.45, 0.45, 2)
        P.append(_p(tf(sphere(rng.uniform(0.14, 0.24), 9, 6),
                       t=(x, y, Z + 0.14), s=(1, 1, 0.6)), 'green'))
    P.append(_p(tf(box(0.2, 0.3, 0.42), t=(0, -0.95, Z + 0.21)), 'white'))
    P.append(_p(tf(box(0.14, 0.04, 0.2), t=(0, -1.11, Z + 0.2)), 'bglow'))
    # солнечное поле на золотистой площадке
    P.append(_p(tf(box(1.15, 1.0, 0.03), t=(-0.85, -0.95, Z + 0.015)), 'gold'))
    for gx in (-1.2, -0.85, -0.5):
        for gy in (-1.25, -0.95, -0.65):
            P.append(_p(tf(tf(box(0.3, 0.26, 0.02), rx=0.2),
                           t=(gx, gy, Z + 0.06)), 'solar'))
    # тарелка связи
    P.append(_p(tf(cyl(0.3, 0.18, 12), t=(1.05, 0.35, Z + 0.09)), 'white'))
    _dish(P, 1.05, 0.35, Z + 0.24, 0.34, tilt=-PI / 3, rz=PI / 4)
    # угловые манипуляторы
    for cx, cy in ((-1.25, 1.25), (1.25, 1.25), (1.25, -1.25), (-1.25, -0.35)):
        a = math.atan2(-cy, -cx)
        P.append(_p(tf(cyl(0.13, 0.3, 10), t=(cx, cy, Z + 0.15)), 'steel'))
        arm = np.array([(cx, cy, Z + 0.3),
                        (cx + 0.28 * math.cos(a), cy + 0.28 * math.sin(a),
                         Z + 0.62),
                        (cx + 0.55 * math.cos(a), cy + 0.55 * math.sin(a),
                         Z + 0.38)])
        P.append(_p(tube(arm, 0.05, 7), 'white'))
        _beacon(P, cx, cy, Z + 0.68, r=0.035)
    _screens(P, 0.83, -0.9, Z + 0.25, 0.22, 0.15, n=2)
    return merge(P)


def farm(level=0, seed=0):
    """Agriplot: грядки, гроздь стеклянных мини-куполов, серебристые чаны
    и связная мачта (реф Agriplot)."""
    P = []
    Z = _plate(P, 3.3, top='grass')
    # грядки: тёмная почва + ряды зелени
    for px, py, w, l in ((-0.85, 0.3, 1.3, 1.15), (-0.35, -0.95, 1.9, 0.8)):
        P.append(_p(tf(box(w, l, 0.05), t=(px, py, Z + 0.025)), 'soil'))
        nrow = int(l / 0.22)
        for k in range(nrow):
            y = py - l / 2 + (k + 0.5) * l / nrow
            P.append(_p(tf(box(w * 0.9, 0.1, 0.08), t=(px, y, Z + 0.07)),
                        'green'))
    # гроздь стеклянных куполов
    for dx, dy, r in ((-0.35, 0.75, 0.4), (0.15, 0.45, 0.34),
                      (-0.75, 0.9, 0.3), (-0.05, 1.05, 0.28)):
        P.append(_p(tf(cyl(r * 1.05, 0.06, 14), t=(dx, dy, Z + 0.03)), 'white'))
        _glassdome(P, dx, dy, r, Z + 0.06, glass='glass_g', frame='steel')
    # серебристые чаны + малые баки
    _pot_tank(P, 0.75, -0.85, 0.34, 0.42, Z)
    _pot_tank(P, 1.15, -0.35, 0.28, 0.36, Z)
    for tx, ty in ((1.25, 0.3), (1.05, 0.62), (1.35, 0.72)):
        _tank(P, tx, ty, 0.11, 0.4, Z)
    P.append(_p(tube(np.array([(0.75, -0.85, Z + 0.5), (1.05, -0.6, Z + 0.45),
                               (1.15, -0.35, Z + 0.42)]), 0.028, 6), 'steel'))
    # связная мачта на бетонной площадке
    P.append(_p(tf(box(0.55, 0.55, 0.06), t=(0.65, 1.15, Z + 0.03)), 'conc_l'))
    P.append(_p(tf(cyl(0.028, 1.5, 8), t=(0.65, 1.15, Z + 0.81)), 'silver'))
    for zz, ww in ((1.35, 0.3), (1.2, 0.24)):
        P.append(_p(tf(box(0.05, ww, 0.14), t=(0.65, 1.15, Z + zz)), 'dark'))
    _beacon(P, 0.65, 1.15, Z + 1.6)
    return merge(P)


def laboratory(level=0, seed=0):
    """Большая тарелка-радиотелескоп + модульный корпус с синими экранами
    и золотыми рёбрами крыши (реф Laboratory)."""
    P = []
    Z = _plate(P, 3.3, top='grass')
    # пьедестал и тарелка
    P.append(_p(tf(box(0.85, 0.85, 0.5), t=(-0.85, -0.5, Z + 0.25)), 'conc_l'))
    P.append(_p(tf(cyl(0.16, 0.35, 10), t=(-0.85, -0.5, Z + 0.65)), 'steel'))
    _dish(P, -0.85, -0.5, Z + 0.85, 0.72, tilt=-PI / 2.6, rz=-PI / 5)
    P.append(_p(tf(cyl(0.02, 0.5, 6),
                   t=(-0.85 - 0.25, -0.5 - 0.18, Z + 1.15), rx=PI / 5),
                'silver'))
    # модульный корпус: сегменты со скошенной крышей
    for k in range(4):
        y = -0.85 + k * 0.62
        P.append(_p(tf(loft_z([(Z, [(0.55, -0.28), (0.55, 0.28),
                                    (-0.55, 0.28), (-0.55, -0.28)]),
                               (Z + 0.55, [(0.42, -0.22), (0.42, 0.22),
                                           (-0.42, 0.22), (-0.42, -0.22)])]),
                       t=(0.8, y, 0), rz=PI / 2), 'white'))
        P.append(_p(tf(box(0.04, 0.42, 0.3), t=(0.52, y, Z + 0.28)), 'screen'))
        P.append(_p(tf(box(0.3, 0.4, 0.07), t=(0.8, y, Z + 0.58)), 'gold'))
    P.append(_p(tf(box(0.6, 0.5, 0.7), t=(0.8, 1.15, Z + 0.35)), 'conc_l'))
    # две белые мачты
    for mx, my, hh in ((0.0, -0.15, 1.9), (0.25, 0.45, 1.6)):
        P.append(_p(tf(cyl(0.045, hh, 8, r2=0.028), t=(mx, my, Z + hh / 2)),
                    'white'))
        _beacon(P, mx, my, Z + hh + 0.03)
    # площадка-геометка
    P.append(_p(tf(cyl(0.35, 0.05, 7), t=(0.0, 1.25, Z + 0.025)), 'conc_l'))
    return merge(P)


def research_campus(level=0, seed=0):
    """Кампус: большой стеклянный купол на белом цоколе, два малых купола,
    жёлтый реактор во дворе и красные флажки (реф ResearchCampus)."""
    P = []
    Z = _plate(P, 3.4, top='grass')
    # цоколь и главный купол (вытянутый)
    P.append(_p(tf(cyl(1.05, 0.35, 24), t=(0.35, 0.25, Z + 0.175),
                   s=(1.15, 1, 1)), 'white'))
    P.append(_p(tf(box(1.7, 0.06, 0.22), t=(0.35, -0.72, Z + 0.2)), 'glass'))
    g, f = geodome(0.95)
    P.append(_p(tf(g, t=(0.35, 0.25, Z + 0.35), s=(1.15, 1, 0.9)), 'glass'))
    P.append(_p(tf(f, t=(0.35, 0.25, Z + 0.35), s=(1.15, 1, 0.9)), 'silver'))
    # интерьер: белые стойки
    for dx, dy in ((0.0, 0.15), (0.55, 0.4), (0.7, -0.05)):
        P.append(_p(tf(box(0.18, 0.18, 0.4), t=(dx, dy, Z + 0.4)), 'white'))
        P.append(_p(tf(box(0.14, 0.14, 0.06), t=(dx, dy, Z + 0.63)), 'screen'))
    # два малых купола на кольцевых цоколях
    for dx, dy, r in ((-1.15, 0.75, 0.42), (-0.65, -0.95, 0.38)):
        P.append(_p(tf(cyl(r * 1.15, 0.18, 16), t=(dx, dy, Z + 0.09)), 'sand'))
        _glassdome(P, dx, dy, r, Z + 0.18, glass='glass', frame='steel')
    # жёлтый реактор на постаменте во дворе
    P.append(_p(tf(cyl(0.3, 0.1, 8), t=(-0.55, 0.0, Z + 0.05)), 'dark'))
    P.append(_p(tf(box(0.34, 0.34, 0.22), t=(-0.55, 0.0, Z + 0.21)), 'gold'))
    P.append(_p(tf(box(0.38, 0.38, 0.06), t=(-0.55, 0.0, Z + 0.35)), 'dark'))
    P.append(_p(tf(torus(0.3, 0.025, 12, 5), t=(-0.55, 0.0, Z + 0.08)),
                'accent'))
    # красные флажки по дуге
    for a in np.linspace(0.5, 2.2, 5):
        fx, fy = 1.35 * math.cos(a) + 0.2, 1.35 * math.sin(a) - 0.4
        P.append(_p(tf(cyl(0.012, 0.55, 6), t=(fx, fy, Z + 0.275)), 'silver'))
        P.append(_p(tf(box(0.16, 0.015, 0.09), t=(fx + 0.08, fy, Z + 0.48)),
                    'red'))
    # арка входа
    P.append(_p(tf(box(0.12, 0.3, 0.5), t=(-1.25, -0.25, Z + 0.25)), 'conc_l'))
    P.append(_p(tf(box(0.12, 0.3, 0.5), t=(-1.25, 0.25, Z + 0.25)), 'conc_l'))
    P.append(_p(tf(box(0.12, 0.8, 0.14), t=(-1.25, 0.0, Z + 0.57)), 'conc_l'))
    return merge(P)


def megafactory(level=0, seed=0):
    """Industrial Megafacility: стеклянный атриум с вертолётными пятачками,
    цветные колонны-баки, монорельс, полосатые цистерны и парные башни."""
    P = []
    Z = _plate(P, 3.5, top='grass')
    # центральный атриум
    P.append(_p(tf(box(1.7, 0.95, 0.75), t=(0.15, 0.35, Z + 0.375)), 'glass'))
    for dx in np.linspace(-0.6, 0.9, 4):
        P.append(_p(tf(box(0.08, 1.0, 0.78), t=(dx, 0.35, Z + 0.39)), 'white'))
    P.append(_p(tf(box(1.8, 1.05, 0.1), t=(0.15, 0.35, Z + 0.8)), 'white'))
    for hx in (-0.3, 0.55):
        P.append(_p(tf(cyl(0.22, 0.03, 14), t=(hx, 0.35, Z + 0.87)), 'conc_l'))
        P.append(_p(tf(torus(0.22, 0.015, 14, 5), t=(hx, 0.35, Z + 0.88)),
                    'gold'))
    # цветные вертикальные баки
    cols = ('red', 'gold', 'white', 'red', 'teal')
    for k, (bx, by) in enumerate(((-1.25, 0.85), (-1.0, 0.55), (-1.3, 0.25),
                                  (-0.95, 0.05), (-1.25, -0.25))):
        hh = (0.95, 1.2, 0.85, 1.05, 0.9)[k]
        P.append(_p(tf(cyl(0.16, hh, 12), t=(bx, by, Z + hh / 2)), cols[k]))
        P.append(_p(tf(dome(0.16, 12, 4), t=(bx, by, Z + hh)), 'silver'))
    # монорельс: эстакада вокруг баков
    track = np.array([(-1.55, -0.7, Z + 0.55), (-1.55, 0.5, Z + 0.55),
                      (-0.9, 1.15, Z + 0.55), (0.3, 1.15, Z + 0.55)])
    P.append(_p(tube(track, 0.055, 7), 'white'))
    for k in (0, 1, 2, 3):
        x, y = track[k][0], track[k][1]
        P.append(_p(tf(box(0.08, 0.08, 0.55), t=(x, y, Z + 0.275)), 'conc_l'))
    P.append(_p(tf(box(0.3, 0.12, 0.1), t=(-1.55, -0.1, Z + 0.62), rz=PI / 2),
                'teal'))
    # полосатые цистерны
    for tx, ty in ((-0.55, -0.95), (0.1, -1.1), (-1.05, -1.05)):
        P.append(_p(tf(cyl(0.34, 0.5, 16), t=(tx, ty, Z + 0.25)), 'white'))
        P.append(_p(tf(torus(0.34, 0.035, 16, 6), t=(tx, ty, Z + 0.3)), 'blue'))
        P.append(_p(tf(dome(0.34, 16, 5), t=(tx, ty, Z + 0.5)), 'silver'))
    # парные круглые башни
    for bx in (1.1, 1.45):
        for k in range(3):
            P.append(_p(tf(cyl(0.3 - 0.02 * k, 0.75, 14),
                           t=(bx, -0.55, Z + 0.375 + 0.78 * k)), 'white'))
            P.append(_p(tf(box(0.16, 0.62, 0.5),
                           t=(bx, -0.55, Z + 0.45 + 0.78 * k)), 'glass'))
        P.append(_p(tf(cyl(0.3, 0.08, 14), t=(bx, -0.55, Z + 2.36)), 'silver'))
        _mast(P, bx, -0.55, Z + 2.4, 0.35, r=0.012)
    # био-колонны во дворе
    for gx, gy in ((0.65, -0.35), (0.85, -0.1), (0.55, -0.05)):
        P.append(_p(tf(cyl(0.07, 0.5, 8), t=(gx, gy, Z + 0.25)), 'gglow'))
        P.append(_p(tf(dome(0.07, 8, 4), t=(gx, gy, Z + 0.5)), 'silver'))
    _screens(P, 0.15, -0.15, Z + 0.55, 0.24, 0.16, n=2)
    return merge(P)


def habitat(level=0, seed=0):
    """Гигантский геокупол над мини-городом (реф Habitat)."""
    P = []
    Z = _plate(P, 3.4, top='grass')
    P.append(_p(tf(cyl(1.55, 0.1, 28), t=(0, 0, Z + 0.05)), 'white'))
    # город внутри
    rng = np.random.default_rng(seed + 7)
    for _ in range(11):
        a = rng.uniform(0, 2 * PI)
        rr = rng.uniform(0, 0.95)
        x, y = rr * math.cos(a), rr * math.sin(a)
        w = rng.uniform(0.14, 0.3)
        h = rng.uniform(0.25, 0.85) * (1.15 - rr * 0.6)
        tag = ('blue', 'white', 'glass')[rng.integers(0, 3)]
        P.append(_p(tf(box(w, w, h), t=(x, y, Z + 0.1 + h / 2),
                       rz=rng.uniform(0, PI)), tag))
        if h > 0.5:
            P.append(_p(tf(box(w * 0.5, w * 0.5, 0.08),
                           t=(x, y, Z + 0.14 + h), rz=0.3), 'screen'))
    # светящееся ядро-площадь
    P.append(_p(tf(cyl(0.22, 0.04, 12), t=(0, 0, Z + 0.12)), 'bglow'))
    # купол
    _glassdome(P, 0, 0, 1.5, Z + 0.1)
    # шлюз
    P.append(_p(tf(box(0.36, 0.5, 0.34), t=(0, -1.5, Z + 0.17)), 'white'))
    P.append(_p(tf(box(0.22, 0.06, 0.2), t=(0, -1.76, Z + 0.16)), 'bglow'))
    return merge(P)


def hydroponifier(level=0, seed=0):
    """Ряды арочных стеклянных теплиц с цветными культурами, три чана
    и вертикальные стеллажи (реф ArtificalHidroponifier)."""
    P = []
    Z = _plate(P, 3.4, top='sand')
    crops = ('green', 'pink', 'gold', 'green', 'teal', 'green')
    k = 0
    for gy in (0.75, 0.0):
        for gx in (-0.95, -0.15):
            P.append(_p(tf(hbarrel(0.62, 0.62, 0.34), t=(gx, gy, Z)),
                        'glass_g'))
            for fy in (-0.31, 0.31):
                P.append(_p(tf(hbarrel(0.66, 0.05, 0.36), t=(gx, gy + fy, Z)),
                            'silver'))
            P.append(_p(tf(box(0.45, 0.5, 0.12), t=(gx, gy, Z + 0.07)),
                        crops[k]))
            k += 1
    # три больших чана
    for tx, ty, r in ((0.95, -0.15, 0.36), (1.15, 0.55, 0.32),
                      (0.55, 0.6, 0.3)):
        _pot_tank(P, tx, ty, r, 0.5, Z)
        P.append(_p(tf(box(0.12, 0.02, 0.16), t=(tx - r - 0.01, ty, Z + 0.3)),
                    'screen'))
    P.append(_p(arc_pipe((-0.15, 0.0, Z + 0.36), (0.95, -0.15, Z + 0.52),
                         (0, 0, 0.25), 0.045), 'silver'))
    P.append(_p(arc_pipe((-0.15, 0.75, Z + 0.36), (1.15, 0.55, Z + 0.5),
                         (0, 0, 0.3), 0.045), 'silver'))
    # вертикальные стеллажи гидропоники
    for sx, sy in ((-0.15, -0.95), (0.2, -1.05), (-0.5, -1.05)):
        for kk in range(4):
            P.append(_p(tf(box(0.2, 0.2, 0.07),
                           t=(sx, sy, Z + 0.12 + kk * 0.16)), 'green'))
            P.append(_p(tf(box(0.24, 0.24, 0.03),
                           t=(sx, sy, Z + 0.06 + kk * 0.16)), 'teal'))
    # серверный блок с экраном
    P.append(_p(tf(box(0.36, 0.3, 0.5), t=(1.25, -0.85, Z + 0.25)), 'dark'))
    _screens(P, 1.05, -0.85, Z + 0.35, 0.18, 0.14, rz=PI / 2, n=1)
    return merge(P)


def metroplex(level=0, seed=0):
    """Плотный городской квартал: сетка улиц и разноликие небоскрёбы
    (реф Metroplex)."""
    P = []
    Z = _plate(P, 3.5, top='conc_l')
    # улицы
    for d in (-0.85, 0.0, 0.85):
        P.append(_p(tf(box(0.16, 3.2, 0.02), t=(d, 0, Z + 0.01)), 'dark'))
        P.append(_p(tf(box(3.2, 0.16, 0.02), t=(0, d, Z + 0.01)), 'dark'))
    rng = np.random.default_rng(seed + 13)
    tags = ('glass', 'rust', 'sand', 'conc_l', 'blue', 'white')
    cells = [(i, j) for i in range(4) for j in range(4)]
    hmap = {(1, 1): 2.6, (2, 2): 2.2, (1, 2): 1.9, (2, 1): 1.7}
    for i, j in cells:
        x = -1.28 + i * 0.85
        y = -1.28 + j * 0.85
        base_h = hmap.get((i, j), rng.uniform(0.45, 1.4))
        w = rng.uniform(0.4, 0.55)
        tag = tags[rng.integers(0, len(tags))]
        if base_h > 1.8:
            # ступенчатая арт-деко башня
            P.append(_p(tf(frustum(w, w, w * 0.75, w * 0.75, base_h * 0.6,
                                   Z), t=(x, y, 0)), tag))
            P.append(_p(tf(frustum(w * 0.7, w * 0.7, w * 0.5, w * 0.5,
                                   base_h * 0.3, Z + base_h * 0.6),
                           t=(x, y, 0)), tag))
            P.append(_p(tf(box(w * 0.4, w * 0.4, base_h * 0.12),
                           t=(x, y, Z + base_h * 0.96)), 'conc_l'))
            _mast(P, x, y, Z + base_h * 1.02, 0.3, r=0.012, tag='steel')
        else:
            P.append(_p(tf(box(w, w, base_h), t=(x, y, Z + base_h / 2)), tag))
            P.append(_p(tf(box(w * 0.9, w * 0.9, 0.04),
                           t=(x, y, Z + base_h + 0.02)), 'conc_d'))
        # оконная полоса
        if base_h > 0.6 and tag not in ('glass', 'blue'):
            P.append(_p(tf(box(w * 0.8, 0.02, base_h * 0.5),
                           t=(x, y - w / 2 - 0.01, Z + base_h * 0.45)),
                        'glass'))
    return merge(P)


def power_plant(level=0, seed=0):
    """Hyperpower Plant: три градирни, плазменные цилиндры в красной
    ферме-раме и ряд катушечных башен (реф HiperPowerPlant)."""
    P = []
    Z = _plate(P, 3.5, top='grass')
    # градирни по диагонали сзади
    for k, (cx, cy) in enumerate(((-0.65, 0.95), (0.15, 0.75), (0.95, 0.55))):
        P.append(_p(tf(cooling_tower(0.42, 0.27, 0.31, 1.55), t=(cx, cy, Z)),
                    'white'))
        P.append(_p(tf(torus(0.31, 0.025, 18, 6), t=(cx, cy, Z + 1.54)),
                    'silver'))
    # красная ферма-рама с плазменными цилиндрами
    fy = -0.1
    for fx in (-0.95, 0.55):
        P.append(_p(tf(box(0.1, 0.1, 0.75), t=(fx, fy - 0.3, Z + 0.375)),
                    'red'))
        P.append(_p(tf(box(0.1, 0.1, 0.75), t=(fx, fy + 0.3, Z + 0.375)),
                    'red'))
    P.append(_p(tf(box(1.7, 0.75, 0.08), t=(-0.2, fy, Z + 0.78)), 'red'))
    for k in range(3):
        px = -0.75 + k * 0.55
        P.append(_p(tf(tf(cyl(0.24, 0.62, 14), rx=PI / 2),
                       t=(px, fy, Z + 0.55), rz=0.35), 'glass'))
        P.append(_p(tf(tf(cyl(0.13, 0.55, 10), rx=PI / 2),
                       t=(px, fy, Z + 0.55), rz=0.35), 'bglow'))
        for sgn in (-1, 1):
            P.append(_p(tf(dome(0.24, 14, 5),
                           t=(px - sgn * 0.33 * math.sin(0.35),
                              fy + sgn * 0.31 * math.cos(0.35), Z + 0.55),
                           rx=sgn * PI / 2, rz=0.35), 'silver'))
    # катушечные башни спереди
    for k in range(5):
        tx = -1.25 + k * 0.45
        ty = -1.05
        hh = 0.85 + 0.08 * (k % 2)
        P.append(_p(tf(cyl(0.13, hh, 10, r2=0.1), t=(tx, ty, Z + hh / 2)),
                    'copper'))
        P.append(_p(tf(helix_coil(0.15, hh * 0.45, 4, 0.025),
                       t=(tx, ty, Z + hh * 0.55)), 'copper'))
        P.append(_p(tf(box(0.08, 0.04, 0.2), t=(tx, ty - 0.12, Z + hh * 0.4)),
                    'accent'))
        P.append(_p(tf(dome(0.1, 10, 4), t=(tx, ty, Z + hh)), 'silver'))
    # конденсаторный блок с бирюзовой обвязкой
    P.append(_p(tf(box(0.85, 0.6, 0.5), t=(1.2, -0.5, Z + 0.25)), 'silver'))
    P.append(_p(arc_pipe((0.95, -0.25, Z + 0.5), (0.55, -0.1, Z + 0.45),
                         (0, 0, 0.2), 0.045), 'teal'))
    _screens(P, 1.2, -0.81, Z + 0.3, 0.2, 0.14, n=2)
    return merge(P)


def sky_net(level=0, seed=0):
    """Sky Net (без рефа, в стиле core): белая башня с радомом-сферой,
    кольцо тарелок и серверные блоки."""
    P = []
    Z = _plate(P, 3.2, top='conc_l')
    # башня
    P.append(_p(tf(frustum(1.0, 1.0, 0.62, 0.62, 0.55, Z), t=(0, 0, 0)),
                'white'))
    P.append(_p(tf(cyl(0.28, 1.35, 12, r2=0.22), t=(0, 0, Z + 1.22)), 'white'))
    for z in (0.75, 1.05, 1.35):
        P.append(_p(tf(torus(0.27, 0.02, 12, 5), t=(0, 0, Z + z)), 'teal'))
    # радом-сфера
    P.append(_p(tf(sphere(0.42, 18, 11), t=(0, 0, Z + 2.2)), 'white'))
    P.append(_p(tf(torus(0.3, 0.02, 16, 5), t=(0, 0, Z + 2.5)), 'silver'))
    _beacon(P, 0, 0, Z + 2.66)
    # кольцо тарелок на башне
    for a in np.linspace(0, 2 * PI, 3, endpoint=False):
        x, y = 0.45 * math.cos(a), 0.45 * math.sin(a)
        P.append(_p(tube(np.array([(0, 0, Z + 1.55), (x, y, Z + 1.62)]),
                         0.03, 6), 'steel'))
        P.append(_p(tf(dish_mesh(0.26), t=(x, y, Z + 1.62), ry=PI / 2.6,
                       rz=a), 'white'))
    # серверные блоки вокруг
    for k, (bx, by) in enumerate(((-1.05, 0.55), (1.05, 0.45), (0.85, -0.85),
                                  (-0.85, -0.9))):
        P.append(_p(tf(box(0.5, 0.38, 0.42), t=(bx, by, Z + 0.21),
                       rz=0.3 * k), 'dark'))
        P.append(_p(tf(box(0.4, 0.03, 0.2), t=(bx, by - 0.2, Z + 0.22),
                       rz=0.3 * k), 'screen'))
        P.append(_p(arc_pipe((bx, by, Z + 0.42), (bx * 0.35, by * 0.35,
                                                  Z + 0.55),
                             (0, 0, 0.15), 0.025), 'teal'))
    _solar(P, -0.35, 1.15, Z, rz=0.5)
    _solar(P, 0.35, 1.2, Z, rz=-0.4)
    return merge(P)


def eco_booster(level=0, seed=0):
    """Lush Growth Bomb: розовая полузарытая сфера-«семя» с прорастающими
    светящимися ветвями и буйной зеленью (реф LushGrowthBomb)."""
    P = []
    Z = _plate(P, 3.3, top='grass')
    # холм-грунт вокруг семени (купол, основание на плите)
    P.append(_p(tf(dome(1.3, 16, 6), t=(0, 0.15, Z), s=(1, 1, 0.3)), 'sand'))
    # розовая сфера, зарытая на треть (купол с юбкой ниже экватора)
    P.append(_p(tf(dome(0.95, 20, 11, cut=-0.5), t=(0, 0.1, Z + 0.46)),
                'pink'))
    # трещины: тёмные пояса
    P.append(_p(tf(torus(0.9, 0.025, 20, 5), t=(0, 0.1, Z + 0.62), rx=0.5),
                'rust'))
    P.append(_p(tf(torus(0.85, 0.02, 20, 5), t=(0, 0.1, Z + 0.5),
                   rx=-0.4, rz=0.8), 'rust'))
    # светящиеся ветви из вершины
    rng = np.random.default_rng(seed + 17)
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        bend = rng.uniform(0.5, 0.9)
        path = [(0.15 * math.cos(a), 0.1 + 0.15 * math.sin(a), Z + 1.28)]
        for t in (0.35, 0.7, 1.0):
            rr = 0.15 + bend * t
            path.append((rr * math.cos(a + t * 0.8),
                         0.1 + rr * math.sin(a + t * 0.8),
                         Z + 1.28 + 0.75 * t - 0.25 * t * t))
        P.append(_p(tube(np.array(path), 0.045 * (1.2 - 0.5), 6), 'gglow'))
        tip = path[-1]
        P.append(_p(tf(sphere(0.06, 6, 5), t=tip), 'gglow'))
    P.append(_p(tf(cyl(0.06, 0.9, 8, r2=0.02), t=(0, 0.1, Z + 1.7)), 'gglow'))
    # зелень вокруг
    for _ in range(9):
        a = rng.uniform(0, 2 * PI)
        rr = rng.uniform(1.05, 1.45)
        x, y = rr * math.cos(a), 0.15 + rr * math.sin(a) * 0.85
        if abs(x) > 1.55 or abs(y) > 1.55:
            continue
        P.append(_p(tf(sphere(rng.uniform(0.12, 0.24), 8, 6),
                       t=(x, y, Z + 0.05), s=(1, 1, 0.8)), 'green'))
    return merge(P)


def terraforming(level=0, seed=0):
    """Terraforming (без рефа, в стиле core): белая воронка-процессор
    с синим жерлом, золотые контрфорсы и кольцо паровых баков."""
    P = []
    Z = _plate(P, 3.4, top='conc_l')
    P.append(_p(tf(cyl(1.1, 0.4, 20, r2=0.95), t=(0, 0, Z + 0.2)), 'white'))
    funnel = revolve([(0.95, 2.1), (0.85, 2.05), (0.45, 1.35), (0.38, 0.9),
                      (0.45, 0.4)], 20)
    P.append(_p(tf(funnel, t=(0, 0, Z)), 'white'))
    P.append(_p(tf(torus(0.9, 0.05, 20, 7), t=(0, 0, Z + 2.1)), 'silver'))
    P.append(_p(tf(cyl(0.78, 0.06, 18), t=(0, 0, Z + 2.0)), 'bglow'))
    # золотые контрфорсы
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        x0, y0 = 1.25 * math.cos(a), 1.25 * math.sin(a)
        x1, y1 = 0.55 * math.cos(a), 0.55 * math.sin(a)
        P.append(_p(tube(np.array([(x0, y0, Z + 0.1),
                                   (x0 * 0.9, y0 * 0.9, Z + 1.2),
                                   (x1, y1, Z + 1.85)]), 0.08, 8), 'gold'))
    # кольцо паровых баков
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        x, y = 1.3 * math.cos(a), 1.3 * math.sin(a)
        _tank(P, x, y, 0.14, 0.6, Z)
    _screens(P, 0, -1.02, Z + 0.45, 0.24, 0.16, n=3)
    _beacon(P, 0.92, 0, Z + 2.18)
    _beacon(P, -0.92, 0, Z + 2.18)
    return merge(P)


# ==================================================== спецпозиции по рефам

def engineering_retreat(level=0, seed=0):
    """Кольцевая белая станция с центральным садовым куполом
    (реф EngineeringRetreat)."""
    P = []
    Z = _plate(P, 3.4, top=None, shape='round')
    P.append(_p(tf(cyl(1.7, 0.28, 28), t=(0, 0, 0.14)), 'dark'))
    P.append(_p(tf(cyl(1.62, 0.06, 28), t=(0, 0, 0.31)), 'conc_l'))
    Z = 0.34
    # внешнее кольцо-коридор из сегментов
    for k, vf in enumerate(box_ring(1.35, 14, 0.34, 0.52, 0.28, z=Z + 0.14)):
        P.append(_p(vf, 'white' if k % 2 == 0 else 'conc_l'))
    for a in np.linspace(0, 2 * PI, 7, endpoint=False):
        x, y = 1.35 * math.cos(a), 1.35 * math.sin(a)
        P.append(_p(tf(box(0.1, 0.32, 0.06), t=(x, y, Z + 0.31), rz=a),
                    'dark'))
    # центральный хаб с садовым куполом
    P.append(_p(tf(cyl(0.78, 0.35, 20, r2=0.68), t=(0, 0, Z + 0.175)),
                'white'))
    P.append(_p(tf(torus(0.72, 0.025, 20, 6), t=(0, 0, Z + 0.36)), 'silver'))
    rng = np.random.default_rng(seed + 23)
    for _ in range(5):
        a = rng.uniform(0, 2 * PI)
        rr = rng.uniform(0, 0.38)
        P.append(_p(tf(sphere(rng.uniform(0.12, 0.2), 8, 6),
                       t=(rr * math.cos(a), rr * math.sin(a), Z + 0.38),
                       s=(1, 1, 0.7)), 'green'))
    g, f = geodome(0.62)
    P.append(_p(tf(g, t=(0, 0, Z + 0.37)), 'glass'))
    P.append(_p(tf(f, t=(0, 0, Z + 0.37)), 'silver'))
    # жёлтые сервисные модули и солнечные панели на внутреннем дворе
    for a in (0.6, 2.1, 3.9, 5.2):
        x, y = 0.95 * math.cos(a), 0.95 * math.sin(a)
        P.append(_p(tf(box(0.18, 0.14, 0.14), t=(x, y, Z + 0.07), rz=a),
                    'gold'))
    _solar(P, 0.95 * math.cos(4.6), 0.95 * math.sin(4.6), Z, w=0.26, l=0.3)
    # четыре шлюза-аппарели по периметру
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        x, y = 1.72 * math.cos(a), 1.72 * math.sin(a)
        P.append(_p(tf(box(0.3, 0.24, 0.18), t=(x, y, 0.23), rz=a), 'white'))
        P.append(_p(tf(box(0.2, 0.03, 0.1), t=(x * 1.06, y * 1.06, 0.2),
                       rz=a), 'accent'))
    _beacon(P, 0, 0, Z + 1.03)
    return merge(P)


def surface_shield(level=0, seed=0):
    """Surface Shield: белая турель с двумя веерами красно-оранжевых
    ракетных сот + ряды стеклянных конденсаторов (реф SurfaceShield)."""
    P = []
    Z = _plate(P, 3.3, top='ygreen')
    # пьедестал турели
    tx, ty = -0.7, 0.55
    P.append(_p(tf(frustum(0.95, 0.95, 0.6, 0.6, 0.45, Z), t=(tx, ty, 0)),
                'white'))
    P.append(_p(tf(cyl(0.3, 0.25, 12), t=(tx, ty, Z + 0.57)), 'conc_l'))
    # два веерных пода с сотами ракет (V-образно вверх-в стороны)
    for sgn in (-1, 1):
        d = np.array([sgn * 0.6, -0.15, 0.8])
        d /= np.linalg.norm(d)
        u1 = np.cross(d, np.array([0, 0, 1.0]))
        u1 /= np.linalg.norm(u1)
        u2 = np.cross(u1, d)
        hc = np.array([tx + sgn * 0.34, ty - 0.03, Z + 0.98])
        P.append(_p(tf(tf(box(0.46, 0.34, 0.6), rx=-0.25, ry=sgn * 0.55),
                       t=tuple(hc)), 'white'))
        for ha, hb in ((0, 0), (1, 0), (-1, 0), (0.5, 0.87), (-0.5, 0.87),
                       (0.5, -0.87), (-0.5, -0.87)):
            base = hc + u1 * ha * 0.145 + u2 * hb * 0.145 + d * 0.12
            tip = base + d * 0.5
            P.append(_p(tube(np.array([base, tip]), 0.062, 8), 'red'))
            P.append(_p(tf(sphere(0.058, 8, 5), t=tuple(tip)), 'accent'))
    # белые плавники между подами
    for da in (-1, 1):
        P.append(_p(tf(tf(box(0.04, 0.26, 0.6), rx=-0.2, ry=da * 0.18),
                       t=(tx + da * 0.1, ty, Z + 1.3)), 'white'))
    # конденсаторные контейнеры: 2 ряда по 3
    for row, cy in enumerate((-0.35, -1.0)):
        for k in range(3):
            cx = 0.05 + k * 0.75
            P.append(_p(tf(box(0.6, 0.42, 0.1), t=(cx, cy, Z + 0.05)),
                        'dark'))
            P.append(_p(tf(box(0.52, 0.34, 0.3), t=(cx, cy, Z + 0.25)),
                        'glass'))
            core = 'bglow' if (row + k) % 3 == 0 else 'gglow'
            P.append(_p(tf(cyl(0.07, 0.4, 8), t=(cx, cy, Z + 0.24),
                           ry=PI / 2), core))
    P.append(_p(tube(np.array([(-0.25, 0.3, Z + 0.02), (0.05, -0.35, Z + 0.02),
                               (0.05, -1.0, Z + 0.02)]), 0.025, 6), 'rust'))
    _screens(P, -1.2, -0.3, Z + 0.25, 0.2, 0.14, n=1)
    return merge(P)


def surface_mega_shield(level=0, seed=0):
    """Surface Megashield: наклонный золотой мегаэмиттер со спаркой красных
    стволов + поле батарейных блоков, сфера и тарелка (реф SurfaceMegaShield)."""
    P = []
    Z = _plate(P, 3.5, top='ygreen')
    # основание-клин и наклонный барабан эмиттера
    P.append(_p(tf(loft_z([(Z, [(0.95, -0.8), (0.95, 0.8), (-0.6, 0.55),
                                (-0.6, -0.55)]),
                           (Z + 0.75, [(0.7, -0.45), (0.75, 0.45),
                                       (-0.3, 0.35), (-0.3, -0.35)])]),
                   t=(0.55, -0.1, 0)), 'blue'))
    # ось эмиттера: наклон ~45° вверх-вправо
    ax = np.array([0.62, 0.32, 0.72])
    ax /= np.linalg.norm(ax)
    polar = math.acos(ax[2])
    yaw = math.atan2(ax[1], ax[0])
    c0 = np.array([0.2, -0.25, Z + 0.85])
    for k, (rr, ll, tag) in enumerate(((0.55, 0.28, 'sand'),
                                       (0.5, 0.24, 'gold'),
                                       (0.44, 0.22, 'white'),
                                       (0.38, 0.18, 'gold'))):
        cc = c0 + ax * (0.26 * k)
        P.append(_p(tf(tf(cyl(rr, ll, 18), ry=polar, rz=yaw), t=tuple(cc)),
                    tag))
    # спарка красных стволов
    u1 = np.cross(ax, np.array([0, 0, 1.0]))
    u1 /= np.linalg.norm(u1)
    top = c0 + ax * 0.95
    for off in (-1, 1):
        b0 = top + u1 * off * 0.17
        b1 = b0 + ax * 0.75
        P.append(_p(tube(np.array([b0, b1]), 0.14, 12), 'red'))
        P.append(_p(tf(tf(torus(0.15, 0.02, 12, 5), ry=polar, rz=yaw),
                       t=tuple(b0 * 0.4 + b1 * 0.6)), 'silver'))
        P.append(_p(tf(tf(cyl(0.16, 0.1, 12), ry=polar, rz=yaw),
                       t=tuple(b1)), 'silver'))
        P.append(_p(tf(tf(cyl(0.09, 0.05, 10), ry=polar, rz=yaw),
                       t=tuple(b1 + ax * 0.06)), 'accent'))
    # поле батарейных блоков слева
    rng = np.random.default_rng(seed + 29)
    for i in range(3):
        for j in range(4):
            bx = -1.25 + i * 0.42
            by = -1.05 + j * 0.6
            hh = rng.uniform(0.22, 0.38)
            tag = ('green', 'teal', 'dgreen')[rng.integers(0, 3)]
            P.append(_p(tf(box(0.34, 0.46, hh), t=(bx, by, Z + hh / 2)), tag))
            P.append(_p(tf(tf(cyl(0.035, 0.3, 6), rx=PI / 2),
                           t=(bx, by - 0.1, Z + hh + 0.04)), 'gglow'))
    # серебристая сфера на постаменте + тарелка
    P.append(_p(tf(cyl(0.28, 0.35, 12, r2=0.24), t=(-1.05, 1.15, Z + 0.175)),
                'dark'))
    P.append(_p(tf(sphere(0.38, 16, 10), t=(-1.05, 1.15, Z + 0.72)), 'silver'))
    P.append(_p(tf(cyl(0.015, 0.35, 6), t=(-1.05, 1.15, Z + 1.2)), 'steel'))
    P.append(_p(tf(box(0.5, 0.4, 0.35), t=(0.15, 1.15, Z + 0.175)), 'dgreen'))
    _dish(P, 0.35, 1.3, Z + 0.4, 0.3, tilt=-PI / 3.2, rz=2.2)
    # оливковые контейнеры у эмиттера
    P.append(_p(tf(box(0.6, 0.4, 0.35), t=(0.45, -1.15, Z + 0.175), rz=0.2),
                'dgreen'))
    P.append(_p(tf(box(0.5, 0.3, 0.28), t=(1.15, 0.85, Z + 0.14), rz=-0.3),
                'green'))
    return merge(P)


def alien_ruins(level=0, seed=0):
    """Alien Ruins: гравированная золотая плита, тёмные рунные монолиты,
    расколотая чёрно-серебристая сфера и упавшие артефакты (реф AlienRuins)."""
    P = []
    # золотая плита с тёмным рантом
    P.append(_p(tf(box(3.3, 3.3, 0.16), t=(0, 0, 0.08)), 'rust'))
    P.append(_p(tf(box(3.1, 3.1, 0.07), t=(0, 0, 0.2)), 'gold'))
    Z = 0.235
    # песчаные наплывы
    rng = np.random.default_rng(seed + 31)
    for _ in range(6):
        x, y = rng.uniform(-1.2, 1.2, 2)
        P.append(_p(tf(sphere(rng.uniform(0.2, 0.45), 9, 6),
                       t=(x, y, Z - 0.05), s=(1.3, 1, 0.35)), 'sand'))
    # рунные монолиты: наклонные стопки гекс-призм
    stacks = [(-1.05, 0.85, 3, 0.3), (-0.45, 1.05, 2, 0.26),
              (-1.2, -0.35, 2, 0.28), (0.15, 0.85, 3, 0.24),
              (-0.55, 0.15, 1, 0.3)]
    for sx, sy, n, r in stacks:
        lean_x = rng.uniform(-0.12, 0.12)
        for k in range(n):
            hh = rng.uniform(0.3, 0.42)
            P.append(_p(tf(ngon_prism(r * (1 - 0.08 * k), hh, 6),
                           t=(sx + lean_x * k, sy + lean_x * k * 0.5,
                              Z + (0.36 * k) + hh / 2),
                           rz=rng.uniform(0, PI), ry=lean_x * 0.6), 'dark'))
        # рунные блики
        P.append(_p(tf(box(0.05, 0.05, 0.05),
                       t=(sx + 0.02, sy - r, Z + 0.3)), 'gglow'))
    # расколотая сфера: тёмный шар + серебристые пластины
    P.append(_p(tf(sphere(0.7, 18, 11), t=(0.85, -0.35, Z + 0.45)), 'graph'))
    for (ra, rb) in ((0.3, 0.9), (1.4, 0.4), (2.4, 1.2)):
        patch = dome(0.72, 10, 4, cut=1.05)
        P.append(_p(tf(patch, t=(0.85, -0.35, Z + 0.45), rx=rb, rz=ra),
                    'silver'))
    # упавшие жезлы-артефакты с бирюзовыми кристаллами
    for (x0, y0, x1, y1) in ((-0.85, -0.85, -0.15, -1.05),
                             (-0.15, -0.55, 0.45, -0.95)):
        P.append(_p(tube(np.array([(x0, y0, Z + 0.06), (x1, y1, Z + 0.12)]),
                         0.045, 7), 'steel'))
        P.append(_p(tf(octahedron(0.09, 1.6), t=(x1, y1, Z + 0.14),
                       ry=PI / 2.2), 'bglow'))
    # шестерни
    for gx, gy, gr in ((0.1, -0.25, 0.16), (0.35, -0.05, 0.11)):
        P.append(_p(tf(torus(gr, 0.035, 10, 5), t=(gx, gy, Z + 0.04)), 'rust'))
    return merge(P)


# ==================================================== орбитальные (без плит)
# Конвенции как у humans: центр конструкции ~z=1.0, «рабочее» направление
# орудий +Y, габарит растёт с уровнем. Рефы: OrbitalDocks/OrbitalShipyard
# (доки), OrbitalShield_1..3 (щиты: парные купола-клетки), OrbitalLaser
# (лазер: модульная платформа с фиолетовой линзой), вариант с плазменными
# трубами (фазер) и OrbitalMissileBase (скорострельный: кассеты красных
# ракет с золотыми БЧ).

def _cone(r, h, seg=10):
    return cyl(r, h, seg, r2=1e-4)


def _rails(P, s, zc, length, dz=0.34, tag='silver'):
    """Верхние монтажные рельсы на стойках (реф OrbitalLaser)."""
    for dx in (-0.16 * s, 0.16 * s):
        P.append(_p(tf(box(0.07 * s, length, 0.05 * s),
                       t=(dx, 0, zc + dz * s)), tag))
    for dy in (-length * 0.38, 0, length * 0.38):
        P.append(_p(tf(box(0.04 * s, 0.04 * s, 0.14 * s),
                       t=(0, dy, zc + (dz - 0.09) * s)), 'steel'))
    P.append(_p(tf(box(0.42 * s, 0.3 * s, 0.03 * s),
                   t=(0, -length * 0.2, zc + (dz + 0.03) * s)), 'solar'))


def orb_dock(level=1, seed=0):
    """Серый многоярусный док-эстакада: палуба с солнечным настилом,
    кормовая надстройка, жёлтые цистерны и шаровые баки (реф OrbitalDocks)."""
    P = []
    s = 0.6 + 0.17 * level
    zc = 1.0
    # главная палуба
    P.append(_p(tf(box(1.7 * s, 1.15 * s, 0.12 * s), t=(0, 0.2 * s, zc)),
                'conc'))
    for gx in np.linspace(-0.62 * s, 0.62 * s, 4):
        for gy in np.linspace(-0.1 * s, 0.55 * s, 3):
            P.append(_p(tf(box(0.27 * s, 0.19 * s, 0.025 * s),
                           t=(gx, gy, zc + 0.07 * s)), 'solar'))
    # причальные тумбы по кромке палубы
    for gx in np.linspace(-0.75 * s, 0.75 * s, 5):
        P.append(_p(tf(box(0.09 * s, 0.12 * s, 0.22 * s),
                       t=(gx, 0.72 * s, zc + 0.14 * s)), 'conc_d'))
        _beacon(P, gx, 0.72 * s, zc + 0.28 * s, r=0.025 * s)
    # кормовая многоярусная надстройка на фермах
    decks = 2 + (level >= 3)
    for k in range(decks):
        z = zc + (0.3 + 0.32 * k) * s
        P.append(_p(tf(box((1.55 - 0.18 * k) * s, 0.6 * s, 0.09 * s),
                       t=(0, -0.5 * s, z)), 'conc_l' if k % 2 else 'conc'))
    for dx in (-0.62 * s, 0.0, 0.62 * s):
        hh = (0.3 + 0.32 * (decks - 1)) * s
        P.append(_p(tf(box(0.08 * s, 0.5 * s, hh),
                       t=(dx, -0.5 * s, zc + hh / 2 + 0.05 * s)), 'steel'))
    # техблоки на ярусах
    rng = np.random.default_rng(seed + 41 + level)
    for _ in range(3 + level):
        k = rng.integers(0, decks)
        z = zc + (0.3 + 0.32 * k) * s + 0.09 * s
        P.append(_p(tf(box(rng.uniform(0.14, 0.3) * s,
                           rng.uniform(0.12, 0.25) * s,
                           rng.uniform(0.1, 0.2) * s),
                       t=(rng.uniform(-0.6, 0.6) * s, -0.5 * s, z)),
                    ('conc_d', 'rust', 'dark')[rng.integers(0, 3)]))
    # жёлтые цистерны сбоку
    for k in range(min(2 + level // 2, 3)):
        ty = 0.15 * s - 0.32 * s * k
        P.append(_p(tf(tf(cyl(0.16 * s, 0.6 * s, 12), rx=PI / 2),
                       t=(-0.98 * s, ty, zc + 0.22 * s)), 'gold'))
        P.append(_p(tf(sphere(0.16 * s, 10, 7),
                       t=(-0.98 * s, ty + 0.3 * s, zc + 0.22 * s)), 'sand'))
    # шаровые баки под палубой
    for gx in np.linspace(-0.5 * s, 0.5 * s, 3 + (level >= 2)):
        P.append(_p(tf(sphere(0.14 * s, 10, 7),
                       t=(gx, 0.35 * s, zc - 0.2 * s)), 'silver'))
    if level >= 4:  # крыло-пристройка huge-дока
        P.append(_p(tf(box(0.5 * s, 1.0 * s, 0.1 * s),
                       t=(1.05 * s, -0.2 * s, zc + 0.45 * s)), 'conc_l'))
        P.append(_p(tf(box(0.08 * s, 0.08 * s, 0.45 * s),
                       t=(1.05 * s, -0.2 * s, zc + 0.22 * s)), 'steel'))
        for gy in (-0.5 * s, 0.1 * s):
            P.append(_p(tf(box(0.4 * s, 0.16 * s, 0.03 * s),
                           t=(1.05 * s, gy, zc + 0.52 * s)), 'solar'))
    _beacon(P, 0, -0.5 * s, zc + (0.3 + 0.32 * (decks - 1)) * s + 0.12 * s,
            r=0.03 * s)
    return merge(P)


def orb_shield(level=1, seed=0):
    """Щит: зелёная платформа с рядом красных куполов-линз и парой
    геокуполов-клеток с синими ядрами (рефы OrbitalShield_1..3)."""
    P = []
    s = 0.72 + 0.15 * level
    zc = 0.85
    # платформа
    P.append(_p(tf(box(1.5 * s, 1.0 * s, 0.22 * s), t=(0, 0, zc)), 'green'))
    P.append(_p(tf(box(1.6 * s, 0.75 * s, 0.1 * s), t=(0, 0, zc - 0.14 * s)),
                'dgreen'))
    # тёмная ферма снизу
    m = lattice_mast(0.9 * s, 0.55 * s, 0.38 * s, bays=2, r=0.016 * s,
                     z0=zc - 0.55 * s)
    P.append(_p(m, 'dark'))
    # передний рельс с красными куполами-линзами
    P.append(_p(tf(box(1.5 * s, 0.2 * s, 0.08 * s),
                   t=(0, 0.52 * s, zc + 0.15 * s)), 'conc_d'))
    for gx in np.linspace(-0.6 * s, 0.6 * s, 3 + level):
        P.append(_p(tf(dome(0.07 * s, 10, 4), t=(gx, 0.52 * s, zc + 0.19 * s)),
                    'red'))
    # пара куполов-клеток с синими ядрами
    r = (0.34 + 0.04 * level) * s
    for dx in (-0.38 * s, 0.38 * s):
        P.append(_p(tf(cyl(r * 0.9, 0.08 * s, 14),
                       t=(dx, -0.08 * s, zc + 0.15 * s)), 'dgreen'))
        P.append(_p(tf(sphere(r * 0.72, 12, 8),
                       t=(dx, -0.08 * s, zc + 0.2 * s + r * 0.45)), 'bglow'))
        _, cage = geodome(r)
        P.append(_p(tf(cage, t=(dx, -0.08 * s, zc + 0.19 * s)), 'ygreen'))
    # жёлто-зелёные кристаллы вокруг куполов
    rng = np.random.default_rng(seed + 47 + level)
    for _ in range(4 + 2 * level):
        gx = rng.uniform(-0.7, 0.7) * s
        gy = rng.uniform(-0.42, 0.3) * s
        hh = rng.uniform(0.12, 0.3) * s
        P.append(_p(tf(box(0.05 * s, 0.05 * s, hh),
                       t=(gx, gy, zc + 0.11 * s + hh / 2), rz=rng.uniform(0, PI)),
                    'gglow'))
    _beacon(P, -0.75 * s, 0, zc + 0.15 * s, r=0.03 * s)
    _beacon(P, 0.75 * s, 0, zc + 0.15 * s, r=0.03 * s)
    return merge(P)


def orb_laser(level=1, seed=0):
    """Лазер: модульная горизонтальная платформа, фиолетовая линза в +Y,
    белый шар-бак с кормы (реф OrbitalLaser, левый вариант)."""
    P = []
    s = 0.72 + 0.14 * level
    zc = 1.0
    # модули корпуса вдоль Y
    for k in range(3):
        y = -0.35 * s + k * 0.35 * s
        P.append(_p(tf(box(0.55 * s, 0.3 * s, 0.5 * s), t=(0, y, zc)),
                    'blue' if k % 2 else 'teal'))
        P.append(_p(tf(box(0.58 * s, 0.06 * s, 0.36 * s),
                       t=(0, y - 0.14 * s, zc)), 'dark'))
        P.append(_p(tf(box(0.04 * s, 0.16 * s, 0.16 * s),
                       t=(0.28 * s, y, zc + 0.06 * s)), 'gglow'))
    # коричневые подвесные блоки
    for dy in (-0.3 * s, 0.15 * s):
        P.append(_p(tf(box(0.4 * s, 0.34 * s, 0.16 * s),
                       t=(-0.2 * s, dy, zc - 0.36 * s)), 'rust'))
    _rails(P, s, zc, 1.3 * s)
    # кормовой шар-бак
    P.append(_p(tf(sphere(0.27 * s, 14, 9), t=(0, -0.75 * s, zc - 0.05 * s)),
                'white'))
    P.append(_p(tf(torus(0.27 * s, 0.02 * s, 14, 5),
                   t=(0, -0.75 * s, zc - 0.05 * s), rx=PI / 2), 'steel'))
    # орудийный блок с фиолетовой линзой
    P.append(_p(tf(tf(cyl(0.15 * s, 0.3 * s, 12), rx=PI / 2),
                   t=(0, 0.62 * s, zc)), 'dark'))
    for k in range(level):
        P.append(_p(tf(torus(0.16 * s, 0.018 * s, 12, 5),
                       t=(0, (0.55 + 0.09 * k) * s, zc), rx=PI / 2), 'silver'))
    P.append(_p(tf(tf(cyl(0.11 * s, 0.05 * s, 12), rx=PI / 2),
                   t=(0, 0.79 * s, zc)), 'pglow'))
    _beacon(P, 0, -0.9 * s, zc + 0.1 * s, r=0.028 * s)
    return merge(P)


def orb_phazer(level=1, seed=0):
    """Фазер: та же семья, но с плазменными трубами-ускорителями по бокам
    и роторным дулом (реф OrbitalLaser, правый вариант)."""
    P = []
    s = 0.75 + 0.14 * level
    zc = 1.0
    # центральная спина
    P.append(_p(tf(box(0.34 * s, 1.15 * s, 0.42 * s), t=(0, -0.05 * s, zc)),
                'teal'))
    P.append(_p(tf(box(0.38 * s, 0.3 * s, 0.5 * s), t=(0, -0.45 * s, zc)),
                'blue'))
    P.append(_p(tf(box(0.04 * s, 0.5 * s, 0.14 * s),
                   t=(0.18 * s, -0.05 * s, zc + 0.1 * s)), 'gglow'))
    # плазменные трубы (1+level//2 пары)
    pairs = 1 + (level - 1) // 2
    for k in range(pairs):
        dz = (0.14 - 0.28 * k) * s if pairs > 1 else 0.0
        for sgn in (-1, 1):
            c = (sgn * 0.3 * s, 0.05 * s, zc + dz)
            P.append(_p(tf(tf(cyl(0.13 * s, 0.6 * s, 12), rx=PI / 2), t=c),
                        'glass'))
            P.append(_p(tf(tf(cyl(0.07 * s, 0.55 * s, 8), rx=PI / 2), t=c),
                        'pglow'))
            for dy in (-0.22 * s, 0.0, 0.22 * s):
                P.append(_p(tf(torus(0.14 * s, 0.02 * s, 12, 5),
                               t=(c[0], c[1] + dy, c[2]), rx=PI / 2),
                            'silver'))
    _rails(P, s, zc, 1.25 * s)
    # роторное дуло
    P.append(_p(tf(tf(cyl(0.17 * s, 0.28 * s, 14), rx=PI / 2),
                   t=(0, 0.6 * s, zc)), 'dark'))
    P.append(_p(tf(tf(cyl(0.19 * s, 0.08 * s, 14), rx=PI / 2),
                   t=(0, 0.5 * s, zc)), 'steel'))
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        P.append(_p(tf(tf(cyl(0.035 * s, 0.1 * s, 6), rx=PI / 2),
                       t=(0.1 * s * math.cos(a), 0.76 * s,
                          zc + 0.1 * s * math.sin(a))), 'pglow'))
    # кормовой шар
    P.append(_p(tf(sphere(0.3 * s, 14, 9), t=(0, -0.72 * s, zc - 0.04 * s)),
                'white'))
    _beacon(P, 0, -0.9 * s, zc + 0.12 * s, r=0.028 * s)
    return merge(P)


def orb_phazer_rapid(level=1, seed=0):
    """Скорострельный: кассеты красных ракет с золотыми БЧ в +Y на общей
    раме, белый шар-бак с кормы (реф OrbitalMissileBase)."""
    P = []
    s = 0.8 + 0.13 * level
    zc = 1.0
    # рама-корпус
    P.append(_p(tf(box(0.6 * s, 1.0 * s, 0.34 * s), t=(0, -0.1 * s, zc)),
                'teal'))
    P.append(_p(tf(box(0.66 * s, 0.24 * s, 0.42 * s), t=(0, -0.55 * s, zc)),
                'blue'))
    P.append(_p(tf(box(0.5 * s, 0.4 * s, 0.14 * s),
                   t=(0, -0.15 * s, zc - 0.28 * s)), 'rust'))
    _rails(P, s, zc, 1.15 * s, dz=0.3)
    # кассеты ракет: rows x cols по уровню
    rows, cols = 2 + level, 3 + level
    for r_i in range(rows):
        for c_i in range(cols):
            x = (c_i - (cols - 1) / 2) * 0.155 * s
            z = zc + (r_i - (rows - 1) / 2) * 0.155 * s
            y0 = 0.28 * s + 0.04 * s * ((r_i + c_i) % 2)
            P.append(_p(tf(tf(cyl(0.055 * s, 0.55 * s, 9), rx=PI / 2),
                           t=(x, y0, z)), 'red'))
            P.append(_p(tf(tf(_cone(0.05 * s, 0.14 * s, 9), rx=PI / 2),
                           t=(x, y0 + 0.33 * s, z)), 'gold'))
    # стяжные пояса кассеты
    for z in (zc - 0.12 * s, zc + 0.12 * s):
        P.append(_p(tf(box(cols * 0.16 * s, 0.05 * s, 0.03 * s),
                       t=(0, 0.3 * s, z)), 'dark'))
    # кормовой шар
    P.append(_p(tf(sphere(0.28 * s, 14, 9), t=(0, -0.78 * s, zc)), 'white'))
    P.append(_p(tf(torus(0.28 * s, 0.02 * s, 14, 5), t=(0, -0.78 * s, zc),
                   rx=PI / 2), 'steel'))
    _beacon(P, 0.35 * s, -0.55 * s, zc + 0.28 * s, r=0.028 * s)
    return merge(P)


# ============================================================ пропсы

def prop_blocks(variant=1, seed=0):
    """Хаотичные контейнеры в палитре core."""
    P = []
    tags = ('white', 'silver', 'teal', 'dark', 'gold')
    boxes = scatter_boxes(seed + variant * 19, 6 + variant * 2, 0.5,
                          0.14, 0.34, hmax=0.26)
    for k, vf in enumerate(boxes):
        P.append(_p(vf, tags[k % len(tags)]))
    return merge(P)


def prop_tanks(level=0, seed=0):
    """Группа серебристых чанов и баков."""
    P = []
    _pot_tank(P, -0.25, 0.1, 0.22, 0.32, 0.0)
    _pot_tank(P, 0.15, -0.2, 0.17, 0.26, 0.0)
    for tx, ty in ((0.3, 0.25), (0.48, 0.05)):
        _tank(P, tx, ty, 0.09, 0.34, 0.0)
    P.append(_p(tube(np.array([(-0.25, 0.1, 0.38), (0.3, 0.25, 0.36)]),
                     0.02, 6), 'steel'))
    P.append(_p(tf(box(0.1, 0.02, 0.12), t=(-0.48, 0.1, 0.18)), 'screen'))
    return merge(P)


def prop_pipes(level=0, seed=0):
    """Золотая труба на опорах с вентилем и бирюзовым отводом."""
    P = []
    path = np.array([(-0.55, -0.08, 0.16), (-0.15, -0.08, 0.16),
                     (0.1, 0.02, 0.16), (0.4, 0.1, 0.16), (0.4, 0.1, 0.38),
                     (0.6, 0.14, 0.38)])
    P.append(_p(tube(path, 0.05, 8), 'gold'))
    for x, y in ((-0.4, -0.08), (0.15, 0.03)):
        P.append(_p(tf(box(0.07, 0.07, 0.12), t=(x, y, 0.055)), 'white'))
    P.append(_p(tf(sphere(0.06, 8, 6), t=(0.1, 0.02, 0.22)), 'silver'))
    P.append(_p(tf(cyl(0.014, 0.09, 6), t=(0.1, 0.02, 0.3)), 'red'))
    P.append(_p(arc_pipe((-0.35, -0.08, 0.2), (-0.5, 0.3, 0.05),
                         (0, 0, 0.12), 0.03), 'teal'))
    return merge(P)


def prop_mast(level=0, seed=0):
    """Белая мачта с тарелкой, панелью и аппаратным боксом."""
    P = []
    P.append(_p(tf(cyl(0.05, 1.1, 8, r2=0.03), t=(0, 0, 0.55)), 'white'))
    for z, w in ((0.85, 0.3), (0.7, 0.22)):
        P.append(_p(tf(box(0.04, w, 0.1), t=(0, 0, z)), 'dark'))
    P.append(_p(tf(dish_mesh(0.13), t=(0.07, 0.07, 0.95), rx=-PI / 3,
                   rz=PI / 4), 'white'))
    P.append(_p(tf(box(0.2, 0.16, 0.16), t=(0.22, -0.12, 0.08)), 'silver'))
    _solar(P, -0.22, 0.14, 0.0, w=0.22, l=0.26, rz=0.6)
    _beacon(P, 0, 0, 1.14)
    return merge(P)


def prop_pad(level=0, seed=0):
    """Посадочный пятачок с маркировкой и огнями."""
    P = []
    P.append(_p(tf(cyl(0.6, 0.07, 20), t=(0, 0, 0.035)), 'plate'))
    P.append(_p(tf(cyl(0.48, 0.02, 20), t=(0, 0, 0.08)), 'conc_l'))
    P.append(_p(tf(torus(0.44, 0.015, 20, 5), t=(0, 0, 0.09)), 'gold'))
    P.append(_p(tf(box(0.05, 0.3, 0.015), t=(-0.08, 0, 0.095)), 'white'))
    P.append(_p(tf(box(0.05, 0.3, 0.015), t=(0.08, 0, 0.095)), 'white'))
    P.append(_p(tf(box(0.21, 0.05, 0.015), t=(0, 0, 0.095)), 'white'))
    for a in np.linspace(PI / 6, 2 * PI, 6, endpoint=False):
        P.append(_p(tf(sphere(0.024, 6, 5),
                       t=(0.54 * math.cos(a), 0.54 * math.sin(a), 0.085)),
                    'accent'))
    P.append(_p(tf(box(0.14, 0.16, 0.14), t=(0.6, 0.32, 0.07)), 'white'))
    _beacon(P, 0.6, 0.32, 0.17, r=0.022)
    return merge(P)
