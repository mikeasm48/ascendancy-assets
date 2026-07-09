# Рецепты HUMANS v2 — индустриальный металл + категорийные цвета как у Core.

from device_meshes import *
import numpy as np, math
PI = math.pi

def _p(vf, tag): return (vf[0], vf[1], tag)

# цвет «поколения» для generator/shield
LEVEL_COL = {1:'blue', 2:'teal', 3:'gold', 4:'accent', 5:'coil'}

def h_nozzle(pos, r=0.3, tag_body='hull_b', with_flame=True):
    """Сопло-колокол, раскрытое в +Y (на зрителя), с лопатками и пламенем."""
    P = []
    bell = revolve([(0.34*r,0.02),(0.42*r,0.2*r),(0.62*r,0.55*r),(0.95*r,1.0*r),(1.04*r,1.12*r),(0.92*r,1.14*r),(0.58*r,0.6*r),(0.38*r,0.22*r),(0.3*r,0.05)], 24)
    P.append(_p(tf(bell, t=pos, rx=PI/2, rz=PI), tag_body))
    P.append(_p(tf(tf(torus(0.98*r, 0.035*r, 26, 8), t=(0,0,1.1*r)), t=pos, rx=PI/2, rz=PI), 'detail'))
    P.append(_p(tf(tf(cyl(0.3*r, 0.05*r, 16), t=(0,0,0.04*r)), t=pos, rx=PI/2, rz=PI), 'dark'))
    for a in np.linspace(0, 2*PI, 10, endpoint=False):
        blade = tf(box(0.04*r, 0.45*r, 0.38*r), t=(0.38*r*math.cos(a), 0.38*r*math.sin(a), 0.28*r), rz=a)
        P.append(_p(tf(blade, t=pos, rx=PI/2, rz=PI), 'detail'))
    if with_flame:
        flame = revolve([(0.01,0.12*r),(0.38*r,0.6*r),(0.24*r,1.4*r),(0.01,2.4*r)], 12)
        P.append(_p(tf(flame, t=pos, rx=PI/2, rz=PI), 'flame'))
    return P

def engine(level, seed=0):
    """Ракетный двигатель горизонтально: камера + трубки + колокол к зрителю."""
    P = []
    s = 0.8 + 0.14*level
    zc = 0.5*s
    # камера сгорания (-Y) и горловина
    P.append(_p(tf(sphere(0.28*s, 18, 10), t=(0, -0.5*s, zc)), 'hull'))
    P.append(_p(tf(cyl(0.2*s, 0.5*s, 16), t=(0, -0.25*s, zc), rx=PI/2), 'hull'))
    # красное катушечное кольцо у горловины (категорийный цвет двигателей)
    P.append(_p(tf(helix_coil(0.24*s, 0.22*s, 4, 0.03*s), t=(0, -0.1*s, zc), rx=PI/2), 'coil'))
    # трубопроводы вдоль камеры
    for a in np.linspace(0, 2*PI, 8, endpoint=False):
        x, z = 0.24*s*math.cos(a), 0.24*s*math.sin(a)
        path = np.array([(x*0.9, -0.62*s, zc + z*0.9), (x, -0.3*s, zc + z), (x*0.85, -0.05*s, zc + z*0.85)])
        P.append(_p(tube(path, 0.022*s, 6), 'hull_b'))
    # верхний агрегат
    P.append(_p(tf(box(0.24*s, 0.3*s, 0.16*s), t=(0, -0.45*s, zc + 0.3*s)), 'detail'))
    P += h_nozzle((0, -0.02*s, zc), r=0.34*s)
    if level >= 2:
        P.append(_p(tf(torus(0.3*s, 0.025*s, 22, 8), t=(0, -0.35*s, zc), rx=PI/2), 'detail'))
    if level >= 3:  # малые боковые сопла
        for sgn in (-1, 1):
            P.append(_p(tf(sphere(0.1*s, 10, 6), t=(sgn*0.3*s, -0.4*s, zc + 0.12*s)), 'hull_b'))
            P += h_nozzle((sgn*0.3*s, -0.1*s, zc + 0.12*s), r=0.12*s, with_flame=False)
    return merge(P)

def star_lane(level, seed=0):
    """Джамп-драйв: ступенчатый цилиндр горизонтально, синее жерло к зрителю."""
    P = []
    s = 0.8 + 0.14*level
    zc = 0.5*s
    y = -0.7*s
    for r, h, tag in ((0.2, 0.3, 'hull'), (0.28, 0.32, 'hull_b'), (0.36, 0.34, 'hull'), (0.42, 0.36, 'detail')):
        P.append(_p(tf(cyl(r*s, h*s, 20), t=(0, y + h*s/2, zc), rx=PI/2), tag))
        y += h*s
    # рёбра на широкой секции
    for k in range(3):
        P.append(_p(tf(torus(0.43*s, 0.02*s, 26, 6), t=(0, y - (0.08 + 0.1*k)*s, zc), rx=PI/2), 'hull_b'))
    # синее жерло (категорийный цвет star lane) + кольцо
    P.append(_p(tf(cyl(0.36*s, 0.05*s, 20), t=(0, y + 0.01*s, zc), rx=PI/2), 'blue'))
    P.append(_p(tf(torus(0.4*s, 0.035*s, 26, 8), t=(0, y + 0.03*s, zc), rx=PI/2), 'blue'))
    # антенны-стабилизаторы сзади
    for a in np.linspace(PI/4, 2*PI, 4, endpoint=False):
        x, z = math.cos(a), math.sin(a)
        P.append(_p(tf(cyl(0.015*s, 0.45*s, 6), t=(x*0.22*s, -0.75*s, zc + z*0.22*s), rx=PI/2 + 0.3*z, rz=0.2*x), 'detail'))
    P.append(_p(tf(sphere(0.16*s, 14, 8), t=(0, -0.78*s, zc)), 'hull_b'))
    if level >= 2:
        P.append(_p(tf(helix_coil(0.45*s, 0.3*s, 3, 0.025*s), t=(0, y - 0.5*s, zc), rx=PI/2), 'blue'))
    return merge(P)

