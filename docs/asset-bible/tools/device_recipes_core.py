# Рецепты устройств CORE v3 — «настольные приборы» по обновлённым
# референсам refs/devices/core (стилизация под иконки Ascendancy 1995:
# каждый гаджет собран на квадратной плите-постаменте).
#
# Плита — ОТДЕЛЬНЫЙ child-меш (см. build_device_sets.py): рецепты строят
# только сам прибор, начиная с высоты PLATE_TOP. Вид плиты задаёт каталог
# (device_catalog_core.RECIPES, поле plate). Ни уровней, ни поколений:
# одна модель = один референс. «Лицо» устройства (стволы, дула, раструбы)
# смотрит в +Y.

from device_meshes import *
from building_meshes import dish_mesh, octahedron, loft_z
import numpy as np, math, os
PI = math.pi

PLATE_TOP = 0.16


def _p(vf, tag):
    return (vf[0], vf[1], tag)


# --------------------------------------------------------------- платформы

def platform(kind='silver', size=1.7):
    """Плита-постамент; верх на z=PLATE_TOP."""
    P = []
    if kind == 'circuit':
        P.append(_p(tf(box(size, size, 0.08), t=(0, 0, 0.04)), 'plat'))
        P.append(_p(tf(box(size * 0.94, size * 0.94, 0.06),
                       t=(0, 0, 0.11)), 'dgreen'))
        rng = np.random.default_rng(3)
        for _ in range(8):
            x, y = rng.uniform(-size * 0.4, size * 0.4, 2)
            P.append(_p(tf(box(0.06, 0.04, 0.02), t=(x, y, 0.15),
                           rz=rng.integers(0, 2) * PI / 2), 'gold'))
    elif kind == 'dark':
        P.append(_p(tf(box(size, size, 0.1), t=(0, 0, 0.05)), 'graph'))
        P.append(_p(tf(box(size * 0.92, size * 0.92, 0.06),
                       t=(0, 0, 0.13)), 'dark'))
    elif kind == 'fins':
        P.append(_p(tf(box(size, size, 0.09), t=(0, 0, 0.05)), 'silver'))
        P.append(_p(tf(box(size * 0.9, size * 0.9, 0.07),
                       t=(0, 0, 0.125)), 'plat'))
        for sgn in (-1, 1):
            for k in range(9):
                x = -size * 0.42 + k * size * 0.105
                P.append(_p(tf(box(0.05, 0.1, 0.07),
                               t=(x, sgn * (size / 2 - 0.02), 0.05)), 'plat'))
    elif kind == 'lattice':
        P.append(_p(tf(box(size, size, 0.06), t=(0, 0, 0.03)), 'silver'))
        for k in range(5):
            d = -size * 0.4 + k * size * 0.2
            P.append(_p(tf(box(0.03, size * 0.9, 0.06), t=(d, 0, 0.09)),
                        'plat'))
            P.append(_p(tf(box(size * 0.9, 0.03, 0.06), t=(0, d, 0.09)),
                        'plat'))
        P.append(_p(tf(box(size * 0.9, size * 0.9, 0.02), t=(0, 0, 0.13)),
                    'plat'))
    else:  # silver
        P.append(_p(tf(box(size, size, 0.09), t=(0, 0, 0.045)), 'silver'))
        P.append(_p(tf(box(size * 0.92, size * 0.92, 0.07),
                       t=(0, 0, 0.115)), 'plat'))
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.append(_p(tf(cyl(0.025, 0.02, 8),
                           t=(sx * size * 0.44, sy * size * 0.44, 0.155)),
                        'detail'))
    return P


# --------------------------------------------------------------- helpers

def _ycyl(r, h, seg=14, r2=None):
    """Цилиндр вдоль +Y (ось Z повёрнута в +Y)."""
    return tf(cyl(r, h, seg, r2=r2), rx=-PI / 2)


def _ycone(r, h, seg=12):
    """Конус остриём в +Y."""
    return tf(cyl(r, h, seg, r2=1e-4), rx=-PI / 2)


def _spool(r=0.09, w=0.14, seg=12, rings=4):
    """Катушка с намоткой: ось Z. (корпус, кольца намотки списком)."""
    body = cyl(r * 0.55, w, seg)
    rims = combine_vf([tf(torus(r, w / (rings * 2.6), seg, 6),
                          t=(0, 0, -w / 2 + w * (k + 0.5) / rings))
                       for k in range(rings)])
    return body, rims


def combine_vf(vfs):
    Vs, Fs, off = [], [], 0
    for V, F in vfs:
        Vs.append(np.asarray(V, float))
        Fs.append(np.asarray(F, int) + off)
        off += len(V)
    return np.vstack(Vs), np.vstack(Fs)


def _gauge(P, pos, rz=0.0):
    P.append(_p(tf(tf(cyl(0.06, 0.03, 12), rx=-PI / 2), t=pos, rz=rz),
                'white'))
    P.append(_p(tf(tf(torus(0.06, 0.012, 12, 5), rx=-PI / 2), t=pos, rz=rz),
                'detail'))


# ============================================================== ENGINES

def engine_tonklin_motor(seed=0):
    """Медный горизонтальный корпус, латунные U-выхлопы вперёд и четыре
    стопки красных плоских катушек сверху (реф Engine_TonklinMotor)."""
    P = []
    Z = PLATE_TOP
    zc = Z + 0.34
    # корпус вдоль X + серебристый купол слева
    P.append(_p(tf(cyl(0.3, 1.1, 16), ry=PI / 2, t=(-0.05, -0.15, zc)),
                'copper'))
    P.append(_p(tf(sphere(0.3, 14, 9), t=(-0.6, -0.15, zc), s=(0.75, 1, 1)),
                'silver'))
    for dx in (-0.35, 0.05, 0.4):
        P.append(_p(tf(torus(0.3, 0.02, 16, 6), ry=PI / 2, t=(dx, -0.15, zc)),
                    'coil2'))
    # латунные U-выхлопы вперёд (+Y), раструбы вниз к плите
    for x0 in (0.15, 0.55):
        P.append(_p(arc_pipe((x0, -0.05, zc + 0.05), (x0 + 0.1, 0.52, Z + 0.16),
                             (0, 0.15, 0.3), 0.13), 'coil2'))
        P.append(_p(tf(torus(0.14, 0.03, 12, 6), rx=PI / 2.6,
                       t=(x0 + 0.1, 0.56, Z + 0.16)), 'coil2'))
    # четыре стопки красных «беговых» катушек
    for k, x in enumerate((-0.5, -0.17, 0.16, 0.49)):
        for j in range(4):
            P.append(_p(tf(torus(0.13, 0.028, 14, 7),
                           t=(x, -0.2 + 0.03 * (k % 2), zc + 0.24 + j * 0.075),
                           s=(1, 1.9, 1)), 'coil'))
        P.append(_p(tf(cyl(0.02, 0.42, 6), t=(x, -0.2, zc + 0.42)), 'coil2'))
        P.append(_p(tf(box(0.05, 0.05, 0.03), t=(x, -0.2, zc + 0.64)), 'gold'))
    # оплётка-шланги по корпусу
    P.append(_p(arc_pipe((-0.55, -0.3, zc + 0.2), (-0.05, -0.42, zc + 0.05),
                         (0, -0.1, 0.15), 0.025), 'silver'))
    P.append(_p(arc_pipe((-0.3, -0.35, zc + 0.15), (0.3, -0.4, zc),
                         (0, -0.08, 0.2), 0.025), 'silver'))
    return merge(P)


def engine_ion_banger(seed=0):
    """Белое «яйцо» со стеклянным окном, ряды красных петель с жёлтыми
    клеммами и два перламутровых ствола вверх (реф Engine_IonBanger)."""
    P = []
    Z = PLATE_TOP
    # корпус-яйцо, окно смотрит вперёд-вправо
    cx, cy, cz = 0.2, -0.05, Z + 0.42
    P.append(_p(tf(sphere(0.42, 18, 12), t=(cx, cy, cz), s=(1.05, 1.15, 1)),
                'white'))
    P.append(_p(tf(tf(dome(0.26, 14, 6), rx=-PI / 2), t=(cx + 0.1, cy + 0.38,
                                                         cz)), 'glass'))
    P.append(_p(tf(tf(torus(0.26, 0.03, 14, 6), rx=-PI / 2),
                   t=(cx + 0.1, cy + 0.38, cz)), 'silver'))
    P.append(_p(tf(helix_coil(0.12, 0.2, 4, 0.014), rx=-PI / 2,
                   t=(cx + 0.1, cy + 0.3, cz)), 'silver'))
    # ряды красных петель с жёлтыми клеммами через верх корпуса
    for k, ang in enumerate(np.linspace(-0.7, 0.9, 5)):
        y = cy - 0.35 + k * 0.18
        R = 0.46 - 0.04 * abs(k - 2)
        for a in np.linspace(0.35, PI - 0.35, 4):
            x0 = cx - R * math.cos(a)
            z0 = cz + R * math.sin(a) * 0.85
            P.append(_p(tf(torus(0.055, 0.018, 10, 6), ry=PI / 2,
                           t=(x0, y, z0)), 'coil'))
        P.append(_p(tf(box(0.16, 0.1, 0.09),
                       t=(cx - R * 0.55, y, cz + R * 0.75), rz=0.2), 'yellow'))
        P.append(_p(tf(box(0.14, 0.09, 0.08),
                       t=(cx + R * 0.55, y, cz + R * 0.72), rz=-0.25),
                    'yellow'))
    # два перламутровых ствола вверх-влево-назад
    for dy, dz in ((-0.15, 0.0), (0.12, 0.12)):
        base = np.array([cx - 0.3, cy + dy, cz + 0.25 + dz])
        d = np.array([-0.55, -0.35, 0.75])
        d /= np.linalg.norm(d)
        tip = base + d * 0.55
        P.append(_p(tube(np.array([base, tip]), 0.075, 10), 'pearl'))
        P.append(_p(tf(sphere(0.08, 8, 6), t=tuple(tip)), 'silver'))
    # опора-косынка под стволами
    P.append(_p(tf(box(0.05, 0.3, 0.35), t=(cx - 0.55, cy - 0.1, Z + 0.18),
                   ry=0.4), 'coil2'))
    return merge(P)


# ====================================================== STAR LANE DRIVES