def generator(level, seed=0):
    """L1-2: линза-ядро (реф GLB); L3: гекс-барабан (реф 3);
    L4-5: кольцевой реактор со светящимся окном (реф 2)."""
    P = []
    lc = LEVEL_COL[level]
    if level <= 2:
        s = 0.7 + 0.14*level
        zc = 0.42*s
        P.append(_p(tf(sphere(0.55*s, 26, 14), s=(1, 1, 0.6), t=(0,0,zc)), 'hull'))
        for i, r in enumerate(np.linspace(0.42, 0.14, 3)):
            zz = zc + 0.55*s*0.6*(1 - (r/0.55)**2)**0.5 * 0.95
            P.append(_p(tf(torus(r*s, 0.032*s, 26, 8), t=(0,0,zz)), 'detail' if i % 2 else lc))
        P.append(_p(tf(sphere(0.12*s, 14, 8), t=(0,0,zc + 0.36*s)), lc))
        for a2 in np.linspace(0, 2*PI, 4, endpoint=False):
            x, y = 0.52*s*math.cos(a2), 0.52*s*math.sin(a2)
            P.append(_p(tf(box(0.14*s, 0.09*s, 0.26*s), t=(x, y, zc), rz=a2), 'hull_b'))
        P.append(_p(tf(cyl(0.34*s, 0.1*s, 20), t=(0,0,0.06*s)), 'hull_b'))
        P.append(_p(tf(helix_coil(0.56*s, 0.14*s, 2, 0.024*s), t=(0,0,zc)), 'coil'))
    elif level == 3:
        s = 1.0
        # гекс-барабан: стеклянный цилиндр с плазмой + крышки с светокольцами
        P.append(_p(tf(cyl(0.34*s, 0.12*s, 20), t=(0,0,0.06*s)), 'gun_d'))
        P.append(_p(tf(cyl(0.3*s, 0.14*s, 18), t=(0,0,0.18*s)), 'gun'))
        P.append(_p(tf(torus(0.285*s, 0.02*s, 24, 6), t=(0,0,0.26*s)), lc))
        P.append(_p(tf(cyl(0.26*s, 0.5*s, 18), t=(0,0,0.52*s)), 'glass'))
        P.append(_p(tf(cyl(0.13*s, 0.44*s, 12), t=(0,0,0.52*s)), lc))  # плазма-ядро
        # гекс-каркас на барабане
        for zi, zz in enumerate((0.38*s, 0.52*s, 0.66*s)):
            n_h = 6
            for a2 in np.linspace(zi*0.3, 2*PI + zi*0.3, n_h, endpoint=False):
                x, y = 0.27*s*math.cos(a2), 0.27*s*math.sin(a2)
                rx = PI/2; rzz = a2 + PI/2
                P.append(_p(tf(tf(cyl(0.07*s, 0.015*s, 6), ry=PI/2), t=(x, y, zz), rz=a2), 'gun'))
        P.append(_p(tf(cyl(0.3*s, 0.14*s, 18), t=(0,0,0.86*s)), 'gun'))
        P.append(_p(tf(torus(0.285*s, 0.02*s, 24, 6), t=(0,0,0.78*s)), lc))
        P.append(_p(tf(cyl(0.2*s, 0.1*s, 14), t=(0,0,0.98*s)), 'gun_d'))
        # манипуляторы по бокам
        for sgn in (-1, 1):
            P.append(_p(tube(np.array([(sgn*0.3*s, 0, 0.7*s), (sgn*0.48*s, 0.05*s, 0.62*s), (sgn*0.52*s, 0.1*s, 0.48*s)]), 0.025*s, 6), 'gun_d'))
    else:
        s = 0.85 + 0.15*(level-4)
        zc = 0.62*s
        # кольцевой реактор: бронированный тор вертикально, окно-плазма в центре
        P.append(_p(tf(box(0.5*s, 0.36*s, 0.14*s), t=(0,0,0.07*s)), 'gun_d'))
        P.append(_p(tf(cyl(0.3*s, 0.18*s, 6, r2=0.36*s), t=(0,0,0.22*s)), 'gun'))
        P.append(_p(tf(torus(0.42*s, 0.14*s, 30, 12), t=(0,0,zc), rx=PI/2), 'gun'))
        # сегменты брони по кольцу
        for a2 in np.linspace(0, 2*PI, 8, endpoint=False):
            x, z = 0.42*s*math.cos(a2), 0.42*s*math.sin(a2)
            P.append(_p(tf(box(0.2*s, 0.12*s, 0.14*s), t=(x, 0, zc+z), rz=0, ry=-a2), 'gun_d'))
        # светящееся окно в центре кольца
        P.append(_p(tf(cyl(0.27*s, 0.06*s, 20), t=(0, 0, zc), rx=PI/2), lc))
        P.append(_p(tf(torus(0.29*s, 0.02*s, 24, 8), t=(0, 0.045*s, zc), rx=PI/2), 'bglow'))
        P.append(_p(tf(torus(0.29*s, 0.02*s, 24, 8), t=(0, -0.045*s, zc), rx=PI/2), 'bglow'))
        # красные кабели (категорийный акцент генераторов)
        for sgn in (-1, 1):
            P.append(_p(arc_pipe((sgn*0.42*s, 0.06*s, 0.22*s), (sgn*0.3*s, 0.06*s, zc+0.28*s), (sgn*0.18*s, 0.04*s, 0.0), 0.022*s), 'coil'))
        if level == 5:  # второй контур
            P.append(_p(tf(torus(0.55*s, 0.05*s, 34, 10), t=(0,0,zc), rx=PI/2), 'detail'))
            P.append(_p(tf(torus(0.55*s, 0.018*s, 34, 8), t=(0, 0.06*s, zc), rx=PI/2), lc))
    return merge(P)