def star_lane_drive(seed=0):
    """Перламутровый «крендель» в синей кабельной обвязке, синие модули
    с медными крышками (реф StarLaneDrive)."""
    P = []
    Z = PLATE_TOP
    zc = Z + 0.45
    # крендель: три пересекающихся жирных тора (перламутровый узел)
    knots = ((0.32, 0.16, PI / 2.4, 0.3, (0.08, 0.05, zc + 0.14)),
             (0.28, 0.15, -PI / 2.9, -0.75, (-0.08, -0.05, zc + 0.02)),
             (0.24, 0.13, PI / 6, 1.6, (0.02, 0.12, zc + 0.22)))
    for R, r, rxx, rzz, t0 in knots:
        P.append(_p(tf(torus(R, r, 20, 12), rx=rxx, rz=rzz, t=t0), 'pearl'))
    # синие кабельные жгуты — обвивают главный тор параллельными витками
    for k, (roff, zoff) in enumerate(((0.2, 0.0), (0.23, 0.05),
                                      (0.21, -0.05))):
        path = []
        for t in np.linspace(-0.2, 1.55 * PI, 26):
            path.append((0.08 + (0.32 + roff * math.cos(3 * t)) * math.cos(t + 0.3),
                         0.05 + (0.32 + roff * math.cos(3 * t)) * math.sin(t + 0.3) * 0.55,
                         zc + 0.14 + zoff + 0.26 * math.sin(t + 0.3)))
        P.append(_p(tube(np.array(path), 0.032, 7), 'blue'))
    # чип-плата на узле
    P.append(_p(tf(box(0.16, 0.12, 0.05), t=(0.0, 0.05, zc + 0.44), rz=0.4),
                'graph'))
    for k in range(4):
        P.append(_p(tf(box(0.12, 0.015, 0.055), t=(0.0, 0.01 + k * 0.03,
                                                    zc + 0.44), rz=0.4),
                    'detail'))
    # синие модули с медными крышками и стеклянными окнами
    for (mx, my, ml, rzz) in ((-0.45, -0.35, 0.5, 0.5), (0.5, 0.3, 0.45, -0.4)):
        P.append(_p(tf(tf(cyl(0.13, ml, 12), ry=PI / 2), t=(mx, my, Z + 0.2),
                       rz=rzz), 'blue'))
        for sgn in (-1, 1):
            cap = (mx + sgn * ml / 2 * math.cos(rzz),
                   my + sgn * ml / 2 * math.sin(rzz), Z + 0.2)
            P.append(_p(tf(tf(cyl(0.145, 0.06, 12), ry=PI / 2), t=cap,
                           rz=rzz), 'copper'))
        P.append(_p(tf(box(ml * 0.5, 0.06, 0.12), t=(mx, my + 0.1, Z + 0.24),
                       rz=rzz), 'glass'))
    # серебристый блок с рёбрами
    P.append(_p(tf(box(0.3, 0.24, 0.2), t=(0.45, -0.4, Z + 0.1)), 'silver'))
    for k in range(4):
        P.append(_p(tf(box(0.26, 0.02, 0.16),
                       t=(0.45, -0.47 + k * 0.045, Z + 0.12)), 'detail'))
    return merge(P)


def star_lane_hyperdrive(seed=0):
    """Спираль из толстых гофрошлангов, тёмно-красные модули сверху и
    манометры (реф StarLaneDrive_HyperDrive)."""
    P = []
    Z = PLATE_TOP
    # спиральная укладка шлангов: нисходящая спираль большого радиуса
    path = []
    for t in np.linspace(0, 4.4 * PI, 64):
        rr = 0.46 - 0.02 * (t / (4.4 * PI))
        path.append((rr * math.cos(t), rr * math.sin(t),
                     Z + 0.6 - 0.1 * t / PI))
    P.append(_p(tube(np.array(path), 0.115, 10), 'silver'))
    # гофра: кольца по шлангу
    for t in np.linspace(0.3, 4.1 * PI, 26):
        rr = 0.46 - 0.02 * (t / (4.4 * PI))
        P.append(_p(tf(torus(0.115, 0.018, 10, 6),
                       t=(rr * math.cos(t), rr * math.sin(t),
                          Z + 0.6 - 0.1 * t / PI),
                       ry=PI / 2, rz=t + PI / 2), 'plat'))
    # тёмно-красные цилиндры-модули сверху
    for (mx, my, rzz) in ((-0.2, 0.25, 0.5), (0.3, -0.05, -0.6)):
        P.append(_p(tf(tf(cyl(0.14, 0.6, 12), ry=PI / 2), t=(mx, my, Z + 0.78),
                       rz=rzz), 'coil'))
        for dxx in (-0.2, 0.0, 0.2):
            P.append(_p(tf(torus(0.145, 0.02, 12, 6), ry=PI / 2,
                           t=(mx + dxx * math.cos(rzz),
                              my + dxx * math.sin(rzz), Z + 0.78), rz=rzz),
                        'silver'))
        P.append(_p(tf(sphere(0.14, 10, 7),
                       t=(mx + 0.32 * math.cos(rzz), my + 0.32 * math.sin(rzz),
                          Z + 0.78), s=(0.7, 1, 1)), 'plat'))
    # красные трубки обвязки и манометры
    P.append(_p(arc_pipe((-0.5, -0.3, Z + 0.15), (-0.35, 0.3, Z + 0.7),
                         (-0.2, 0, 0.2), 0.045), 'coil'))
    P.append(_p(arc_pipe((0.5, 0.25, Z + 0.2), (0.35, -0.1, Z + 0.72),
                         (0.2, 0.1, 0.15), 0.045), 'coil'))
    _gauge(P, (0.52, 0.35, Z + 0.5), rz=-0.6)
    _gauge(P, (-0.15, 0.02, Z + 0.95), rz=0.3)
    # центральная серебристая капсула
    P.append(_p(tf(cyl(0.09, 0.35, 10), t=(0.02, 0.05, Z + 0.55)), 'silver'))
    P.append(_p(tf(dome(0.09, 10, 5), t=(0.02, 0.05, Z + 0.72)), 'silver'))
    return merge(P)


# ============================================================ GENERATORS

def generator_proton_shaver(seed=0):
    """Синяя центральная колонна с красной обмоткой и четыре угловые
    катушечные башенки, медная обвязка (реф Generator_ProtonShaver)."""
    P = []
    Z = PLATE_TOP
    # центральная колонна
    P.append(_p(tf(cyl(0.3, 0.28, 16, r2=0.26), t=(0, 0, Z + 0.14)), 'blue'))
    P.append(_p(tf(helix_coil(0.21, 0.34, 7, 0.032), t=(0, 0, Z + 0.48)),
                'coil'))
    P.append(_p(tf(cyl(0.21, 0.26, 16), t=(0, 0, Z + 0.82)), 'blue'))
    P.append(_p(tf(torus(0.21, 0.02, 16, 6), t=(0, 0, Z + 0.95)), 'blue'))
    # угловые башенки
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.55, sy * 0.55
            for k in range(4):  # синие рёбра-блины
                P.append(_p(tf(cyl(0.13 - 0.005 * k, 0.035, 12),
                               t=(x, y, Z + 0.05 + k * 0.055)), 'blue'))
            P.append(_p(tf(cyl(0.1, 0.1, 12), t=(x, y, Z + 0.3)), 'gold'))
            P.append(_p(tf(cyl(0.115, 0.06, 12), t=(x, y, Z + 0.38)), 'blue'))
            P.append(_p(tf(helix_coil(0.095, 0.16, 5, 0.02),
                           t=(x, y, Z + 0.5)), 'coil'))
            P.append(_p(tf(cyl(0.085, 0.07, 12), t=(x, y, Z + 0.62)),
                        'silver'))
            # медные трубки к колонне
            P.append(_p(arc_pipe((x * 0.75, y * 0.75, Z + 0.55),
                                 (x * 0.25, y * 0.25, Z + 0.72),
                                 (0, 0, 0.1), 0.016), 'copper'))
            P.append(_p(arc_pipe((x * 0.8, y * 0.8, Z + 0.42),
                                 (x * 0.3, y * 0.3, Z + 0.35),
                                 (0, 0, 0.06), 0.016), 'copper'))
    # жёлтые поперечины
    for rzz in (0, PI / 2):
        P.append(_p(tf(box(1.35, 0.05, 0.04), t=(0, 0, Z + 0.33), rz=rzz),
                    'yellow'))
    return merge(P)


def generator_subatomic_scoop(seed=0):
    """Двойная стеклянная чаша-воронка с вихрем на колонне, синие
    перфорированные пилоны и боковые капсулы (реф Generator_SubatomicScoop)."""
    P = []
    Z = PLATE_TOP
    # медное кольцо-основание
    P.append(_p(tf(cyl(0.52, 0.07, 20), t=(0, 0, Z + 0.035)), 'copper'))
    # шесть синих пилонов-плавников
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        x, y = 0.33 * math.cos(a), 0.33 * math.sin(a)
        P.append(_p(tf(tf(box(0.05, 0.3, 0.42), rx=0.35),
                       t=(x, y, Z + 0.28), rz=a + PI / 2), 'blue'))
    # колонна-стек
    P.append(_p(tf(cyl(0.14, 0.1, 14), t=(0, 0, Z + 0.3)), 'dark'))
    P.append(_p(tf(cyl(0.11, 0.08, 14), t=(0, 0, Z + 0.39)), 'gold'))
    P.append(_p(tf(cyl(0.13, 0.06, 14), t=(0, 0, Z + 0.46)), 'silver'))
    # двойная чаша (открытые, стенка с толщиной)
    bowl1 = revolve([(0.34, 0.32), (0.1, 0.06), (0.12, 0.0), (0.36, 0.28)],
                    22, close=False)
    P.append(_p(tf(bowl1, t=(0, 0, Z + 0.5)), 'glass'))
    P.append(_p(tf(torus(0.35, 0.022, 22, 7), t=(0, 0, Z + 0.81)), 'silver'))
    bowl2 = revolve([(0.42, 0.3), (0.13, 0.04), (0.15, -0.02), (0.44, 0.26)],
                    22, close=False)
    P.append(_p(tf(bowl2, t=(0, 0, Z + 0.76)), 'glass'))
    P.append(_p(tf(torus(0.43, 0.025, 22, 7), t=(0, 0, Z + 1.05)), 'silver'))
    # тёмное дно и вихрь в верхней чаше
    P.append(_p(tf(cyl(0.13, 0.03, 14), t=(0, 0, Z + 0.81)), 'dark'))
    path = [(0.3 * math.exp(-t / 6) * math.cos(t),
             0.3 * math.exp(-t / 6) * math.sin(t),
             Z + 1.0 - 0.018 * t) for t in np.linspace(0, 10, 34)]
    P.append(_p(tube(np.array(path), 0.014, 6), 'bglow'))
    P.append(_p(tf(sphere(0.045, 8, 6), t=(0, 0, Z + 0.86)), 'bglow'))
    # боковые капсулы: красные/бирюзовые сердечники в серебре
    for k, a in enumerate(np.linspace(PI / 6, 2 * PI, 3, endpoint=False)):
        x, y = 0.62 * math.cos(a), 0.62 * math.sin(a)
        P.append(_p(tf(tf(cyl(0.09, 0.3, 10), ry=PI / 2), t=(x, y, Z + 0.12),
                       rz=a), 'silver'))
        core = 'redline' if k % 2 == 0 else 'teal'
        P.append(_p(tf(tf(cyl(0.06, 0.34, 8), ry=PI / 2), t=(x, y, Z + 0.12),
                       rz=a), core))
        P.append(_p(tf(torus(0.095, 0.015, 10, 5), ry=PI / 2,
                       t=(x, y, Z + 0.12), rz=a), 'teal'))
    return merge(P)