def shield(level, seed=0):
    """Гекс-сфера; размер и цвет кольца/плиток = поколение. Без сглаживания."""
    P = []
    s = 0.62 + 0.13*level
    lc = LEVEL_COL[level]
    zc = 0.6*s
    P.append(_p(tf(sphere(0.48*s, 26, 14), t=(0,0,zc)), 'hull'))
    V, _ = sphere(0.48*s, 12, 7)
    seen = set()
    for v in V:
        key = tuple((v*8).astype(int))
        if key in seen: continue
        seen.add(key)
        n = v / (np.linalg.norm(v) + 1e-9)
        c = v + n*0.012*s + np.array([0,0,zc])
        rx = math.atan2(math.hypot(n[0], n[1]), n[2])
        rz = math.atan2(n[1], n[0])
        tag = 'hull_b' if (abs(hash(key)) % 5) else lc
        P.append(_p(tf(cyl(0.08*s, 0.018*s, 6), t=c, ry=rx, rz=rz), tag))
    P.append(_p(tf(torus(0.56*s, 0.028*s, 30, 8), t=(0,0,zc), rx=PI/2.6), lc))
    P.append(_p(tf(torus(0.3*s, 0.045*s, 22, 8), t=(0,0,0.1*s)), 'detail'))
    P.append(_p(tf(cyl(0.26*s, 0.08*s, 16), t=(0,0,0.04*s)), 'hull_b'))
    return merge(P)

def ring_seg(R, r_tube, y, a0, a1, n=16, tseg=8):
    """Сегмент кольца в плоскости XZ (нормаль на зрителя +Y)."""
    path = [(R*math.cos(a), y, R*math.sin(a)) for a in np.linspace(a0, a1, n)]
    return tube(np.array(path), r_tube, tseg)