def generator_quark_express(seed=0):
    """Синий хаб с золотым куполом, двойное золотое кольцо и четыре
    красных светящихся капсулы (реф Generator_QuarkExpress)."""
    P = []
    Z = PLATE_TOP
    # барабан-основание с зелёными катушками по кругу
    P.append(_p(tf(cyl(0.42, 0.22, 18), t=(0, 0, Z + 0.11)), 'blue'))
    for a in np.linspace(0, 2 * PI, 12, endpoint=False):
        P.append(_p(tf(box(0.06, 0.05, 0.1),
                       t=(0.36 * math.cos(a), 0.36 * math.sin(a), Z + 0.12),
                       rz=a), 'green'))
    # двойное золотое кольцо
    P.append(_p(tf(torus(0.55, 0.035, 24, 8), t=(0, 0, Z + 0.16)), 'gold'))
    P.append(_p(tf(torus(0.55, 0.03, 24, 8), t=(0, 0, Z + 0.34)), 'gold'))
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        P.append(_p(tf(box(0.05, 0.05, 0.2),
                       t=(0.55 * math.cos(a), 0.55 * math.sin(a), Z + 0.25),
                       rz=a), 'blue'))
    # центральный хаб
    P.append(_p(tf(cyl(0.2, 0.3, 14), t=(0, 0, Z + 0.37)), 'blue'))
    P.append(_p(tf(dome(0.17, 14, 6), t=(0, 0, Z + 0.52)), 'gold'))
    # четыре красные капсулы: пара горизонтальных, пара под 45° вверх
    dirs = [(np.array([1, 0.15, 0.0]), 0.34), (np.array([-1, 0.15, 0.0]), 0.34),
            (np.array([0.55, 0.15, 0.8]), 0.42),
            (np.array([-0.55, 0.15, 0.8]), 0.42)]
    for d, off in dirs:
        d = d / np.linalg.norm(d)
        c = np.array([0, 0, Z + 0.42]) + d * off
        polar = math.acos(d[2])
        yaw = math.atan2(d[1], d[0])
        P.append(_p(tf(tf(cyl(0.105, 0.28, 12), ry=polar, rz=yaw), t=tuple(c)),
                    'blue'))
        P.append(_p(tf(tf(cyl(0.085, 0.3, 10), ry=polar, rz=yaw),
                       t=tuple(c + d * 0.06)), 'redline'))
        P.append(_p(tf(tf(cyl(0.11, 0.05, 12), ry=polar, rz=yaw),
                       t=tuple(c + d * 0.2)), 'blue'))
    # красный блок-упор спереди
    P.append(_p(tf(box(0.34, 0.14, 0.1), t=(0, 0.42, Z + 0.05)), 'coil'))
    return merge(P)


def generator_van_creeg(seed=0):
    """Стеклянный купол с бирюзовой «звездой» внутри и четыре наклонных
    стеклянных катушечных ускорителя (реф Generator_VanCreegHypersplicer)."""
    P = []
    Z = PLATE_TOP
    # кольцо-основание и купол
    P.append(_p(tf(cyl(0.48, 0.1, 20, r2=0.44), t=(0, 0, Z + 0.05)), 'silver'))
    P.append(_p(tf(dome(0.46, 20, 10), t=(0, 0, Z + 0.1), s=(1, 1, 1.05)),
                'glass'))
    # начинка: золотая клетка + звезда
    P.append(_p(tf(torus(0.3, 0.02, 16, 6), t=(0, 0, Z + 0.16)), 'gold'))
    P.append(_p(tf(torus(0.2, 0.016, 14, 6), t=(0, 0, Z + 0.34)), 'gold'))
    P.append(_p(tf(sphere(0.09, 10, 7), t=(0, 0, Z + 0.32)), 'accent'))
    rng = np.random.default_rng(seed + 9)
    for _ in range(8):
        d = rng.normal(size=3)
        d[2] = abs(d[2]) * 0.7
        d /= np.linalg.norm(d)
        tip = np.array([0, 0, Z + 0.32]) + d * rng.uniform(0.16, 0.26)
        P.append(_p(tube(np.array([(0, 0, Z + 0.32), tip]), 0.012, 5),
                    'bglow'))
    # четыре наклонных стеклянных ускорителя по диагоналям
    for sx in (-1, 1):
        for sy in (-1, 1):
            d = np.array([sx * 0.62, sy * 0.62, 0.75])
            d /= np.linalg.norm(d)
            polar = math.acos(d[2])
            yaw = math.atan2(d[1], d[0])
            c = np.array([sx * 0.5, sy * 0.5, Z + 0.32])
            P.append(_p(tf(tf(cyl(0.095, 0.5, 10), ry=polar, rz=yaw),
                           t=tuple(c)), 'glass'))
            P.append(_p(tf(tf(helix_coil(0.055, 0.4, 7, 0.016), ry=polar,
                              rz=yaw), t=tuple(c)), 'copper'))
            for f in (-0.24, 0.0, 0.24):
                P.append(_p(tf(tf(torus(0.1, 0.018, 10, 5), ry=polar, rz=yaw),
                               t=tuple(c + d * f)), 'silver'))
            P.append(_p(tf(tf(cyl(0.07, 0.06, 10), ry=polar, rz=yaw),
                           t=tuple(c + d * 0.29)), 'gold'))
    # два боковых финированных модуля
    for sgn in (-1, 1):
        P.append(_p(tf(tf(cyl(0.08, 0.3, 10), ry=PI / 2),
                       t=(sgn * 0.3, -0.62, Z + 0.09)), 'coil'))
        P.append(_p(tf(tf(torus(0.085, 0.015, 10, 5), ry=PI / 2),
                       t=(sgn * 0.3, -0.62, Z + 0.09)), 'blue'))
    return merge(P)


def generator_nanotwirler(seed=0):
    """Две стопки золотых гофрированных «бубликов» с красными светящимися
    оголовками и плазменная трубка спереди (реф Generator_Nanotwirler)."""
    P = []
    Z = PLATE_TOP
    for k, (cx, cy) in enumerate(((-0.35, 0.25), (0.38, 0.05))):
        # стопка бубликов: золотой + стеклянный со смещением
        for j, zz in enumerate((0.16, 0.42)):
            P.append(_p(tf(torus(0.27, 0.115, 18, 9), t=(cx, cy, Z + zz)),
                        'gold'))
            P.append(_p(tf(torus(0.27, 0.09, 18, 8),
                           t=(cx, cy, Z + zz + 0.13)), 'glass'))
            P.append(_p(tf(helix_coil(0.27, 0.04, 10, 0.012),
                           t=(cx, cy, Z + zz + 0.13)), 'copper'))
        # оголовок: красное свечение + тёмные рёбра
        P.append(_p(tf(cyl(0.09, 0.2, 12), t=(cx, cy, Z + 0.72)), 'redline'))
        for j in range(3):
            P.append(_p(tf(torus(0.1, 0.014, 12, 5),
                           t=(cx, cy, Z + 0.65 + j * 0.06)), 'coil'))
        P.append(_p(tf(cyl(0.115, 0.07, 14), t=(cx, cy, Z + 0.86)), 'dark'))
        for a in np.linspace(0, 2 * PI, 10, endpoint=False):
            P.append(_p(tf(box(0.015, 0.05, 0.07),
                           t=(cx + 0.11 * math.cos(a), cy + 0.11 * math.sin(a),
                              Z + 0.86), rz=a), 'dark'))
        # ножка
        P.append(_p(tf(cyl(0.16, 0.12, 12), t=(cx, cy, Z + 0.06)), 'silver'))
    # плазменная трубка на стойках спереди
    ax = np.array([0.92, 0.38, 0.1])
    ax /= np.linalg.norm(ax)
    polar, yaw = math.acos(ax[2]), math.atan2(ax[1], ax[0])
    c = np.array([-0.05, -0.5, Z + 0.22])
    P.append(_p(tf(tf(cyl(0.095, 0.6, 12), ry=polar, rz=yaw), t=tuple(c)),
                'glass'))
    P.append(_p(tf(tf(cyl(0.05, 0.55, 8), ry=polar, rz=yaw), t=tuple(c)),
                'bglow'))
    for f, tag in ((-0.28, 'blue'), (-0.18, 'coil'), (0.18, 'coil'),
                   (0.28, 'blue')):
        P.append(_p(tf(tf(torus(0.1, 0.022, 12, 6), ry=polar, rz=yaw),
                       t=tuple(c + ax * f)), tag))
    for sgn in (-1, 1):
        P.append(_p(tf(box(0.05, 0.05, 0.2),
                       t=tuple(c + ax * sgn * 0.22 - np.array([0, 0, 0.12]))),
                    'plat'))
    return merge(P)


# ============================================================== SCANNERS