def scanner(level, seed=0):
    """По Scanner_humans_1..4: графит, красные канты."""
    P = []
    s = 0.85 + 0.08*level
    if level == 1:  # крест из сдвоенных штанг на башне (ref 1)
        P.append(_p(tf(box(0.34*s, 0.34*s, 0.3*s), t=(0,0,0.15*s)), 'graph'))
        P.append(_p(tf(torus(0.2*s, 0.02*s, 20, 6), t=(0,0,0.08*s)), 'redline'))
        P.append(_p(tf(cyl(0.13*s, 0.5*s, 8, r2=0.1*s), t=(0,0,0.55*s)), 'dark'))
        P.append(_p(tf(sphere(0.11*s, 14, 8), t=(0,0,0.88*s)), 'graph'))
        for (zz, rot) in ((0.68*s, 0.0), (0.82*s, PI/2)):
            for dy in (-0.045*s, 0.045*s):
                P.append(_p(tf(box(1.05*s, 0.055*s, 0.07*s), t=(0, dy, zz), rz=rot), 'dark'))
            P.append(_p(tf(box(0.16*s, 0.16*s, 0.1*s), t=(0,0,zz), rz=rot), 'redline'))
        P.append(_p(tf(sphere(0.045*s, 8, 6), t=(0,0,1.0*s)), 'redline'))
    elif level == 2:  # широкая изогнутая «банан»-антенна (ref 2)
        P.append(_p(tf(box(0.55*s, 0.45*s, 0.16*s), t=(0,0,0.08*s)), 'graph'))
        P.append(_p(tf(cyl(0.22*s, 0.34*s, 4, r2=0.13*s), t=(0,0,0.3*s), rz=PI/4), 'dark'))
        P.append(_p(tf(cyl(0.08*s, 0.24*s, 8), t=(0, 0.06*s, 0.52*s)), 'graph'))
        # вогнутая к зрителю дуга из сегментов, единая высота
        Rарк = 0.66*s
        cyy = 0.5*s
        for k, aa in enumerate(np.linspace(-1.05, 1.05, 12)):
            x = Rарк*math.sin(aa)
            y = cyy - Rарк*math.cos(aa)*0.75
            hh = 0.46*s*(1.0 - 0.25*abs(aa))  # к краям ниже — «банан»
            P.append(_p(tf(box(0.17*s, 0.05*s, hh), t=(x, y, 0.8*s + 0.02*s*math.cos(aa)), rz=-aa*0.8, rx=-0.1), 'graph'))
        # красный кант по верхней кромке дуги
        path = [(Rарк*math.sin(a)*0.98, cyy - Rарк*math.cos(a)*0.75 - 0.03*s, 1.04*s) for a in np.linspace(-1.0, 1.0, 14)]
        P.append(_p(tube(np.array(path), 0.016*s, 6), 'redline'))
        # фидер-рука к зрителю
        P.append(_p(tube(np.array([(0, 0.0, 0.55*s), (0, -0.3*s, 0.66*s), (0, -0.38*s, 0.74*s)]), 0.028*s, 6), 'dark'))
        P.append(_p(tf(box(0.16*s, 0.09*s, 0.05*s), t=(0, -0.4*s, 0.76*s)), 'redline'))
    elif level == 3:  # круглая «голова» с лепестками (ref 3)
        P.append(_p(tf(cyl(0.3*s, 0.22*s, 6), t=(0,0,0.11*s)), 'graph'))
        P.append(_p(tf(torus(0.26*s, 0.02*s, 6, 6), t=(0,0,0.2*s)), 'redline'))
        P.append(_p(tf(cyl(0.2*s, 0.3*s, 14, r2=0.24*s), t=(0,0,0.4*s)), 'dark'))
        P.append(_p(tf(torus(0.21*s, 0.018*s, 18, 6), t=(0,0,0.55*s)), 'redline'))
        P.append(_p(tf(cyl(0.08*s, 0.2*s, 10), t=(0,0,0.65*s)), 'graph'))
        P.append(_p(tf(sphere(0.24*s, 18, 10), t=(0,0,0.85*s), s=(1,1,0.82)), 'graph'))
        P.append(_p(tf(torus(0.16*s, 0.015*s, 16, 6), t=(0,0,1.0*s)), 'redline'))
        for sgn in (-1, 1):  # лепестки-уши
            for k, aa in enumerate(np.linspace(-0.4, 0.4, 3)):
                P.append(_p(tf(box(0.16*s, 0.05*s, 0.34*s), t=(sgn*0.34*s, aa*0.25*s, 0.88*s), rz=sgn*0.5 + aa*0.3, rx=aa*0.4), 'dark'))
    elif level == 4:  # кольцевой массив с разрывами + спутники-поды (ref 4 + 5)
        P.append(_p(tf(box(0.5*s, 0.4*s, 0.2*s), t=(0,0,0.1*s)), 'graph'))
        P.append(_p(tf(box(0.3*s, 0.3*s, 0.12*s), t=(0,0,0.24*s)), 'dark'))
        P.append(_p(tf(box(0.12*s, 0.1*s, 0.06*s), t=(0,0,0.32*s)), 'redline'))
        yc, zc = 0.0, 0.75*s
        for a0 in (0.35, 2.45, 4.55):
            V, F = ring_seg(0.55*s, 0.05*s, yc, a0, a0 + 1.75)
            P.append((V + np.array([0, 0, zc]), F, 'graph'))
            V2, F2 = ring_seg(0.55*s, 0.018*s, yc - 0.045*s, a0 + 0.1, a0 + 1.65)
            P.append((V2 + np.array([0, 0, zc]), F2, 'redline'))
        for a0 in (1.2, 4.3):
            V, F = ring_seg(0.32*s, 0.04*s, yc, a0, a0 + 2.4)
            P.append((V + np.array([0, 0, zc]), F, 'dark'))
        # спутники-поды на внешнем кольце (реф 5)
        for a2 in (0.7, 2.0, 3.6, 5.2):
            px, pz = 0.55*s*math.cos(a2), 0.55*s*math.sin(a2)
            P.append(_p(tf(box(0.07*s, 0.07*s, 0.1*s), t=(px, yc, zc+pz), rz=0.3), 'dark'))
            P.append(_p(tf(box(0.12*s, 0.02*s, 0.05*s), t=(px, yc+0.06*s, zc+pz)), 'graph'))
            P.append(_p(tf(sphere(0.025*s, 6, 5), t=(px, yc-0.05*s, zc+pz)), 'redline'))
        P.append(_p(tf(sphere(0.08*s, 12, 7), t=(0, yc, zc)), 'graph'))
        for a2 in np.linspace(0.5, 2*PI, 4, endpoint=False):
            P.append(_p(tube(np.array([(0.07*s*math.cos(a2), yc, zc + 0.07*s*math.sin(a2)), (0.3*s*math.cos(a2), yc, zc + 0.3*s*math.sin(a2))]), 0.015*s, 5), 'dark'))
    else:  # L5: большая тарелка на восьмигранной башне + боковые панели (ref 6)
        # башня
        P.append(_p(tf(cyl(0.3*s, 0.16*s, 8), t=(0,0,0.08*s)), 'graph'))
        P.append(_p(tf(cyl(0.22*s, 0.55*s, 8), t=(0,0,0.44*s)), 'graph'))
        for zz in (0.28, 0.5, 0.66):
            P.append(_p(tf(torus(0.23*s, 0.014*s, 8, 6), t=(0,0,zz*s)), 'redline'))
        P.append(_p(tf(cyl(0.26*s, 0.12*s, 8), t=(0,0,0.76*s)), 'dark'))
        # большая тарелка вверх-к зрителю
        dish = revolve([(0.03,0.2),(0.35,0.07),(0.68,0.0),(0.72,0.025),(0.38,0.1),(0.05,0.24)], 28)
        P.append(_p(tf(dish, t=(0, 0.12*s, 0.95*s), rx=-PI/4, s=s), 'hull_b'))
        P.append(_p(tf(torus(0.68*s, 0.016*s, 30, 6), t=(0, 0.15*s, 0.97*s), rx=-PI/4), 'redline'))
        # фидер
        P.append(_p(tube(np.array([(0, 0.16*s, 1.0*s), (0, 0.38*s, 1.22*s)]), 0.018*s, 6), 'dark'))
        P.append(_p(tf(sphere(0.05*s, 8, 6), t=(0, 0.4*s, 1.24*s)), 'redline'))
        # боковые рычаги с восьмигранными панель-подами
        for sgn in (-1, 1):
            P.append(_p(tube(np.array([(sgn*0.2*s, 0, 0.6*s), (sgn*0.5*s, 0, 0.66*s)]), 0.03*s, 6), 'graph'))
            P.append(_p(tf(tf(cyl(0.17*s, 0.08*s, 8), ry=PI/2), t=(sgn*0.62*s, 0, 0.66*s)), 'graph'))
            P.append(_p(tf(tf(torus(0.15*s, 0.012*s, 8, 6), ry=PI/2), t=(sgn*(0.62+0.045)*s, 0, 0.66*s)), 'redline'))
            P.append(_p(tf(sphere(0.03*s, 6, 5), t=(sgn*0.62*s, 0, 0.78*s)), 'redline'))
    return merge(P)