def scanner_tonklin_freq(seed=0):
    """Латунные петли-«скрепки» с красными катушками на осях и линза в
    латунной клетке (реф Scanner_TonklinFrequencyAnalizer)."""
    P = []
    Z = PLATE_TOP
    # две серебристые стойки
    for dy in (-0.12, 0.14):
        P.append(_p(tf(cyl(0.03, 0.55, 8), t=(0.12, dy, Z + 0.28)), 'silver'))
    # латунные петли-скрепки (плющеные торы стоймя) на разной высоте
    loops = [(0.0, 0.0, 0.35, 0.6, 0.0), (-0.05, 0.1, 0.5, 0.75, 0.5),
             (0.1, -0.1, 0.28, 0.45, -0.4)]
    for (lx, ly, lz, lw, rzz) in loops:
        P.append(_p(tf(torus(0.16, 0.028, 16, 7), rx=PI / 2,
                       t=(lx, ly, Z + lz), rz=rzz, s=(lw / 0.32, 1, 1)),
                    'coil2'))
    # красные катушки на латунных осях, радиально в стороны
    rng = np.random.default_rng(seed + 11)
    for k, a in enumerate(np.linspace(0, 2 * PI, 8, endpoint=False)):
        R = 0.42 + 0.08 * (k % 2)
        x, y = R * math.cos(a), R * math.sin(a)
        z = Z + 0.2 + 0.18 * (k % 3)
        body, rims = _spool(0.095, 0.16)
        P.append(_p(tf(body, ry=PI / 2, t=(x, y, z), rz=a), 'coil2'))
        P.append(_p(tf(rims, ry=PI / 2, t=(x, y, z), rz=a), 'coil'))
        P.append(_p(tf(tf(cyl(0.025, 0.08, 6), ry=PI / 2),
                       t=(x + 0.11 * math.cos(a), y + 0.11 * math.sin(a), z),
                       rz=a), 'gold'))
        # ось к центру
        P.append(_p(tube(np.array([(x * 0.35, y * 0.35, z), (x, y, z)]),
                         0.022, 6), 'coil2'))
    # клетка с линзой наверху
    P.append(_p(tf(cyl(0.1, 0.06, 12), t=(0.12, 0.0, Z + 0.6)), 'coil2'))
    P.append(_p(tf(dome(0.07, 10, 5), t=(0.12, 0.0, Z + 0.64)), 'glass'))
    return merge(P)


def scanner_subspace_phase_array(seed=0):
    """Большая белая тарелка с крестовиной на золотом зубчатом основании
    и три малых тарелки вокруг (реф Scanner_SubspacePhaseArray)."""
    P = []
    Z = PLATE_TOP
    # золотое зубчатое основание
    P.append(_p(tf(cyl(0.3, 0.14, 16), t=(0, 0, Z + 0.07)), 'gold'))
    for a in np.linspace(0, 2 * PI, 12, endpoint=False):
        P.append(_p(tf(box(0.1, 0.07, 0.12),
                       t=(0.32 * math.cos(a), 0.32 * math.sin(a), Z + 0.07),
                       rz=a), 'gold'))
    P.append(_p(tf(cyl(0.09, 0.2, 10), t=(0, 0, Z + 0.24)), 'silver'))
    # большая тарелка (лицом вверх, чуть к зрителю)
    d = dish_mesh(0.6, depth=0.3)
    P.append(_p(tf(d, t=(0, 0, Z + 0.34), rx=-0.22), 'white'))
    # крестовина-облучатель
    for a in (0, PI / 2):
        P.append(_p(tf(tf(cyl(0.012, 0.75, 6), ry=PI / 2), t=(0, 0, Z + 0.52),
                       rz=a + 0.4, rx=-0.22), 'white'))
    P.append(_p(tf(cyl(0.02, 0.3, 6), t=(0, -0.05, Z + 0.55), rx=-0.22),
                'silver'))
    # золотые пластинчатые веера по бокам
    for sgn in (-1, 1):
        for k in range(4):
            P.append(_p(tf(box(0.36, 0.03, 0.02 + 0.008 * k),
                           t=(sgn * 0.45, -0.05 + k * 0.07, Z + 0.16)),
                        'gold'))
    # три малых тарелки вокруг
    for a in (PI * 0.78, PI * 1.5, PI * 0.22):
        x, y = 0.62 * math.cos(a), 0.62 * math.sin(a)
        P.append(_p(tf(box(0.14, 0.12, 0.14), t=(x, y, Z + 0.07), rz=a),
                    'plat'))
        P.append(_p(tf(dish_mesh(0.22, depth=0.28), t=(x, y, Z + 0.2),
                       rx=-PI / 2.6, rz=a - PI / 2), 'white'))
    return merge(P)


def scanner_aural_cloud(seed=0):
    """Кольцо наклонных бирюзовых перфотруб вокруг рубиновой «ягоды» на
    бронзовом конусе, стеклянные песочные колонны (реф AuralCloudConstructor)."""
    P = []
    Z = PLATE_TOP
    # золотое кольцо-обруч
    P.append(_p(tf(torus(0.5, 0.045, 24, 8), t=(0, 0, Z + 0.3)), 'gold'))
    # шесть наклонных бирюзовых труб раструбами вверх-наружу
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        d = np.array([math.cos(a) * 0.55, math.sin(a) * 0.55, 0.8])
        d /= np.linalg.norm(d)
        polar, yaw = math.acos(d[2]), math.atan2(d[1], d[0])
        c = np.array([0.38 * math.cos(a), 0.38 * math.sin(a), Z + 0.32])
        P.append(_p(tf(tf(cyl(0.15, 0.5, 12), ry=polar, rz=yaw), t=tuple(c)),
                    'teal'))
        P.append(_p(tf(tf(torus(0.15, 0.02, 12, 5), ry=polar, rz=yaw),
                       t=tuple(c + d * 0.25)), 'silver'))
        P.append(_p(tf(tf(cyl(0.12, 0.02, 12), ry=polar, rz=yaw),
                       t=tuple(c - d * 0.2)), 'dark'))
    # бронзовый конус + рубиновая ягода
    P.append(_p(tf(cyl(0.18, 0.35, 14, r2=0.1), t=(0, 0, Z + 0.4)), 'copper'))
    P.append(_p(tf(sphere(0.17, 12, 9), t=(0, 0, Z + 0.68)), 'redline'))
    rng = np.random.default_rng(seed + 13)
    for _ in range(12):
        d = rng.normal(size=3)
        d[2] = abs(d[2])
        d /= np.linalg.norm(d)
        P.append(_p(tf(sphere(0.035, 6, 5),
                       t=tuple(np.array([0, 0, Z + 0.68]) + d * 0.16)),
                    'coil'))
    # стеклянные песочные колонны по углам
    hour = revolve([(0.09, 0.5), (0.1, 0.45), (0.045, 0.25), (0.1, 0.05),
                    (0.09, 0.0)], 12)
    for (hx, hy) in ((-0.62, -0.42), (0.62, -0.42), (0.05, -0.68)):
        P.append(_p(tf(hour, t=(hx, hy, Z)), 'glass'))
    return merge(P)


def scanner_hyperwave_tympanum(seed=0):
    """Стопка медных торов-«барабанов» и четыре золотых кристалла-лампы
    на красных стойках (реф Scanner_HyperwaveTympanum)."""
    P = []
    Z = PLATE_TOP
    # барабан: три сплюснутых тора + крышка с воронкой
    for k, (R, zz) in enumerate(((0.44, 0.14), (0.46, 0.34), (0.42, 0.52))):
        P.append(_p(tf(torus(R, 0.14, 22, 10), t=(0, 0, Z + zz),
                       s=(1, 1, 0.75)), 'copper'))
    P.append(_p(tf(cyl(0.4, 0.05, 20), t=(0, 0, Z + 0.64)), 'copper'))
    funnel = revolve([(0.28, 0.08), (0.1, 0.02), (0.04, 0.06)], 18)
    P.append(_p(tf(funnel, t=(0, 0, Z + 0.66)), 'copper'))
    # центральный кристалл
    P.append(_p(tf(octahedron(0.09, 1.4), t=(0, 0, Z + 0.84)), 'gold'))
    # четыре красных стойки с золотыми кристаллами-лампами
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.58, sy * 0.58
            P.append(_p(tf(cyl(0.028, 0.62, 8), t=(x, y, Z + 0.31)), 'coil'))
            P.append(_p(tf(cyl(0.04, 0.04, 8), t=(x, y, Z + 0.62)), 'silver'))
            P.append(_p(tf(octahedron(0.1, 1.3), t=(x, y, Z + 0.74)), 'gold'))
            P.append(_p(tf(sphere(0.035, 6, 5), t=(x, y, Z + 0.74)),
                        'accent'))
    return merge(P)


def scanner_nanowave_net(seed=0):
    """Красный обруч-диск с «кружевом» синих колец на паучьих ногах
    (реф Scanner_NanowaveDecouplingNet)."""
    P = []
    Z = PLATE_TOP
    zc = Z + 0.42
    # красный обруч
    P.append(_p(tf(cyl(0.62, 0.1, 28), t=(0, 0, zc)), 'coil'))
    P.append(_p(tf(cyl(0.56, 0.11, 28), t=(0, 0, zc)), 'copper'))
    # кружево синих колец: внешнее кольцо из 8 + внутреннее из 5 + центр
    for R, n, rr in ((0.42, 8, 0.115), (0.22, 5, 0.085)):
        for a in np.linspace(0, 2 * PI, n, endpoint=False):
            x, y = R * math.cos(a), R * math.sin(a)
            P.append(_p(tf(torus(rr, 0.024, 14, 6), t=(x, y, zc + 0.06)),
                        'blue'))
            P.append(_p(tf(cyl(rr - 0.02, 0.02, 12), t=(x, y, zc + 0.02)),
                        'copper'))
    for a in np.linspace(PI / 8, 2 * PI, 4, endpoint=False):
        P.append(_p(tf(torus(0.05, 0.014, 10, 5),
                       t=(0.32 * math.cos(a), 0.32 * math.sin(a), zc + 0.07)),
                    'pglow'))
    # серебристая кнопка в центре
    P.append(_p(tf(cyl(0.09, 0.05, 12), t=(0, 0, zc + 0.07)), 'silver'))
    P.append(_p(tf(dome(0.05, 10, 4), t=(0, 0, zc + 0.1)), 'silver'))
    # паучьи ноги-актуаторы
    for a in np.linspace(PI / 6, 2 * PI, 6, endpoint=False):
        x1, y1 = 0.52 * math.cos(a), 0.52 * math.sin(a)
        x0, y0 = 0.66 * math.cos(a), 0.66 * math.sin(a)
        P.append(_p(tube(np.array([(x0 * 0.9, y0 * 0.9, Z + 0.02),
                                   (x0, y0, Z + 0.2),
                                   (x1, y1, zc - 0.06)]), 0.025, 6), 'plat'))
        P.append(_p(tf(cyl(0.035, 0.12, 8),
                       t=(x1 * 1.05, y1 * 1.05, zc - 0.16)), 'silver'))
    return merge(P)


# =============================================================== SHIELDS

def shield_ion_wrap(seed=0):
    """Плоский медный тор, красная пружина и полосатые обручи в сетчатых
    зажимах (реф Shield_ion_wrap). Гранёный, без сглаживания."""
    P = []
    Z = PLATE_TOP
    # медный тор
    P.append(_p(tf(torus(0.45, 0.12, 24, 10), t=(0, 0, Z + 0.14)), 'copper'))
    # красная пружина-башня в центре
    P.append(_p(tf(helix_coil(0.16, 0.36, 7, 0.035), t=(0, 0, Z + 0.36)),
                'coil'))
    P.append(_p(tf(cyl(0.07, 0.12, 8), t=(0, 0, Z + 0.56)), 'silver'))
    # четыре сетчатых зажима-седла на торе + два красных обруча между ними
    clamp_a = (PI * 0.2, PI * 0.8, PI * 1.15, PI * 1.75)
    for k, a in enumerate(clamp_a):
        x, y = 0.45 * math.cos(a), 0.45 * math.sin(a)
        tag = 'teal' if k % 2 == 0 else 'blue'
        # седло обнимает тор и спускается к плите
        P.append(_p(tf(loft_z([(Z + 0.02, [(0.17, -0.14), (0.17, 0.14),
                                           (-0.17, 0.14), (-0.17, -0.14)]),
                               (Z + 0.3, [(0.13, -0.11), (0.13, 0.11),
                                          (-0.13, 0.11), (-0.13, -0.11)]),
                               (Z + 0.5, [(0.075, -0.06), (0.075, 0.06),
                                          (-0.075, 0.06), (-0.075, -0.06)])]),
                       t=(x, y, 0), rz=a), tag))
        P.append(_p(tf(box(0.1, 0.1, 0.06), t=(x, y, Z + 0.53), rz=a),
                    'green'))
    # красные обручи: концы входят в оголовки пар зажимов
    for (a0, a1) in ((clamp_a[0], clamp_a[1]), (clamp_a[2], clamp_a[3])):
        p0 = (0.45 * math.cos(a0), 0.45 * math.sin(a0), Z + 0.56)
        p1 = (0.45 * math.cos(a1), 0.45 * math.sin(a1), Z + 0.56)
        P.append(_p(arc_pipe(p0, p1, (0, 0, 0.42), 0.05, n=20), 'coil'))
    # тонкие медные провода из тора в центр
    for a in (0.8, 2.6, 4.4):
        P.append(_p(arc_pipe((0.4 * math.cos(a), 0.4 * math.sin(a), Z + 0.2),
                             (0.1 * math.cos(a + 1), 0.1 * math.sin(a + 1),
                              Z + 0.3), (0, 0, 0.12), 0.012), 'copper'))
    # чип-коробочка на торе
    P.append(_p(tf(box(0.1, 0.07, 0.06), t=(-0.44, 0.12, Z + 0.28), rz=0.5),
                'graph'))
    return merge(P)


def shield_deactotron(seed=0):
    """Синий барабан, крест из четырёх медных пик под золотым куполом и
    чёрные обручи (реф Shield_deactotron). Гранёный."""
    P = []
    Z = PLATE_TOP
    # барабан
    P.append(_p(tf(cyl(0.5, 0.32, 20), t=(0, 0, Z + 0.16)), 'blue'))
    P.append(_p(tf(torus(0.5, 0.03, 20, 7), t=(0, 0, Z + 0.32)), 'teal'))
    for a in np.linspace(0, 2 * PI, 8, endpoint=False):
        P.append(_p(tf(box(0.12, 0.03, 0.12),
                       t=(0.48 * math.cos(a), 0.48 * math.sin(a), Z + 0.14),
                       rz=a), 'bglow'))
    # ножки-шарики
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        P.append(_p(tf(sphere(0.07, 8, 6),
                       t=(0.38 * math.cos(a), 0.38 * math.sin(a), Z + 0.02)),
                    'blue'))
    # крест из медных пик
    hub = np.array([0, 0, Z + 0.44])
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        d = np.array([math.cos(a), math.sin(a), 0.12])
        d /= np.linalg.norm(d)
        polar, yaw = math.acos(d[2]), math.atan2(d[1], d[0])
        c = hub + d * 0.3
        P.append(_p(tf(tf(cyl(0.06, 0.35, 10, r2=1e-4), ry=polar, rz=yaw),
                       t=tuple(c + d * 0.1)), 'copper'))
        P.append(_p(tf(tf(cyl(0.065, 0.16, 10), ry=polar, rz=yaw),
                       t=tuple(hub + d * 0.16)), 'blue'))
    P.append(_p(tf(dome(0.14, 14, 6), t=tuple(hub + np.array([0, 0, 0.02]))),
                'gold'))
    # чёрные обручи над крестом
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        x, y = 0.3 * math.cos(a), 0.3 * math.sin(a)
        P.append(_p(tf(torus(0.16, 0.022, 14, 6), rx=PI / 2,
                       t=(x, y, Z + 0.52), rz=a + PI / 2), 'dark'))
    return merge(P)


def shield_wave_scatterer(seed=0):
    """Тёмная сфера-клетка с фиолетовыми линзами, утыканная перламутровыми
    кристаллами, на зелёных трубах-опорах (реф Shield_wave_scatterer).
    Гранёный."""
    P = []
    Z = PLATE_TOP
    c = np.array([0, 0, Z + 0.52])
    # сфера-клетка
    P.append(_p(tf(sphere(0.42, 16, 11), t=tuple(c)), 'graph'))
    for zz, rr in ((0.18, 0.38), (0.0, 0.42), (-0.18, 0.38)):
        P.append(_p(tf(torus(rr, 0.03, 20, 6), t=tuple(c + np.array([0, 0,
                                                                     zz]))),
                    'dark'))
    # фиолетовые линзы по экватору
    for a in np.linspace(0, 2 * PI, 8, endpoint=False):
        P.append(_p(tf(sphere(0.05, 8, 6),
                       t=tuple(c + np.array([0.42 * math.cos(a),
                                             0.42 * math.sin(a), 0.02]))),
                    'pglow'))
    # перламутровые кристаллы наружу
    rng = np.random.default_rng(seed + 17)
    for _ in range(26):
        d = rng.normal(size=3)
        d /= np.linalg.norm(d)
        if d[2] < -0.55:
            continue
        base = c + d * 0.4
        ln = rng.uniform(0.12, 0.24)
        polar, yaw = math.acos(d[2]), math.atan2(d[1], d[0])
        P.append(_p(tf(tf(cyl(0.035, ln, 6, r2=1e-4), ry=polar, rz=yaw),
                       t=tuple(base + d * ln / 2)), 'pearl'))
    # зелёные трубы-опоры
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        x, y = 0.62 * math.cos(a), 0.62 * math.sin(a)
        P.append(_p(arc_pipe((x, y, Z + 0.04), tuple(c + np.array(
            [0.3 * math.cos(a), 0.3 * math.sin(a), -0.2])),
                             (0, 0, 0.1), 0.075), 'green'))
    return merge(P)


def shield_conclusion(seed=0):
    """Центральное «яйцо» с перламутровыми дольками в тёмной оправе и
    четыре купольные тумбы на стопках шестерён (реф Shield_conclusion).
    Гранёный."""
    P = []
    Z = PLATE_TOP
    c = np.array([0, 0, Z + 0.5])
    # яйцо: перламутровая сфера + тёмные меридианы
    P.append(_p(tf(sphere(0.4, 18, 12), t=tuple(c), s=(1, 1, 1.3)), 'pearl'))
    for rzz in (0, PI / 3, 2 * PI / 3):
        P.append(_p(tf(torus(0.4, 0.028, 20, 6), rx=PI / 2, rz=rzz,
                       t=tuple(c), s=(1, 1, 1.28)), 'graph'))
    P.append(_p(tf(torus(0.34, 0.025, 18, 6), t=tuple(c + np.array([0, 0,
                                                                    -0.3]))),
                'graph'))
    # четыре угловые тумбы: стопка шестерён + перламутровый купол
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 0.52, sy * 0.52
            for k in range(4):
                r = 0.16 - 0.008 * k
                P.append(_p(tf(cyl(r, 0.05, 14), t=(x, y, Z + 0.04 + k * 0.08)),
                            'graph'))
                P.append(_p(tf(torus(r, 0.018, 14, 6),
                               t=(x, y, Z + 0.07 + k * 0.08)), 'dark'))
            P.append(_p(tf(cyl(0.17, 0.04, 14), t=(x, y, Z + 0.36)), 'silver'))
            P.append(_p(tf(dome(0.15, 14, 8), t=(x, y, Z + 0.38)), 'pearl'))
    # малый купол спереди
    for k in range(3):
        P.append(_p(tf(cyl(0.12 - 0.006 * k, 0.045, 12),
                       t=(0, -0.62, Z + 0.03 + k * 0.07)), 'graph'))
    P.append(_p(tf(dome(0.11, 12, 7), t=(0, -0.62, Z + 0.24)), 'pearl'))
    return merge(P)


# =============================================================== WEAPONS