def weapon_beam(level, family, seed=0):
    """Lazer: длинноствольная пушка (ref laser_3.glb).
    Phazer: тяжёлый ствол с синими светокольцами (ref laser_4)."""
    P = []
    s = 0.78 + 0.12*level
    zc = 0.5*s
    if family == 'lazer':
        # станок
        P.append(_p(tf(box(0.5*s, 0.7*s, 0.12*s), t=(0,-0.15*s,0.06*s)), 'gun_d'))
        P.append(_p(tf(box(0.16*s, 0.3*s, 0.3*s), t=(0,-0.15*s,0.25*s)), 'gun_d'))
        # ребристый конический казённик (-Y)
        P.append(_p(tf(cyl(0.19*s, 0.35*s, 14, r2=0.13*s), t=(0,-0.55*s,zc), rx=-PI/2), 'gun'))
        for k in range(4):
            P.append(_p(tf(torus((0.14+0.012*k)*s, 0.018*s, 16, 6), t=(0,(-0.44-0.07*k)*s,zc), rx=PI/2), 'gun_d'))
        # ресивер-коробка + скоба сверху
        P.append(_p(tf(box(0.24*s, 0.45*s, 0.26*s), t=(0,-0.15*s,zc)), 'gun'))
        P.append(_p(tf(box(0.06*s, 0.2*s, 0.1*s), t=(0,-0.2*s,zc+0.2*s)), 'gun_d'))
        P.append(_p(tf(helix_coil(0.15*s, 0.12*s, 2, 0.018*s), t=(0,-0.32*s,zc), rx=PI/2), 'coil'))
        # ступенчатый ствол (+Y): толстая муфта -> ствол -> глушитель
        L = (0.55 + 0.15*level)*s
        P.append(_p(tf(cyl(0.1*s, 0.25*s, 12), t=(0,0.2*s,zc), rx=PI/2), 'gun'))
        P.append(_p(tf(cyl(0.055*s, L, 10), t=(0,0.3*s+L/2,zc), rx=PI/2), 'gun_d'))
        for k in range(level):
            P.append(_p(tf(torus(0.075*s, 0.016*s, 14, 6), t=(0,(0.45+0.18*k)*s,zc), rx=PI/2), 'gun'))
        P.append(_p(tf(cyl(0.08*s, 0.22*s, 12), t=(0,0.3*s+L+0.08*s,zc), rx=PI/2), 'gun'))
        P.append(_p(tf(cyl(0.04*s, 0.06*s, 8), t=(0,0.3*s+L+0.22*s,zc), rx=PI/2), 'accent'))
        # боковая трубка
        P.append(_p(tube(np.array([(0.12*s,-0.05*s,zc-0.08*s),(0.12*s,0.35*s,zc-0.08*s)]), 0.02*s, 6), 'gun_d'))
    else:  # phazer
        # барабан-тело
        P.append(_p(tf(box(0.55*s, 0.5*s, 0.12*s), t=(0,-0.3*s,0.06*s)), 'gun_d'))
        P.append(_p(tf(cyl(0.3*s, 0.5*s, 18), t=(0,-0.3*s,zc), rx=PI/2), 'gun'))
        P.append(_p(tf(torus(0.31*s, 0.03*s, 22, 8), t=(0,-0.5*s,zc), rx=PI/2), 'gun_d'))
        # синее светокольцо на теле
        P.append(_p(tf(torus(0.305*s, 0.022*s, 22, 8), t=(0,-0.12*s,zc), rx=PI/2), 'bglow'))
        # ствол с сегментами свечения
        L = (0.5 + 0.14*level)*s
        P.append(_p(tf(cyl(0.16*s, L, 14), t=(0,-0.05*s+L/2,zc), rx=PI/2), 'gun'))
        for k in range(1+level):
            P.append(_p(tf(torus(0.165*s, 0.02*s, 18, 6), t=(0,(0.12+0.16*k)*s,zc), rx=PI/2), 'bglow'))
        # мультилинзовое дуло (4 линзы)
        P.append(_p(tf(cyl(0.19*s, 0.16*s, 14), t=(0,-0.05*s+L+0.07*s,zc), rx=PI/2), 'gun_d'))
        my = -0.05*s + L + 0.16*s
        for a in np.linspace(PI/4, 2*PI+PI/4, 4, endpoint=False):
            P.append(_p(tf(sphere(0.05*s, 8, 6), t=(0.09*s*math.cos(a), my, zc+0.09*s*math.sin(a))), 'bglow'))
        P.append(_p(tf(sphere(0.04*s, 8, 6), t=(0, my, zc)), 'bglow'))
        # верхний сенсор
        P.append(_p(tf(box(0.12*s, 0.18*s, 0.12*s), t=(0,-0.35*s,zc+0.32*s)), 'gun_d'))
        P.append(_p(tf(sphere(0.035*s, 8, 6), t=(0,-0.26*s,zc+0.34*s)), 'bglow'))
    return merge(P)