def weapon_ueberlaser(seed=0):
    """Гатлинг-лазер: серебристая сфера в жёлтой вилке на круглом
    постаменте, ствол-кассета в клетке из прутьев, дуло в +Y
    (реф Weapon_Ueberlaser)."""
    P = []
    Z = PLATE_TOP
    # круглый постамент с зубцами
    P.append(_p(tf(cyl(0.48, 0.1, 20), t=(0, -0.1, Z + 0.05)), 'wood'))
    P.append(_p(tf(cyl(0.42, 0.06, 20), t=(0, -0.1, Z + 0.13)), 'plat'))
    for a in np.linspace(0, 2 * PI, 10, endpoint=False):
        P.append(_p(tf(box(0.1, 0.06, 0.08),
                       t=(0.46 * math.cos(a), -0.1 + 0.46 * math.sin(a),
                          Z + 0.1), rz=a), 'wood'))
    # жёлтая вилка-качалка
    for sgn in (-1, 1):
        P.append(_p(tf(loft_z([(Z + 0.14, [(0.2, -0.07), (0.2, 0.07),
                                           (-0.2, 0.07), (-0.2, -0.07)]),
                               (Z + 0.75, [(0.08, -0.05), (0.08, 0.05),
                                           (-0.08, 0.05), (-0.08, -0.05)])]),
                       t=(sgn * 0.33, -0.25, 0)), 'yellow'))
    P.append(_p(tf(box(0.75, 0.1, 0.09), t=(0, -0.25, Z + 0.78)), 'yellow'))
    P.append(_p(tf(tf(cyl(0.05, 0.5, 8), ry=PI / 2), t=(0, -0.25, Z + 0.68)),
                'glass'))
    # тело: сфера + барабан вдоль +Y
    P.append(_p(tf(sphere(0.28, 16, 10), t=(0, -0.3, Z + 0.45)), 'silver'))
    P.append(_p(tf(_ycyl(0.24, 0.4, 16), t=(0, 0.0, Z + 0.45)), 'silver'))
    P.append(_p(tf(_ycyl(0.26, 0.06, 16), t=(0, 0.14, Z + 0.45)), 'detail'))
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        P.append(_p(tf(box(0.05, 0.2, 0.02),
                       t=(0.24 * math.cos(a), 0.02, Z + 0.45 + 0.24 * math.sin(a)),
                       ry=-a), 'detail'))
    # кассета стволов: зелёно-жёлтые сегменты в клетке из прутьев
    segs = [('green', 0.3), ('yellow', 0.5), ('green', 0.72)]
    for tag, yy in segs:
        P.append(_p(tf(_ycyl(0.16, 0.2, 14), t=(0, yy, Z + 0.45)), tag))
    for f, tag in ((0.4, 'white'), (0.62, 'silver')):
        P.append(_p(tf(tf(torus(0.185, 0.022, 14, 6), rx=PI / 2),
                       t=(0, f, Z + 0.45)), tag))
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        P.append(_p(tf(tf(cyl(0.018, 0.62, 6), rx=-PI / 2),
                       t=(0.185 * math.cos(a), 0.5,
                          Z + 0.45 + 0.185 * math.sin(a))), 'silver'))
    # дульный блок
    P.append(_p(tf(_ycyl(0.15, 0.1, 12), t=(0, 0.88, Z + 0.45)), 'green'))
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        P.append(_p(tf(tf(cyl(0.02, 0.05, 6), rx=-PI / 2),
                       t=(0.1 * math.cos(a), 0.94,
                          Z + 0.45 + 0.1 * math.sin(a))), 'dark'))
    P.append(_p(tf(_ycyl(0.07, 0.08, 10), t=(0, 0.97, Z + 0.45)), 'bglow'))
    # жёлтый амбушюр-блок на теле
    P.append(_p(tf(box(0.2, 0.25, 0.18), t=(-0.2, -0.42, Z + 0.35), rz=0.3),
                'coil2'))
    return merge(P)


def weapon_plasmatron(seed=0):
    """Бронзовый барабан сзади, белая рама-скоба и красная светящаяся
    гофроспираль-ствол с раскалённым дулом в +Y (реф Weapon_Plasmatron)."""
    P = []
    Z = PLATE_TOP
    zc = Z + 0.42
    # задний бронзовый диск-барабан
    P.append(_p(tf(_ycyl(0.36, 0.22, 18), t=(0, -0.42, zc)), 'copper'))
    P.append(_p(tf(_ycyl(0.28, 0.06, 16), t=(0, -0.55, zc)), 'dark'))
    P.append(_p(tf(tf(torus(0.36, 0.03, 18, 7), rx=PI / 2), t=(0, -0.3, zc)),
                'detail'))
    # белое тело и рама-скоба
    P.append(_p(tf(_ycyl(0.2, 0.35, 14), t=(0, -0.1, zc)), 'white'))
    for sgn in (-1, 1):
        path = np.array([(sgn * 0.3, -0.5, Z + 0.05),
                         (sgn * 0.42, -0.35, zc + 0.28),
                         (sgn * 0.18, 0.05, zc + 0.4),
                         (sgn * 0.08, 0.1, zc + 0.28)])
        P.append(_p(tube(path, 0.045, 8), 'white'))
    P.append(_p(tf(box(0.1, 0.3, 0.3), t=(0.28, -0.15, Z + 0.15), ry=0.3),
                'white'))
    # красная гофроспираль вокруг ствола
    P.append(_p(tf(tf(helix_coil(0.13, 0.55, 9, 0.045), rx=-PI / 2),
                   t=(0, 0.25, zc)), 'redline'))
    P.append(_p(tf(_ycyl(0.07, 0.6, 10), t=(0, 0.25, zc)), 'silver'))
    # дуло
    P.append(_p(tf(_ycyl(0.09, 0.08, 10), t=(0, 0.58, zc)), 'detail'))
    P.append(_p(tf(_ycone(0.06, 0.14, 10), t=(0, 0.68, zc)), 'accent'))
    return merge(P)


def weapon_hypersphere_driver(seed=0):
    """Ствол-объектив с синим нутром и линзой в +Y, сзади гроздь золотых
    сфер-накопителей (реф Weapon_HypersphereDriver)."""
    P = []
    Z = PLATE_TOP
    zc = Z + 0.45
    # объектив: серебристый барабан с кольцами и синим голо-окном
    P.append(_p(tf(_ycyl(0.32, 0.55, 18), t=(0, 0.32, zc)), 'silver'))
    for yy, rr in ((0.1, 0.345), (0.3, 0.36), (0.5, 0.345)):
        P.append(_p(tf(tf(torus(rr, 0.028, 18, 7), rx=PI / 2), t=(0, yy, zc)),
                    'plat'))
    # синее светящееся окно-голограмма на боку барабана
    P.append(_p(tf(box(0.05, 0.26, 0.2), t=(0.32, 0.3, zc), rz=0.1), 'bglow'))
    P.append(_p(tf(box(0.05, 0.3, 0.24), t=(0.325, 0.3, zc), rz=0.1),
                'glass'))
    # линза: стеклянный купол + бирюзовая и оранжевая сердцевина
    P.append(_p(tf(tf(cyl(0.3, 0.06, 18), rx=-PI / 2), t=(0, 0.62, zc)),
                'dark'))
    P.append(_p(tf(tf(dome(0.26, 16, 8), rx=-PI / 2), t=(0, 0.63, zc),
                   s=(1, 0.6, 1)), 'teal'))
    P.append(_p(tf(sphere(0.08, 10, 7), t=(0, 0.68, zc)), 'accent'))
    P.append(_p(tf(tf(dome(0.29, 16, 8), rx=-PI / 2), t=(0, 0.62, zc),
                   s=(1, 0.75, 1)), 'glass'))
    P.append(_p(tf(tf(torus(0.31, 0.032, 18, 7), rx=PI / 2), t=(0, 0.62, zc)),
                'silver'))
    # гроздь золотых сфер сзади: упакована вокруг оси
    rng = np.random.default_rng(seed + 19)
    cluster = [(0, 0, 0, 0.17)]
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        cluster.append((0.22 * math.cos(a), -0.05, 0.22 * math.sin(a), 0.14))
    for a in np.linspace(PI / 6, 2 * PI, 5, endpoint=False):
        cluster.append((0.3 * math.cos(a), -0.24, 0.3 * math.sin(a), 0.12))
    for (x, y, zoff, r) in cluster:
        P.append(_p(tf(sphere(r, 12, 8), t=(x, -0.12 + y, zc + zoff)),
                    'gold'))
        P.append(_p(tf(box(r * 0.5, 0.03, r * 0.3),
                       t=(x, -0.12 + y + r * 0.85, zc + zoff)), 'accent'))
    # горловина с гофрой между гроздью и объективом
    P.append(_p(tf(_ycyl(0.22, 0.14, 14), t=(0, 0.06, zc)), 'dark'))
    P.append(_p(tf(tf(helix_coil(0.24, 0.1, 3, 0.022), rx=-PI / 2),
                   t=(0, 0.04, zc)), 'plat'))
    # опора-ложемент
    P.append(_p(tf(box(0.34, 0.5, 0.1), t=(0, 0.3, Z + 0.05)), 'graph'))
    for yy in (0.12, 0.5):
        P.append(_p(tf(box(0.44, 0.08, 0.16), t=(0, yy, Z + 0.12)), 'graph'))
    return merge(P)


def weapon_nanomanipulator(seed=0):
    """Рупор из стопки серебристых дисков с розовыми светящимися кольцами,
    серая труба-рукоять и радиаторное основание (реф Weapon_Nanomanipulator).
    Рупор растёт в +Y вверх."""
    P = []
    Z = PLATE_TOP
    # основание: конус + радиаторные рёбра
    P.append(_p(tf(cyl(0.4, 0.16, 18, r2=0.28), t=(0, -0.15, Z + 0.08)),
                'graph'))
    for k in range(6):
        P.append(_p(tf(box(0.34, 0.02, 0.1),
                       t=(0, -0.15 - 0.03 * k, Z + 0.2)), 'dark'))
    # ось рупора: вперёд-вверх
    d = np.array([0, 0.55, 0.83])
    d /= np.linalg.norm(d)
    polar, yaw = math.acos(d[2]), math.atan2(d[1], d[0])
    c0 = np.array([0, -0.15, Z + 0.3])
    # стопка дисков от малого к большому с розовыми кольцами между
    discs = ((0.09, 0.0), (0.13, 0.14), (0.17, 0.28), (0.22, 0.44),
             (0.28, 0.62), (0.36, 0.82))
    for k, (rr, off) in enumerate(discs):
        cc = c0 + d * off
        P.append(_p(tf(tf(cyl(rr, 0.06, 16), ry=polar, rz=yaw), t=tuple(cc)),
                    'silver'))
        if k:
            mid = c0 + d * (off - 0.07)
            P.append(_p(tf(tf(torus(rr * 0.75, 0.02, 14, 6), ry=polar,
                              rz=yaw), t=tuple(mid)), 'pglow'))
    # раструб с розовым нутром
    tip = c0 + d * 0.95
    P.append(_p(tf(tf(cyl(0.42, 0.05, 18), ry=polar, rz=yaw), t=tuple(tip)),
                'silver'))
    P.append(_p(tf(tf(cyl(0.36, 0.02, 16), ry=polar, rz=yaw),
                   t=tuple(tip + d * 0.02)), 'pglow'))
    # серая труба-рукоять вокруг
    path = np.array([(-0.55, -0.35, Z + 0.05), (-0.55, -0.35, Z + 0.7),
                     (0.0, -0.55, Z + 0.85), (0.55, -0.35, Z + 0.7),
                     (0.55, -0.35, Z + 0.05)])
    P.append(_p(tube(path, 0.05, 8), 'plat'))
    # мех-узлы на рукояти
    P.append(_p(tf(box(0.14, 0.12, 0.1), t=(0.55, -0.35, Z + 0.4)), 'silver'))
    P.append(_p(tf(box(0.12, 0.1, 0.09), t=(0.35, -0.5, Z + 0.72), rz=0.5),
                'silver'))
    return merge(P)


# ================================================================== AUX

def aux_colonizer(seed=0):
    """Колонизатор-диорама (реф Aux_Colonizer), скомпонована по грани плиты:
    panel-a вдоль грани d; drum-a и engine-a — параллельные агрегаты вдоль
    оси X, торцами упёртые в panel-a, drum-a боком у грани c, engine-a
    боком у drum-a; dome-a у грани a; tank-a у второго торца drum-a;
    rack-a/шкаф/rack-b — группа вдоль оси a между tank-a и торцом engine-a;
    clamp-a стоит на ребре вдоль грани b рядом с tank-a, из него выходят
    hose-a/hose-b, огибающие rack-группу; egg-a/b/c в углу a-b вдоль грани
    b, mini-a..f вторым рядом за ними, ring-a (лежит плашмя) — следом за
    mini-рядом; флаг в углу c-d."""
    P = []
    Z = PLATE_TOP
    half = 0.85

    def xcyl(vf, x, y, z, tag):
        P.append(_p(tf(tf(vf, ry=PI / 2), t=(x, y, z)), tag))

    # --- panel-a: вдоль грани d (левая грань, тянется по Y)
    panel_thick = 0.07
    px = -half + panel_thick / 2          # -0.815
    panel_inner_x = -half + panel_thick   # -0.78 (лицевая сторона панели)
    py = 0.28
    plen = 1.05
    # панель стоит ребром на подложке (нижняя кромка на Z = уровень плиты)
    P.append(_p(tf(box(panel_thick, plen, 0.62), t=(px, py, Z + 0.31)),
                'graph'))
    for dz in (0.61, 0.01):
        P.append(_p(tf(box(0.1, plen + 0.04, 0.05), t=(px, py, Z + dz)),
                    'copper'))
    for sgn in (-1, 1):
        P.append(_p(tf(box(0.1, 0.05, 0.64),
                       t=(px, py + sgn * (plen / 2 - 0.01), Z + 0.31)),
                    'copper'))
    for k in range(8):
        P.append(_p(tf(box(0.09, 0.05, 0.4),
                       t=(px + 0.02, py - plen / 2 + 0.08 + k * (plen - 0.16)
                          / 7, Z + 0.23)), 'dark'))
    P.append(_p(tf(box(0.05, 0.24, 0.16),
                   t=(px + 0.06, py + plen / 2 - 0.22, Z + 0.49)), 'bglow'))
    for k, tag in enumerate(('teal', 'yellow', 'blue')):
        yy = py + plen / 2 - 0.3 + k * 0.09
        P.append(_p(arc_pipe((px, yy, Z + 0.59), (px, yy, Z + 0.55),
                             (0.05, 0, 0.05), 0.012), tag))

    # --- drum-a: параллельно оси X, торцом (dome) к panel-a, боком к грани c
    drum_r = 0.21
    drum_y = half - 0.23 - 0.02             # 0.60 — у грани c (с учётом макс. радиуса торцевых колец 0.23)
    drum_dome_x = panel_inner_x + drum_r   # торец у панели
    # исходные относительные смещения (от dome-центра исходного рецепта)
    drum_rel = (0.0, 0.12, 0.34, 0.56, 0.72, 0.75)
    d0 = drum_dome_x
    P.append(_p(tf(tf(dome(0.21, 14, 7), ry=-PI / 2),
                   t=(d0 + drum_rel[0], drum_y, Z + 0.34)), 'silver'))
    drum_segs = ((0.12, 0.21, 0.2), (0.34, 0.23, 0.2), (0.56, 0.21, 0.18),
                (0.72, 0.18, 0.14))
    for (rel, rr, ww) in drum_segs:
        xcyl(cyl(rr, ww, 16), d0 + rel, drum_y, Z + 0.34, 'silver')
        xcyl(torus(rr, 0.02, 16, 6), d0 + rel + ww / 2, drum_y, Z + 0.34,
             'plat')
    drum_end_x = d0 + 0.72 + 0.14 / 2      # правый торец барабана
    xcyl(cyl(0.12, 0.06, 12), drum_end_x + 0.06, drum_y, Z + 0.34, 'graph')
    drum_end_x += 0.12
    # панелька-люк на барабане
    P.append(_p(tf(box(0.12, 0.02, 0.1),
                   t=(d0 + 0.34, drum_y - 0.23, Z + 0.36)), 'coil2'))
    for rel in (0.0, 0.56):
        P.append(_p(tf(box(0.12, 0.3, 0.18),
                       t=(d0 + rel, drum_y, Z + 0.09)), 'plat'))

    # --- engine-a: параллельно, торцом (dome) к panel-a, боком к drum-a
    engine_dome_r = 0.15
    engine_r = 0.17
    engine_y = drum_y - drum_r - engine_r - 0.02   # 0.22 — сторона к drum
    engine_dome_x = panel_inner_x + engine_dome_r
    e0 = engine_dome_x
    # исходные относительные смещения от dome-центра (было xx=-0.2)
    def erel(orig_xx):
        return orig_xx - (-0.2)

    P.append(_p(tf(tf(dome(0.15, 12, 6), ry=-PI / 2),
                   t=(e0, engine_y, Z + 0.26)), 'green'))
    # стеклянная секция в зелёной клетке, удлинена для симметрии с drum-a
    cage_len = 0.62
    xcyl(cyl(0.15, cage_len, 14), e0 + 0.05 + cage_len / 2, engine_y,
         Z + 0.26, 'glass')
    xcyl(cyl(0.095, cage_len - 0.04, 10), e0 + 0.05 + cage_len / 2, engine_y,
         Z + 0.26, 'detail')
    for f in (0.06, 0.36, 0.66):
        xcyl(cyl(0.17, 0.055, 14), e0 + 0.05 + f, engine_y, Z + 0.26,
             'green')
    for roll in np.linspace(0, 2 * PI, 6, endpoint=False):
        P.append(_p(tf(box(cage_len + 0.02, 0.042, 0.042),
                       t=(e0 + 0.05 + cage_len / 2,
                          engine_y + 0.163 * math.cos(roll),
                          Z + 0.26 + 0.163 * math.sin(roll))), 'green'))
    cage_end_x = e0 + 0.05 + cage_len
    # серебристый воротник + нос
    xcyl(cyl(0.14, 0.05, 12), cage_end_x + 0.025, engine_y, Z + 0.26,
         'silver')
    xcyl(cyl(0.125, 0.09, 12, r2=0.085), cage_end_x + 0.115, engine_y,
         Z + 0.26, 'green')
    nose_c = cage_end_x + 0.16 + 0.1
    xcyl(cyl(0.09, 0.2, 12, r2=0.045), nose_c, engine_y, Z + 0.26, 'green')
    engine_end_x = nose_c + 0.1            # кончик носа
    # ложементы
    for xx in (e0 + 0.3, cage_end_x - 0.1):
        P.append(_p(tf(box(0.1, 0.26, 0.14), t=(xx, engine_y, Z + 0.07)),
                    'plat'))

    # --- геокупол со шлюзом: максимально к грани a
    dome_r = 0.34
    ddx, ddy = -0.38, -half + dome_r + 0.03   # к грани a
    P.append(_p(tf(cyl(dome_r * 1.05, 0.06, 18), t=(ddx, ddy, Z + 0.03)),
                'silver'))
    g, fr = _geodome_dev(dome_r)
    P.append(_p(tf(g, t=(ddx, ddy, Z + 0.06)), 'glass'))
    P.append(_p(tf(fr, t=(ddx, ddy, Z + 0.06)), 'silver'))
    # --- gate-a: восьмигранный модуль-шлюз правее купола
    gx, gy_ = ddx + dome_r + 0.16, ddy
    P.append(_p(tf(tf(cyl(0.11, 0.08, 8), rx=PI / 2), t=(gx, gy_, Z + 0.14),
                   rz=PI / 8), 'plat'))
    P.append(_p(tf(tf(cyl(0.07, 0.1, 8), rx=PI / 2),
                   t=(gx, gy_ - 0.01, Z + 0.14), rz=PI / 8), 'graph'))
    P.append(_p(tf(tf(cyl(0.04, 0.03, 8), rx=PI / 2),
                   t=(gx, gy_ - 0.05, Z + 0.14), rz=PI / 8), 'bglow'))

    # --- tank-a: у второго (правого) торца drum-a
    tank_r = 0.12
    tank_x = drum_end_x + tank_r + 0.02
    tank_y = drum_y
    P.append(_p(tf(cyl(tank_r, 0.42, 14), t=(tank_x, tank_y, Z + 0.21)),
                'wood'))
    P.append(_p(tf(cyl(tank_r + 0.01, 0.06, 14), t=(tank_x, tank_y, Z + 0.45)),
                'graph'))
    P.append(_p(tf(box(0.1, 0.06, 0.04), t=(tank_x, tank_y, Z + 0.5)),
                'plat'))

    # --- rack-a / шкаф / rack-b: компактная группа, оси a (X), у грани b;
    # связана короткими кабелями с tank-a и торцом engine-a
    rack_hw, cab_hw = 0.05, 0.07
    rack_row_y = engine_y + 0.1
    rack_a_x = 0.5
    cab_x = rack_a_x + rack_hw + cab_hw + 0.02
    rack_b_x = cab_x + cab_hw + rack_hw + 0.02   # <= half(0.85) - rack_hw

    def rack(cx, cy, hh):
        P.append(_p(tf(box(rack_hw * 2, 0.13, hh), t=(cx, cy, Z + hh / 2)),
                    'copper'))
        for j in range(4):
            P.append(_p(tf(box(rack_hw * 1.5, 0.02, 0.05),
                           t=(cx - rack_hw * 0.05, cy - 0.065,
                              Z + 0.08 + j * hh / 4.5)), 'dark'))
            P.append(_p(tf(box(rack_hw * 1.3, 0.015, 0.03),
                           t=(cx - rack_hw * 0.08, cy - 0.068,
                              Z + 0.08 + j * hh / 4.5)), 'white'))

    rack(rack_a_x, rack_row_y, 0.5)
    rack(rack_b_x, rack_row_y, 0.44)
    # шкаф с полками за матовым (полупрозрачным) стеклом
    cab_h = 0.46
    P.append(_p(tf(box(cab_hw * 2, 0.15, cab_h), t=(cab_x, rack_row_y, Z +
                                                     cab_h / 2)), 'dark'))
    P.append(_p(tf(box(cab_hw * 1.8, 0.02, cab_h * 0.9),
                   t=(cab_x, rack_row_y - 0.075, Z + cab_h / 2)), 'glass'))
    for j in range(3):
        P.append(_p(tf(box(cab_hw * 1.6, 0.1, 0.02),
                       t=(cab_x, rack_row_y, Z + 0.1 + j * cab_h / 3)),
                    'plat'))
    # короткие кабели-перемычки: tank-a -> rack-a, торец engine-a -> rack-b
    P.append(_p(tube(np.array([(tank_x + tank_r * 0.6, tank_y, Z + 0.2),
                               (rack_a_x - rack_hw, rack_row_y, Z + 0.2)]),
                     0.022, 6), 'plat'))
    P.append(_p(tube(np.array([(engine_end_x, engine_y, Z + 0.15),
                               (rack_b_x - rack_hw, rack_row_y, Z + 0.15)]),
                     0.022, 6), 'plat'))

    # --- clamp-a: вдоль грани b, у tank-a, стоит на длинном ребре
    clamp_x = tank_x + tank_r + 0.1
    clamp_y = tank_y
    P.append(_p(tf(box(0.16, 0.2, 0.3), t=(clamp_x, clamp_y, Z + 0.15)),
                'white'))
    P.append(_p(tf(box(0.18, 0.22, 0.05), t=(clamp_x, clamp_y, Z + 0.31)),
                'silver'))

    # --- hose-a/hose-b: выходят из clamp-a одним торцом, огибают сверху
    # rack-группу (rack-a и rack-b)
    for k, (target_x, ry) in enumerate(((rack_a_x, rack_row_y),
                                        (rack_b_x, rack_row_y))):
        R = 0.16 + 0.04 * k
        ts = np.linspace(0, PI, 14)
        path = np.array([
            (clamp_x - t / PI * (clamp_x - target_x),
             clamp_y - (clamp_y - ry) * (t / PI),
             Z + 0.3 + R * 1.2 * math.sin(t))
            for t in ts])
        P.append(_p(tube(path, 0.032, 9), 'gold'))
        for pt in (path[0], path[-1]):
            P.append(_p(tf(cyl(0.042, 0.06, 9),
                           t=(pt[0], pt[1], pt[2] - 0.025)), 'silver'))


    # --- egg-a/b/c: угол граней a-b, далее вдоль грани b
    egg_r = 0.085
    egg_x = half - egg_r - 0.04
    egg_y0 = -half + egg_r + 0.04
    for k in range(3):
        ex, ey = egg_x, egg_y0 + k * (2 * egg_r + 0.06)
        P.append(_p(tf(cyl(0.06, 0.03, 10), t=(ex, ey, Z + 0.015)), 'plat'))
        P.append(_p(tf(sphere(egg_r, 10, 8), t=(ex, ey, Z + 0.12),
                       s=(1, 1, 1.25)), 'teal'))

    # --- mini-a..f: следующий ряд за яйцами, вдоль грани b (интерьер)
    mini_x0 = egg_x - 0.22
    mini_defs = (('blue', 0.3), ('teal', 0.26), ('graph', 0.34),
                ('coil', 0.16), ('yellow', 0.22), ('white', 0.12))
    for k, (tag, hh) in enumerate(mini_defs):
        col = k % 2
        row = k // 2
        mx = mini_x0 - col * 0.11
        my = egg_y0 + row * (2 * egg_r + 0.06)
        P.append(_p(tf(box(0.055, 0.05, hh), t=(mx, my, Z + hh / 2)), tag))
        P.append(_p(tf(box(0.04, 0.035, 0.02), t=(mx, my, Z + hh + 0.01)),
                    'dark'))
        if col == 0:
            P.append(_p(tf(cyl(0.005, 0.07, 5), t=(mx, my, Z + hh + 0.05)),
                        'silver'))

    # --- ring-a: лежит плашмя, следом за рядом mini вдоль грани b
    ring_y = egg_y0 + 3 * (2 * egg_r + 0.06)
    ring_x = mini_x0 - 0.05
    P.append(_p(tf(torus(0.13, 0.05, 8, 6), t=(ring_x, ring_y, Z + 0.05)),
                'green'))
    P.append(_p(tf(torus(0.09, 0.035, 8, 6), t=(ring_x, ring_y, Z + 0.11)),
                'green'))

    # --- флагшток с латунным рваным флагом (угол граней d-a)
    fx, fy = -half + 0.08, -half + 0.08
    P.append(_p(tf(cyl(0.016, 1.05, 8), t=(fx, fy, Z + 0.52)), 'silver'))
    P.append(_p(tf(sphere(0.03, 8, 6), t=(fx, fy, Z + 1.06)), 'silver'))
    P.append(_p(tf(box(0.24, 0.02, 0.15), t=(fx + 0.13, fy, Z + 0.93)),
                'coil2'))
    P.append(_p(tf(box(0.08, 0.02, 0.09), t=(fx + 0.28, fy, Z + 0.96),
                   rz=0.15), 'coil2'))
    return merge(P)