def weapon_rapid(level, family, seed=0):
    """Турель по ref laser_rapid_1: толстые орудийные поды со светолинзами
    в гранёном корпусе на ребристом пьедестале. Стволы вверх-к зрителю."""
    P = []
    s = 0.8 + 0.12*level
    glow = 'accent' if family == 'lazer' else 'bglow'
    tilt = 0.7  # подъём стволов над горизонтом
    dirv = np.array([0, math.cos(tilt), math.sin(tilt)])
    rx_axis = -(PI/2 - tilt)  # rx, отображающий ось цилиндра (+Z) в dirv
    ux = np.array([1.0, 0, 0])
    uz = np.cross(ux, dirv); uz /= np.linalg.norm(uz)  # «верх» турели
    # пьедестал: клёпаное кольцо + ребристый воротник + конус
    P.append(_p(tf(cyl(0.46*s, 0.09*s, 24), t=(0,0,0.045*s)), 'gun_d'))
    for a2 in np.linspace(0, 2*PI, 14, endpoint=False):
        P.append(_p(tf(sphere(0.02*s, 6, 5), t=(0.43*s*math.cos(a2), 0.43*s*math.sin(a2), 0.08*s)), 'gun'))
    P.append(_p(tf(cyl(0.34*s, 0.14*s, 22, r2=0.38*s), t=(0,0,0.16*s)), 'gun'))
    for zz in (0.12, 0.19):
        P.append(_p(tf(torus(0.37*s, 0.016*s, 26, 6), t=(0,0,zz*s)), 'gun_d'))
    P.append(_p(tf(cyl(0.24*s, 0.14*s, 18, r2=0.3*s), t=(0,0,0.3*s)), 'gun_d'))
    # гранёный корпус (шестигранник осью вдоль стволов)
    hc = np.array([0, -0.06*s, 0.56*s])
    P.append(_p(tf(cyl(0.32*s, 0.44*s, 6), t=tuple(hc), rx=rx_axis), 'gun'))
    P.append(_p(tf(cyl(0.335*s, 0.1*s, 6), t=tuple(hc - dirv*0.18*s), rx=rx_axis), 'gun_d'))
    # крышка-панель сверху + антенна + красные огни
    P.append(_p(tf(box(0.3*s, 0.26*s, 0.08*s), t=tuple(hc + uz*0.3*s), rx=tilt), 'gun_d'))
    P.append(_p(tf(box(0.14*s, 0.14*s, 0.05*s), t=tuple(hc + uz*0.34*s), rx=tilt), 'gun'))
    P.append(_p(tf(cyl(0.012*s, 0.3*s, 6), t=tuple(hc + uz*0.42*s - dirv*0.15*s)), 'gun_d'))
    for dd in (-0.2, 0.2):
        P.append(_p(tf(sphere(0.022*s, 6, 5), t=tuple(hc + ux*dd*s + uz*0.31*s - dirv*0.1*s)), 'coil'))
    # орудийные поды
    n_p = {1:2, 2:4, 3:6}.get(level, 4)
    if n_p == 2: grid = [(-0.13, 0.0), (0.13, 0.0)]
    elif n_p == 4: grid = [(-0.13,-0.12),(0.13,-0.12),(-0.13,0.14),(0.13,0.14)]
    else: grid = [(-0.24,-0.12),(0,-0.12),(0.24,-0.12),(-0.24,0.14),(0,0.14),(0.24,0.14)]
    pr = 0.115*s if n_p < 6 else 0.1*s
    plen = 0.5*s
    for dx, dz in grid:
        base = hc + ux*dx*s + uz*dz*s + dirv*0.2*s
        c = base + dirv*plen/2
        P.append(_p(tf(cyl(pr, plen, 14), t=tuple(c), rx=rx_axis), 'gun'))
        P.append(_p(tf(torus(pr*1.06, 0.016*s, 16, 6), t=tuple(base + dirv*plen*0.55), rx=rx_axis), 'gun_d'))
        face = base + dirv*(plen + 0.01*s)
        P.append(_p(tf(torus(pr*0.92, 0.022*s, 16, 8), t=tuple(face), rx=rx_axis), 'gun_d'))
        P.append(_p(tf(cyl(pr*0.78, 0.04*s, 14), t=tuple(face), rx=rx_axis), glow))
        P.append(_p(tf(sphere(pr*0.4, 10, 7), t=tuple(face + dirv*0.03*s)), glow))
    return merge(P)