def _geodome_dev(r, seg=14, rings=6):
    """Мини-геокупол для устройств: (стекло, каркас)."""
    glass = dome(r, seg, rings)
    parts = []
    for rr in np.linspace(0.95, 0.4, 3):
        z = r * math.sqrt(max(1 - rr * rr, 0))
        parts.append(tf(torus(rr * r, 0.008 + 0.008 * r, 16, 5), t=(0, 0, z)))
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        path = [(r * math.cos(t) * math.cos(a), r * math.cos(t) * math.sin(a),
                 r * math.sin(t)) for t in np.linspace(0.05, PI / 2, 7)]
        parts.append(tube(np.array(path), 0.008 + 0.008 * r, 5))
    return glass, combine_vf(parts)


_INVASION_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "invasion_module_mesh.npz")


def aux_invasion_module(seed=0):
    """Десантный штурмовой модуль — геометрия взята из точного низкополи-
    гонального референса Aux_core_InvasionModule_3.glb (5723 верш./9839
    треуг., ~90КБ, без цвета в исходнике). Цвет перенесён с более раннего
    высокополигонального 100%-эталона Aux_core_InvasionModule_2.glb
    (129MB, растеризован и не годится для прямого импорта) методом
    ближайшей точки: с эталона взято ~60k точек поверхности с цветом из
    базовой текстуры (с переводом linear->sRGB), для каждой грани
    референса-3 голосованием по 40 ближайшим точкам определён доминирующий
    оттенок среди узкого набора реальных цветов модели (tan/teal/
    redbright/copper/dark — остальные теги палитры исключены, иначе
    многочисленные похожие серые перетягивают грани на себя). Результат
    сохранён заранее (tools/invasion_module_mesh.npz) и просто грузится
    здесь — самого тяжёлого референса в рантайме нет."""
    data = np.load(_INVASION_MESH_PATH)
    V, F = data["V"], data["F"]
    tag_idx, tag_names = data["tag_idx"], data["tag_names"]
    tags = [str(tag_names[i]) for i in tag_idx]
    V = V.astype(float).copy()
    V[:, 2] += PLATE_TOP - V[:, 2].min()   # опустить на уровень плиты
    return V, F.astype(int), tags



def aux_lane_magnetron(seed=0):
    """Кластер серебристых баков и «самоцветных» цилиндров, связанных
    трубками с жёлто-зелёной светящейся жидкостью (реф Aux_LaneMagnetron)."""
    P = []
    Z = PLATE_TOP
    # три самоцветных цилиндра (синий/бирюзовый/зелёный) по диагонали
    gems = (((-0.15, 0.35), 'blue', 0.5), ((0.2, 0.15), 'teal', 0.42),
            ((0.5, -0.05), 'green', 0.36))
    for (gx, gy), tag, zz in gems:
        P.append(_p(tf(cyl(0.15, 0.2, 14), t=(gx, gy, Z + zz)), tag))
        P.append(_p(tf(torus(0.15, 0.025, 14, 6), t=(gx, gy, Z + zz + 0.1)),
                    'gold'))
        P.append(_p(tf(torus(0.15, 0.02, 14, 6), t=(gx, gy, Z + zz - 0.08)),
                    'gold'))
        P.append(_p(tf(dome(0.11, 12, 5), t=(gx, gy, Z + zz + 0.11)), 'glass'))
        P.append(_p(tf(cyl(0.1, 0.18, 12), t=(gx, gy, Z + zz - 0.2)), 'gold'))
    # серебристые пузатые баки
    for (bx, by, r) in ((0.42, -0.42, 0.17), (0.12, -0.5, 0.15)):
        P.append(_p(tf(sphere(r, 14, 9), t=(bx, by, Z + r + 0.16),
                       s=(1, 1, 1.25)), 'silver'))
        P.append(_p(tf(cyl(r * 0.75, 0.14, 12), t=(bx, by, Z + 0.08)),
                    'detail'))
    # лежачий бак слева и латунный насос-конус
    P.append(_p(tf(cyl(0.13, 0.4, 12), ry=PI / 2, t=(-0.45, -0.3, Z + 0.14),
                   rz=0.3), 'silver'))
    P.append(_p(tf(sphere(0.13, 10, 7), t=(-0.65, -0.24, Z + 0.14)), 'plat'))
    P.append(_p(tf(cyl(0.1, 0.22, 10, r2=0.04), ry=PI / 2,
                   t=(-0.15, -0.42, Z + 0.12), rz=-0.2), 'coil2'))
    # светящиеся жёлто-зелёные трубки между узлами
    links = (((-0.15, 0.35, 0.75), (0.2, 0.15, 0.66), 0.25),
             ((0.2, 0.15, 0.66), (0.5, -0.05, 0.6), 0.2),
             ((0.5, -0.05, 0.5), (0.42, -0.42, 0.45), 0.18),
             ((-0.45, -0.3, 0.2), (-0.15, 0.35, 0.55), 0.3))
    for (a, b, lift) in links:
        P.append(_p(arc_pipe((a[0], a[1], Z + a[2] - 0.15),
                             (b[0], b[1], Z + b[2] - 0.15),
                             (0, 0, lift), 0.035), 'yglow'))
    # вертикальная светящаяся колонна с серебристым верхом
    P.append(_p(tf(cyl(0.05, 0.5, 8), t=(0.68, 0.3, Z + 0.35)), 'yglow'))
    P.append(_p(tf(cyl(0.06, 0.08, 8), t=(0.68, 0.3, Z + 0.62)), 'silver'))
    P.append(_p(tf(cyl(0.06, 0.06, 8), t=(0.68, 0.3, Z + 0.08)), 'silver'))
    # лежачая стеклянная трубка с жидкостью
    P.append(_p(tf(cyl(0.075, 0.4, 10), ry=PI / 2, t=(-0.3, 0.55, Z + 0.1),
                   rz=0.25), 'glass'))
    P.append(_p(tf(cyl(0.05, 0.36, 8), ry=PI / 2, t=(-0.3, 0.55, Z + 0.1),
                   rz=0.25), 'yglow'))
    _gauge(P, (-0.02, -0.15, Z + 0.52), rz=0.4)
    return merge(P)