def aux(kind, seed=0):
    P = []
    if kind == 'colony':  # по Colonizer_humans_2: блюдце на опорах + геокупол + зелёные отсеки
        zc = 0.52
        # блюдце-корпус
        saucer = revolve([(0.16,0.26),(0.5,0.16),(0.7,0.03),(0.7,-0.03),(0.48,-0.14),(0.18,-0.2)], 28)
        P.append(_p(tf(saucer, t=(0,0,zc)), 'gun'))
        P.append(_p(tf(torus(0.69, 0.025, 30, 8), t=(0,0,zc)), 'gun_d'))
        # геодезический купол
        P.append(_p(tf(dome(0.4, 20, 9), t=(0,0,zc+0.24)), 'glass'))
        for i, rr in enumerate((0.395, 0.33, 0.2)):
            P.append(_p(tf(torus(rr, 0.012, 24, 6), t=(0,0,zc+0.26+0.12*i)), 'detail'))
        for a2 in np.linspace(0, 2*PI, 8, endpoint=False):
            path = [(0.4*math.cos(t)*math.cos(a2), 0.4*math.cos(t)*math.sin(a2), zc+0.24+0.4*math.sin(t)) for t in np.linspace(0.05, PI/2, 8)]
            P.append(_p(tube(np.array(path), 0.012, 5), 'detail'))
        # кольцо модулей вокруг основания купола
        for a2 in np.linspace(PI/8, 2*PI, 6, endpoint=False):
            x, y = 0.45*math.cos(a2), 0.45*math.sin(a2)
            P.append(_p(tf(box(0.22, 0.16, 0.14), t=(x, y, zc+0.24), rz=a2), 'gun_d'))
            P.append(_p(tf(box(0.1, 0.17, 0.06), t=(x, y, zc+0.24), rz=a2), 'dark'))
        # центральный модуль с гербом (к зрителю)
        P.append(_p(tf(box(0.26, 0.18, 0.2), t=(0, 0.42, zc+0.26)), 'gun'))
        P.append(_p(tf(box(0.14, 0.04, 0.12), t=(0, 0.52, zc+0.26)), 'gun_d'))
        # бортовые отсеки с гидропоникой (зелёное нутро)
        for sgn in (-1, 1):
            bx, by = sgn*0.52, 0.28
            P.append(_p(tf(box(0.3, 0.24, 0.16), t=(bx, by, zc+0.02), rz=sgn*0.5), 'gun_d'))
            P.append(_p(tf(box(0.26, 0.2, 0.1), t=(bx+sgn*0.02, by+0.04, zc+0.02), rz=sgn*0.5), 'green'))
            for k in range(3):
                P.append(_p(tf(sphere(0.035, 8, 6), t=(bx+sgn*0.04-0.05*sgn*k, by+0.08+0.02*k, zc+0.06), s=1), 'green'))
        # нижний десантный модуль с зелёным зевом (к зрителю)
        P.append(_p(tf(box(0.3, 0.26, 0.24), t=(0, 0.28, zc-0.18)), 'gun'))
        P.append(_p(tf(box(0.22, 0.06, 0.16), t=(0, 0.42, zc-0.18)), 'green'))
        # четыре шарнирные опоры
        for a2 in (PI/4, 3*PI/4, 5*PI/4, 7*PI/4):
            cx, cy = math.cos(a2), math.sin(a2)
            hip = np.array([0.5*cx, 0.5*cy, zc-0.12])
            knee = np.array([0.75*cx, 0.75*cy, 0.24])
            foot = np.array([0.88*cx, 0.88*cy, 0.07])
            P.append(_p(tube(np.array([hip, knee]), 0.045, 8), 'gun'))
            P.append(_p(tf(sphere(0.06, 10, 7), t=tuple(knee)), 'gun_d'))
            P.append(_p(tube(np.array([knee, foot + np.array([0,0,0.03])]), 0.035, 8), 'gun'))
            P.append(_p(tf(cyl(0.1, 0.05, 12), t=tuple(foot)), 'gun_d'))
            # гидроцилиндр
            P.append(_p(tube(np.array([hip + np.array([0,0,0.14]), knee + np.array([-0.04*cx, -0.04*cy, 0.06])]), 0.018, 6), 'detail'))
        # антенна и красный огонь
        P.append(_p(tf(cyl(0.012, 0.35, 6), t=(0.15, -0.3, zc+0.55)), 'gun_d'))
        P.append(_p(tf(sphere(0.025, 6, 5), t=(0.15, -0.3, zc+0.74)), 'coil'))
    else:  # invasion — чистый гранёный корпус по InvasionModule_humans_3
        zc = 0.5

        def cross8(w, zb, zt, ch):
            """октагон-сечение (x,z), обход CCW при взгляде с +Y"""
            return [(-0.55*w, zt), (0.55*w, zt), (w, zt-ch), (w, zb+ch),
                    (0.55*w, zb), (-0.55*w, zb), (-w, zb+ch), (-w, zt-ch)]

        def loft(sections):
            """sections: [(y, [(x,z),...]), ...] от носа к корме; крышки с торцов"""
            V, F = [], []
            n = len(sections[0][1])
            for y, pts in sections:
                V += [(x, y, z) for x, z in pts]
            for i in range(len(sections)-1):
                for j in range(n):
                    a1 = i*n + j; b1 = i*n + (j+1) % n
                    a2 = (i+1)*n + j; b2 = (i+1)*n + (j+1) % n
                    F += [(a1, a2, b2), (a1, b2, b1)]
            # крышки
            c0 = len(V); V.append((0, sections[0][0], sum(z for _,z in sections[0][1])/n))
            for j in range(n):
                F.append(((j+1) % n, j, c0))
            c1 = len(V); V.append((0, sections[-1][0], sum(z for _,z in sections[-1][1])/n))
            off = (len(sections)-1)*n
            for j in range(n):
                F.append((off + j, off + (j+1) % n, c1))
            return np.array(V, float), np.array(F, int)

        # фюзеляж: одно чистое тело от носа к корме
        def sec(y, w, hgt, zlift=0.0, ch=0.35):
            zb = zc - hgt*0.45 + zlift
            zt = zc + hgt*0.55 + zlift
            return (y, cross8(w, zb, zt, ch*hgt))
        fus = loft([
            sec(0.95, 0.045, 0.05, 0.01),
            sec(0.72, 0.13, 0.1, 0.01),
            sec(0.4, 0.21, 0.17),
            sec(0.0, 0.25, 0.21),
            sec(-0.4, 0.24, 0.21),
            sec(-0.65, 0.19, 0.17),
        ])
        P.append(_p(fus, 'gun'))
        # надстройка-хребет с кабиной (задняя половина)
        spine = loft([
            (-0.08, [(-0.02, zc+0.11), (0.02, zc+0.11), (0.03, zc+0.1), (-0.03, zc+0.1)]),
            (-0.22, [(-0.07, zc+0.3), (0.07, zc+0.3), (0.09, zc+0.12), (-0.09, zc+0.12)]),
            (-0.58, [(-0.08, zc+0.32), (0.08, zc+0.32), (0.1, zc+0.12), (-0.1, zc+0.12)]),
        ])
        P.append(_p(spine, 'gun'))
        # кабина — тёмное лобовое стекло на скосе хребта
        P.append(_p(tf(box(0.11, 0.12, 0.03), t=(0, -0.16, zc+0.21), rx=-0.95), 'gun'))
        # панельные полосы
        for dy in (0.15, 0.45):
            P.append(_p(tf(box(0.3-0.12*(dy>0.3), 0.05, 0.02), t=(0, dy, zc+0.115+0.001)), 'gun'))
        # турбины прямо в кормовом срезе корпуса
        for dx in (-0.1, 0.1):
            P.append(_p(tf(tf(cyl(0.075, 0.1, 8), rz=PI/8), t=(dx, -0.66, zc+0.01), rx=PI/2), 'gun'))
            P.append(_p(tf(torus(0.078, 0.014, 16, 6), t=(dx, -0.7, zc+0.01), rx=PI/2), 'bglow'))
            P.append(_p(tf(tf(cyl(0.058, 0.025, 8), rz=PI/8), t=(dx, -0.71, zc+0.01), rx=PI/2), 'bglow'))
        # крылья-плоскости (чистые трапеции-пластины)
        for sgn in (-1, 1):
            P.append(_p(tf(box(0.42, 0.34, 0.025), t=(sgn*0.4, 0.12, zc-0.06), rz=-sgn*0.3), 'gun'))
            P.append(_p(tf(box(0.2, 0.18, 0.02), t=(sgn*0.24, 0.5, zc), rz=-sgn*0.2), 'gun'))
        # брюшной десантный отсек с синим зевом
        P.append(_p(tf(box(0.22, 0.32, 0.12), t=(0, 0.08, zc-0.16)), 'gun'))
        P.append(_p(tf(box(0.17, 0.26, 0.04), t=(0, 0.08, zc-0.23)), 'bglow'))
        # киль + красный огонь
        P.append(_p(tf(box(0.035, 0.18, 0.16), t=(0, -0.55, zc+0.4)), 'gun'))
        P.append(_p(tf(sphere(0.02, 6, 5), t=(0, -0.55, zc+0.5)), 'coil'))
    return merge(P)

def inertia_negator(seed=0):
    P = []
    zc = 0.62
    P.append(_p(tf(torus(0.48, 0.055, 34, 10), t=(0,0,zc), rx=PI/2), 'hull'))
    P.append(_p(tf(torus(0.48, 0.055, 34, 10), t=(0,0,zc), rx=PI/2, rz=PI/2), 'hull_b'))
    P.append(_p(tf(torus(0.48, 0.055, 34, 10), t=(0,0,zc)), 'gold'))
    P.append(_p(tf(sphere(0.2, 18, 10), t=(0,0,zc)), 'accent'))
    P.append(_p(tf(cyl(0.24, 0.1, 16), t=(0,0,0.05)), 'hull_b'))
    P.append(_p(tf(cyl(0.05, 0.45, 8), t=(0,0,0.28)), 'hull'))
    P.append(_p(tf(torus(0.3, 0.02, 24, 6), t=(0,0,0.1)), 'gold'))
    return merge(P)
