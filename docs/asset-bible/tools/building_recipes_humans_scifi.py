# Рецепты зданий HUMANS, стиль SCIFI — футуристическое техно по
# refs/buildings (PowerPlant_1/2, Metroplex_1, SkyNet_1, EcoBooster_1,
# ResearchCampus_1, ArtificalHidroponifier_1): белый металл и стекло,
# шпили, кольца, купола, канопе-тарелки, синее свечение (bglow), зелёные
# биомы (green/gglow). Никаких труб с дымом и ржавчины — стили не смешиваем.
# Земля z=0, здания растут в +Z.

from building_meshes import *
import numpy as np, math
PI = math.pi


def _p(vf, tag):
    return (vf[0], vf[1], tag)


def _glow_band(P, r, z, rt=0.02, tag='bglow'):
    P.append(_p(tf(torus(r, rt, 22, 6), t=(0, 0, z)), tag))


def _pylon(P, x0, y0, x1, y1, z1, r=0.05, tag='white'):
    """Изогнутая опора от земли к точке (x1,y1,z1)."""
    P.append(_p(arc_pipe((x0, y0, 0.0), (x1, y1, z1),
                         ((x0 - x1) * 0.25, (y0 - y1) * 0.25, z1 * 0.15), r),
                tag))


def _canopy_tower(P, x, y, h, r_dish, tag_body='white'):
    """Тонкая башня с чашей-канопе наверх (реф PowerPlant_humans_1)."""
    P.append(_p(tf(cyl(0.09 * h / 1.6, h, 12, r2=0.055 * h / 1.6),
                   t=(x, y, h / 2)), tag_body))
    _glow_band_at(P, x, y, 0.1 * h / 1.6, h * 0.55)
    _glow_band_at(P, x, y, 0.085 * h / 1.6, h * 0.8)
    d = dish_mesh(r_dish, depth=0.3)
    P.append(_p(tf(d, t=(x, y, h)), 'silver'))
    P.append(_p(tf(cyl(0.015, 0.3 * r_dish + 0.15, 6),
                   t=(x, y, h + 0.12)), 'silver'))


def _glow_band_at(P, x, y, r, z, tag='bglow'):
    P.append(_p(tf(torus(r, 0.018, 18, 6), t=(x, y, z)), tag))


# ============================================================ планетарные

def colony_base(level=0, seed=0):
    """Центральный шпиль с посадочным кольцом на пилонах и куполами."""
    P = []
    P.append(_p(tf(cyl(1.35, 0.22, 28, r2=1.2), t=(0, 0, 0.11)), 'white'))
    _glow_band(P, 1.28, 0.24)
    P.append(_p(spire(0.42, 3.1, 20, bulges=((0.42, 0.55), (0.12, 0.8))),
                'white'))
    for zf in (0.9, 1.5, 2.1):
        _glow_band(P, 0.42 * (1 - zf / 3.4) + 0.06, zf)
    # посадочное кольцо на пилонах
    R = 1.05
    P.append(_p(tf(torus(R, 0.09, 30, 9), t=(0, 0, 1.15)), 'silver'))
    P.append(_p(tf(torus(R, 0.025, 30, 6), t=(0, 0, 1.24)), 'bglow'))
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        _pylon(P, 1.45 * math.cos(a), 1.45 * math.sin(a),
               R * math.cos(a), R * math.sin(a), 1.1, r=0.06)
    # купола-модули у подножия
    for a in (0.5, 2.2, 4.2):
        x, y = 0.95 * math.cos(a), 0.95 * math.sin(a)
        P.append(_p(tf(cyl(0.32, 0.12, 16), t=(x, y, 0.28)), 'white'))
        P.append(_p(tf(dome(0.3, 16, 6), t=(x, y, 0.34)), 'glass'))
    P.append(_p(tf(sphere(0.07, 8, 6), t=(0, 0, 3.14)), 'bglow'))
    return merge(P)


def factory(level=0, seed=0):
    """Монолит-башня с энергополосами и наклонным кольцом-конвейером."""
    P = []
    oct8 = [(math.cos(a), math.sin(a)) for a in
            np.linspace(PI / 8, 2 * PI + PI / 8, 8, endpoint=False)]
    P.append(_p(loft_z([(0.0, [(0.85 * x, 0.7 * y) for x, y in oct8]),
                        (1.4, [(0.62 * x, 0.5 * y) for x, y in oct8]),
                        (2.3, [(0.42 * x, 0.36 * y) for x, y in oct8])]),
                'white'))
    # вертикальные энергополосы
    for a in (PI / 8 + PI / 4, PI + PI / 8 - PI / 4):
        x, y = 0.66 * math.cos(a), 0.54 * math.sin(a)
        P.append(_p(tf(box(0.08, 0.03, 1.6), t=(x * 0.98, y * 0.98, 0.95),
                       rz=a), 'bglow'))
    # наклонное кольцо-конвейер вокруг башни
    P.append(_p(tf(torus(1.0, 0.06, 28, 8), t=(0, 0, 0.85), rx=0.22), 'silver'))
    P.append(_p(tf(torus(1.0, 0.02, 28, 6), t=(0, 0, 0.92), rx=0.22), 'bglow'))
    for a in np.linspace(0.4, 2 * PI, 3, endpoint=False):
        x, y = 1.0 * math.cos(a), 1.0 * math.sin(a)
        P.append(_p(tf(box(0.2, 0.16, 0.12),
                       t=(x, y, 0.85 + 0.22 * y), rz=a), 'white'))
    # приёмные воронки-интейки на крыше
    for a in (1.1, 3.6):
        x, y = 0.26 * math.cos(a), 0.22 * math.sin(a)
        P.append(_p(tf(revolve([(0.02, 0.35), (0.16, 0.28), (0.2, 0.1),
                                (0.12, 0.0)], 12), t=(x, y, 2.28)), 'silver'))
    P.append(_p(tf(sphere(0.06, 8, 6), t=(0, 0, 2.4)), 'bglow'))
    return merge(P)


def outpost(level=0, seed=0):
    """Грибовидная башня-платформа с куполом (стиль mushroom towers)."""
    P = []
    P.append(_p(tf(cyl(0.85, 0.14, 22, r2=0.75), t=(0, 0, 0.07)), 'white'))
    P.append(_p(tf(cyl(0.3, 1.05, 16, r2=0.22), t=(0, 0, 0.66)), 'white'))
    _glow_band(P, 0.27, 0.5)
    _glow_band(P, 0.24, 0.95)
    # шляпка
    cap = revolve([(0.02, 0.32), (0.7, 0.22), (0.95, 0.08), (0.98, 0.0),
                   (0.6, -0.08), (0.24, -0.12)], 22)
    P.append(_p(tf(cap, t=(0, 0, 1.3)), 'white'))
    P.append(_p(tf(torus(0.9, 0.025, 26, 6), t=(0, 0, 1.28)), 'bglow'))
    P.append(_p(tf(dome(0.42, 18, 7), t=(0, 0, 1.6)), 'glass'))
    P.append(_p(tf(cyl(0.1, 0.1, 10), t=(0, 0, 2.0)), 'silver'))
    # малые поды вокруг основания
    for a in (0.9, 2.6, 4.6):
        x, y = 0.85 * math.cos(a), 0.85 * math.sin(a)
        P.append(_p(tf(sphere(0.2, 12, 7), t=(x, y, 0.2), s=(1, 1, 0.75)),
                    'white'))
        P.append(_p(tf(torus(0.14, 0.015, 12, 5), t=(x, y, 0.3)), 'bglow'))
    return merge(P)


def farm(level=0, seed=0):
    """Кластер стеклянных биокуполов на белых кольцах-основаниях + канопе."""
    P = []
    domes = [(-0.7, 0.35, 0.55), (0.45, 0.55, 0.45), (0.15, -0.5, 0.62),
             (-0.85, -0.6, 0.38)]
    for x, y, r in domes:
        P.append(_p(tf(cyl(r + 0.08, 0.12, 20, r2=r + 0.03), t=(x, y, 0.06)),
                    'white'))
        P.append(_p(tf(sphere(r * 0.75, 12, 7), t=(x, y, 0.12), s=(1, 1, 0.4)),
                    'green'))
        P.append(_p(tf(dome(r, 18, 7), t=(x, y, 0.12)), 'glass'))
        _glow_band_at(P, x, y, r + 0.05, 0.13)
    # переходы между куполами
    P.append(_p(bridge_tube((-0.7, 0.35, 0.14), (0.15, -0.5, 0.14), r=0.07,
                            flat=0.6), 'white'))
    P.append(_p(bridge_tube((0.45, 0.55, 0.14), (0.15, -0.5, 0.14), r=0.06,
                            flat=0.6), 'white'))
    _canopy_tower(P, 0.95, -0.35, 1.5, 0.5)
    return merge(P)


def laboratory(level=0, seed=0):
    """Тор-кольцо на пилонах над стеклянным ядром."""
    P = []
    P.append(_p(tf(cyl(1.0, 0.14, 24, r2=0.9), t=(0, 0, 0.07)), 'white'))
    # ядро
    P.append(_p(tf(dome(0.45, 18, 7), t=(0, 0, 0.14)), 'glass'))
    P.append(_p(tf(sphere(0.18, 12, 8), t=(0, 0, 0.42)), 'bglow'))
    # тор-лаборатория
    P.append(_p(tf(torus(0.72, 0.22, 28, 12), t=(0, 0, 1.05), s=1), 'white'))
    P.append(_p(tf(torus(0.72, 0.055, 28, 8), t=(0, 0, 1.18)), 'glass'))
    P.append(_p(tf(torus(0.72, 0.02, 28, 6), t=(0, 0, 0.92)), 'bglow'))
    for a in np.linspace(PI / 6, 2 * PI, 3, endpoint=False):
        _pylon(P, 1.15 * math.cos(a), 1.15 * math.sin(a),
               0.72 * math.cos(a), 0.72 * math.sin(a), 0.95, r=0.055)
    # шпиль-антенна из центра тора
    P.append(_p(tf(cyl(0.07, 1.0, 10, r2=0.02), t=(0, 0, 1.6)), 'silver'))
    P.append(_p(tf(sphere(0.05, 8, 6), t=(0, 0, 2.14)), 'bglow'))
    return merge(P)


def research_campus(level=0, seed=0):
    """Центральный шпиль + купола по кольцу с мостами (реф
    ResearchCampus_humans_1)."""
    P = []
    P.append(_p(tf(cyl(0.85, 0.16, 22, r2=0.72), t=(0, 0, 0.08)), 'white'))
    P.append(_p(spire(0.34, 2.6, 18, bulges=((0.5, 0.6), (0.18, 0.85))),
                'white'))
    for zf in (0.7, 1.35, 1.9):
        _glow_band(P, 0.34 * (1 - zf / 2.9) + 0.05, zf)
    P.append(_p(tf(sphere(0.06, 8, 6), t=(0, 0, 2.64)), 'bglow'))
    # купола-факультеты по кольцу
    for a in np.linspace(0.3, 2 * PI + 0.3, 4, endpoint=False):
        x, y = 1.25 * math.cos(a), 1.25 * math.sin(a)
        P.append(_p(tf(cyl(0.42, 0.1, 18, r2=0.38), t=(x, y, 0.05)), 'white'))
        P.append(_p(tf(sphere(0.28, 10, 6), t=(x, y, 0.1), s=(1, 1, 0.4)),
                    'green'))
        P.append(_p(tf(dome(0.36, 16, 6), t=(x, y, 0.1)), 'glass'))
        P.append(_p(bridge_tube((x * 0.35, y * 0.35, 0.3), (x * 0.75, y * 0.75, 0.2),
                                r=0.06, flat=0.6), 'white'))
    # кольцевая дорога-подсветка
    P.append(_p(tf(torus(1.55, 0.03, 34, 6), t=(0, 0, 0.03)), 'bglow'))
    return merge(P)


def megafactory(level=0, seed=0):
    """Две сходящиеся башни с светящимися мостами-конвейерами."""
    P = []
    P.append(_p(tf(cyl(1.5, 0.16, 28, r2=1.35), t=(0, 0, 0.08)), 'white'))
    _glow_band(P, 1.42, 0.18)
    for sgn in (-1, 1):
        # башня слегка наклонена к центру
        secs = []
        for t, w in ((0.0, 0.55), (0.9, 0.42), (1.8, 0.3), (2.55, 0.2)):
            xc = sgn * (0.85 - 0.28 * t / 2.55)
            secs.append((t, [(xc + w * math.cos(a) * 0.8, w * math.sin(a))
                             for a in np.linspace(PI / 8, 2 * PI + PI / 8, 8,
                                                  endpoint=False)]))
        P.append(_p(loft_z(secs), 'white'))
        # вертикальная энергополоса на внешней грани (следует наклону)
        P.append(_p(tf(box(0.06, 0.03, 1.6),
                       t=(sgn * 0.72, -0.34, 1.0), rx=0, ry=-sgn * 0.11),
                    'bglow'))
    # светящиеся мосты-конвейеры между башнями
    for z, r in ((0.9, 0.09), (1.6, 0.07), (2.25, 0.055)):
        x = 0.85 - 0.28 * z / 2.55
        P.append(_p(bridge_tube((-x, 0, z), (x, 0, z), r=r, flat=0.75),
                    'silver'))
        P.append(_p(bridge_tube((-x, 0, z + 0.02), (x, 0, z + 0.02),
                                r=r * 0.45, flat=0.7), 'bglow'))
    # интейк-воронки на вершинах
    for sgn in (-1, 1):
        P.append(_p(tf(revolve([(0.02, 0.3), (0.2, 0.22), (0.24, 0.06),
                                (0.14, 0.0)], 14),
                       t=(sgn * 0.58, 0, 2.55)), 'silver'))
    return merge(P)


def habitat(level=0, seed=0):
    """Три грибовидные жилые башни с садами на шляпках."""
    P = []
    towers = [(-0.7, -0.3, 1.5, 0.75), (0.55, 0.15, 2.1, 0.85),
              (-0.1, 0.75, 1.15, 0.6)]
    for x, y, h, rc in towers:
        P.append(_p(tf(cyl(0.42 * rc, 0.1, 16, r2=0.36 * rc), t=(x, y, 0.05)),
                    'white'))
        P.append(_p(tf(cyl(0.2 * rc, h, 14, r2=0.15 * rc), t=(x, y, h / 2)),
                    'white'))
        _glow_band_at(P, x, y, 0.19 * rc, h * 0.4)
        _glow_band_at(P, x, y, 0.17 * rc, h * 0.75)
        cap = revolve([(0.02, 0.16), (0.6 * rc, 0.1), (0.82 * rc, 0.02),
                       (0.85 * rc, -0.04), (0.5 * rc, -0.1), (0.2 * rc, -0.12)],
                      18)
        P.append(_p(tf(cap, t=(x, y, h + 0.1)), 'white'))
        # сад на шляпке + стеклянный поручень
        P.append(_p(tf(cyl(0.6 * rc, 0.05, 16), t=(x, y, h + 0.27)), 'green'))
        P.append(_p(tf(torus(0.68 * rc, 0.015, 20, 5), t=(x, y, h + 0.33)),
                    'glass'))
        P.append(_p(tf(torus(0.8 * rc, 0.02, 20, 5), t=(x, y, h + 0.05)),
                    'bglow'))
    # мост между двумя большими
    P.append(_p(bridge_tube((-0.7, -0.3, 1.1), (0.55, 0.15, 1.1), r=0.06,
                            flat=0.65), 'white'))
    return merge(P)


def hydroponifier(level=0, seed=0):
    """Башня-оранжерея: стеклянный цилиндр с зелёной спиралью роста
    (реф ArtificalHidroponifier_humans_1)."""
    P = []
    P.append(_p(tf(cyl(0.95, 0.14, 24, r2=0.85), t=(0, 0, 0.07)), 'white'))
    P.append(_p(tf(cyl(0.4, 0.25, 16, r2=0.34), t=(0, 0, 0.26)), 'white'))
    # стеклянный ствол с зелёной спиралью внутри
    P.append(_p(tf(cyl(0.3, 1.6, 18), t=(0, 0, 1.2)), 'glass'))
    P.append(_p(tf(helix_coil(0.2, 1.45, 4.5, 0.055, 18, 7), t=(0, 0, 1.2)),
                'green'))
    P.append(_p(tf(cyl(0.05, 1.55, 8), t=(0, 0, 1.2)), 'silver'))
    # белые рёбра-стойки вокруг стекла
    for a in np.linspace(0, 2 * PI, 4, endpoint=False):
        x, y = 0.33 * math.cos(a), 0.33 * math.sin(a)
        P.append(_p(tf(box(0.07, 0.05, 1.6), t=(x, y, 1.2), rz=a), 'white'))
    # корона-раструб
    P.append(_p(tf(revolve([(0.05, 0.45), (0.42, 0.3), (0.5, 0.05),
                            (0.32, 0.0)], 16), t=(0, 0, 2.0)), 'white'))
    _glow_band(P, 0.44, 2.28, tag='gglow')
    # купола-грядки у подножия
    for a in (0.7, 2.5, 4.3):
        x, y = 0.72 * math.cos(a), 0.72 * math.sin(a)
        P.append(_p(tf(sphere(0.2, 10, 6), t=(x, y, 0.12), s=(1, 1, 0.5)),
                    'green'))
        P.append(_p(tf(dome(0.26, 14, 5), t=(x, y, 0.12)), 'glass'))
    _glow_band(P, 0.9, 0.16)
    return merge(P)


def metroplex(level=0, seed=0):
    """Мегаполис: главный шпиль, малые шпили, алмазные сады-поды на опорах,
    кольцевая эстакада (реф Metroplex_humans_1)."""
    P = []
    P.append(_p(tf(cyl(1.6, 0.14, 30, r2=1.5), t=(0, 0, 0.07)), 'white'))
    P.append(_p(spire(0.45, 3.5, 20, bulges=((0.55, 0.5), (0.3, 0.75),
                                             (0.1, 0.9))), 'white'))
    for zf in (0.6, 1.4, 2.2, 2.9):
        _glow_band(P, 0.45 * (1 - zf / 3.8) + 0.05, zf)
    P.append(_p(tf(sphere(0.07, 8, 6), t=(0, 0, 3.55)), 'bglow'))
    # малые шпили
    for a, h in ((1.1, 1.9), (3.4, 1.5), (5.2, 2.2)):
        x, y = 1.05 * math.cos(a), 1.05 * math.sin(a)
        P.append(_p(tf(spire(0.2, h, 14, bulges=((0.35, 0.65),)), t=(x, y, 0)),
                    'white'))
        _glow_band_at(P, x, y, 0.14, h * 0.45)
    # алмазные сады-поды
    for a in (0.2, 2.4):
        x, y = 1.45 * math.cos(a), 1.45 * math.sin(a)
        P.append(_p(tf(cyl(0.05, 0.9, 8), t=(x, y, 0.45)), 'silver'))
        P.append(_p(tf(octahedron(0.3, 1.4), t=(x, y, 1.15)), 'glass'))
        P.append(_p(tf(sphere(0.16, 10, 6), t=(x, y, 1.15)), 'green'))
        P.append(_p(tf(torus(0.3, 0.018, 4, 5), t=(x, y, 1.15)), 'silver'))
    # кольцевая эстакада
    P.append(_p(tf(torus(1.35, 0.05, 34, 7), t=(0, 0, 0.35)), 'white'))
    P.append(_p(tf(torus(1.35, 0.018, 34, 5), t=(0, 0, 0.41)), 'bglow'))
    for a in np.linspace(0.5, 2 * PI, 6, endpoint=False):
        P.append(_p(tf(cyl(0.035, 0.33, 6),
                       t=(1.35 * math.cos(a), 1.35 * math.sin(a), 0.17)),
                    'white'))
    return merge(P)


def power_plant(level=0, seed=0):
    """Светящийся купол-реактор + башни-канопе + кольцевая стена
    (реф PowerPlant_humans_1/2)."""
    P = []
    P.append(_p(tf(cyl(1.05, 0.16, 24, r2=0.95), t=(0, 0, 0.08)), 'white'))
    glass, frame = geodome(0.8)
    P.append(_p(tf(sphere(0.4, 16, 10), t=(0, 0, 0.35)), 'accent'))
    P.append(_p(tf(glass, t=(0, 0, 0.16)), 'glass'))
    P.append(_p(tf(frame, t=(0, 0, 0.16)), 'silver'))
    _glow_band(P, 0.98, 0.18)
    # три башни-канопе вокруг
    for a in np.linspace(PI / 2, 2 * PI + PI / 2, 3, endpoint=False):
        x, y = 1.45 * math.cos(a), 1.45 * math.sin(a)
        _canopy_tower(P, x, y, 2.0, 0.55)
    # энерго-жёлоб от купола к башням
    for a in np.linspace(PI / 2, 2 * PI + PI / 2, 3, endpoint=False):
        x, y = 1.45 * math.cos(a), 1.45 * math.sin(a)
        P.append(_p(bridge_tube((x * 0.55, y * 0.55, 0.12), (x, y, 0.1),
                                r=0.05, flat=0.5), 'silver'))
        P.append(_p(bridge_tube((x * 0.55, y * 0.55, 0.16), (x, y, 0.14),
                                r=0.022, flat=0.5), 'bglow'))
    return merge(P)


def sky_net(level=0, seed=0):
    """Шпиль со спиральной лентой и светящимися сферами-узлами
    (реф SkyNet-humans_1)."""
    P = []
    P.append(_p(tf(cyl(0.9, 0.14, 22, r2=0.78), t=(0, 0, 0.07)), 'white'))
    P.append(_p(spire(0.36, 3.3, 18, bulges=((0.45, 0.6), (0.14, 0.85))),
                'white'))
    # спиральная лента вокруг шпиля
    n = 90
    t = np.linspace(0, 3.6 * PI, n)
    z = np.linspace(0.2, 2.9, n)
    rr = 0.5 * (1 - z / 3.8) + 0.14
    path = np.stack([rr * np.cos(t), rr * np.sin(t), z], -1)
    P.append(_p(tube(path, 0.05, 8), 'silver'))
    P.append(_p(tube(path + np.array([0, 0, 0.06]), 0.018, 6), 'bglow'))
    # светящиеся сферы-узлы сети
    for zf, r in ((1.15, 0.16), (2.05, 0.13)):
        P.append(_p(tf(sphere(r, 12, 8), t=(0, 0, zf)), 'bglow'))
        P.append(_p(tf(torus(r + 0.05, 0.015, 16, 5), t=(0, 0, zf)), 'silver'))
    # антенное трио на вершине
    for a in np.linspace(0, 2 * PI, 3, endpoint=False):
        x, y = 0.1 * math.cos(a), 0.1 * math.sin(a)
        P.append(_p(tf(cyl(0.012, 0.5, 6), t=(x, y, 3.5)), 'silver'))
    P.append(_p(tf(sphere(0.06, 8, 6), t=(0, 0, 3.8)), 'bglow'))
    # приёмные тарелки на базе
    for a in (0.8, 2.9, 4.7):
        x, y = 0.68 * math.cos(a), 0.68 * math.sin(a)
        P.append(_p(tf(dish_mesh(0.2), t=(x, y, 0.16), rx=-PI / 5, rz=a),
                    'silver'))
    return merge(P)


def eco_booster(level=0, seed=0):
    """Цветок-лотос: лепестки вокруг светящегося био-ядра
    (реф EcoBooster_humans_1)."""
    P = []
    P.append(_p(tf(cyl(1.1, 0.18, 26, r2=0.95), t=(0, 0, 0.09)), 'white'))
    P.append(_p(tf(torus(1.0, 0.03, 28, 6), t=(0, 0, 0.2)), 'gglow'))
    # ядро
    P.append(_p(tf(cyl(0.3, 0.5, 14, r2=0.24), t=(0, 0, 0.43)), 'white'))
    P.append(_p(tf(sphere(0.34, 16, 10), t=(0, 0, 0.95)), 'gglow'))
    P.append(_p(tf(torus(0.4, 0.02, 20, 6), t=(0, 0, 0.95), rx=PI / 3), 'silver'))
    P.append(_p(tf(torus(0.4, 0.02, 20, 6), t=(0, 0, 0.95), rx=-PI / 3), 'silver'))
    # лепестки двумя ярусами
    for ring, (rr, tilt, sc, z0) in enumerate((((0.68, 0.75, 1.0, 0.22)),
                                               ((0.42, 0.42, 1.3, 0.28)))):
        n = 6
        for a in np.linspace(ring * PI / 6, 2 * PI + ring * PI / 6, n,
                             endpoint=False):
            x, y = rr * math.cos(a), rr * math.sin(a)
            petal = tf(dome(0.3, 12, 6), s=(0.38, 1.0, 2.3 * sc))
            petal = tf(petal, rx=tilt, rz=a - PI / 2)
            P.append(_p(tf(petal, t=(x, y, z0)), 'white'))
    # водопадные жёлобы от базы
    for a in np.linspace(PI / 6, 2 * PI, 3, endpoint=False):
        x, y = 1.35 * math.cos(a), 1.35 * math.sin(a)
        P.append(_p(bridge_tube((x * 0.7, y * 0.7, 0.14), (x, y, 0.02),
                                r=0.05, flat=0.5), 'white'))
        P.append(_p(bridge_tube((x * 0.7, y * 0.7, 0.17), (x, y, 0.05),
                                r=0.02, flat=0.5), 'gglow'))
    return merge(P)


def terraforming(level=0, seed=0):
    """Атмосферное кольцо на арочных пилонах над световым столбом."""
    P = []
    P.append(_p(tf(cyl(1.0, 0.14, 24, r2=0.9), t=(0, 0, 0.07)), 'white'))
    # световой столб
    P.append(_p(tf(cyl(0.14, 1.7, 12), t=(0, 0, 0.95)), 'bglow'))
    P.append(_p(tf(cyl(0.3, 0.3, 16, r2=0.2), t=(0, 0, 0.29)), 'white'))
    # кольцо-генератор
    R = 0.95
    P.append(_p(tf(torus(R, 0.11, 30, 10), t=(0, 0, 1.8)), 'white'))
    P.append(_p(tf(torus(R, 0.03, 30, 6), t=(0, 0, 1.94)), 'bglow'))
    P.append(_p(tf(torus(R * 0.7, 0.025, 26, 6), t=(0, 0, 1.8)), 'silver'))
    # арочные пилоны
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        x, y = math.cos(a), math.sin(a)
        P.append(_p(arc_pipe((1.5 * x, 1.5 * y, 0.0), (R * x, R * y, 1.72),
                             (-0.55 * x, -0.55 * y, 0.55), 0.07), 'white'))
    # туманные диффузоры на кольце
    for a in np.linspace(0, 2 * PI, 6, endpoint=False):
        x, y = R * math.cos(a), R * math.sin(a)
        P.append(_p(tf(revolve([(0.02, 0.16), (0.1, 0.1), (0.12, 0.0)], 10),
                       t=(x, y, 1.9)), 'silver'))
    P.append(_p(tf(sphere(0.1, 10, 7), t=(0, 0, 1.85)), 'bglow'))
    return merge(P)


# ============================================================ орбитальные
# Центр ~z=1.0, «рабочее» направление орудий +Y.

def orb_dock(level=1, seed=0):
    """Чистое кольцо-верфь: гладкий обод, четыре стапель-пилона, свето-полоса."""
    P = []
    s = 0.72 + 0.16 * level
    zc = 1.0
    R = 0.85 * s
    P.append(_p(tf(torus(R, 0.1 * s, 32, 10), t=(0, 0, zc)), 'white'))
    P.append(_p(tf(torus(R, 0.032 * s, 32, 6), t=(0, 0, zc + 0.09 * s)), 'bglow'))
    # плоское техническое кольцо внутри
    P.append(_p(tf(torus(R * 0.78, 0.05 * s, 28, 6), t=(0, 0, zc)), 'silver'))
    # стапель-пилоны внутрь
    for a in np.linspace(PI / 4, 2 * PI, 4, endpoint=False):
        x, y = math.cos(a), math.sin(a)
        P.append(_p(tube(np.array([(R * x, R * y, zc),
                                   (0.3 * s * x, 0.3 * s * y, zc)]),
                         0.045 * s, 8), 'white'))
        P.append(_p(tf(box(0.16 * s, 0.1 * s, 0.16 * s),
                       t=(0.45 * s * x, 0.45 * s * y, zc), rz=a), 'silver'))
        P.append(_p(tf(sphere(0.03 * s, 6, 5),
                       t=(0.32 * s * x, 0.32 * s * y, zc + 0.08 * s)), 'bglow'))
    # диспетчерская сфера
    P.append(_p(tf(sphere(0.17 * s, 14, 9), t=(0, 0, zc)), 'white'))
    P.append(_p(tf(torus(0.2 * s, 0.015 * s, 16, 5), t=(0, 0, zc)), 'bglow'))
    if level >= 3:
        P.append(_p(tf(torus(R, 0.06 * s, 32, 8), t=(0, 0, zc + 0.35 * s)),
                    'silver'))
    if level >= 4:
        P.append(_p(tf(torus(R, 0.06 * s, 32, 8), t=(0, 0, zc - 0.35 * s)),
                    'silver'))
        for a in np.linspace(0, 2 * PI, 6, endpoint=False):
            P.append(_p(tf(cyl(0.02 * s, 0.7 * s, 6),
                           t=(R * math.cos(a), R * math.sin(a), zc)), 'white'))
    return merge(P)


def orb_shield(level=1, seed=0):
    """Гиро-щит: вложенные кольца-гимбалы вокруг светящегося ядра."""
    P = []
    s = 0.78 + 0.14 * level
    zc = 1.0
    P.append(_p(tf(sphere(0.24 * s, 16, 10), t=(0, 0, zc)), 'bglow'))
    P.append(_p(tf(sphere(0.3 * s, 12, 8), t=(0, 0, zc)), 'glass'))
    rings = [(0.95, PI / 2, 0.0), (0.75, 0.0, 0.0)]
    if level >= 2:
        rings.append((0.55, PI / 2, PI / 2))
    for rr, rx, rz in rings:
        P.append(_p(tf(torus(rr * s, 0.05 * s, 30, 8), t=(0, 0, zc),
                       rx=rx, rz=rz), 'white'))
        P.append(_p(tf(torus(rr * s, 0.018 * s, 30, 6), t=(0, 0, zc),
                       rx=rx, rz=rz), 'bglow'))
    # полюсные эмиттеры
    for sgn in (-1, 1):
        P.append(_p(tf(cyl(0.05 * s, 0.2 * s, 8, r2=0.02 * s),
                       t=(0, 0, zc + sgn * 0.4 * s)), 'silver'))
        P.append(_p(tf(sphere(0.035 * s, 6, 5),
                       t=(0, 0, zc + sgn * 0.52 * s)), 'bglow'))
    if level >= 3:
        P.append(_p(tf(torus(1.1 * s, 0.02 * s, 34, 6), t=(0, 0, zc),
                       rx=PI / 3), 'bglow'))
    return merge(P)


def orb_laser(level=1, seed=0):
    """Веретено-лазер: гладкий корпус, фокусирующие кольца, эмиттер в +Y."""
    P = []
    s = 0.75 + 0.14 * level
    zc = 1.0
    body = revolve([(0.02, 0.55), (0.2, 0.4), (0.28, 0.05), (0.24, -0.3),
                    (0.1, -0.55), (0.02, -0.6)], 20)
    P.append(_p(tf(tf(body, s=s), t=(0, 0, zc), rx=-PI / 2), 'white'))
    # фокусирующие кольца перед эмиттером
    for k in range(2 + level):
        y = (0.6 + 0.2 * k) * s
        rr = (0.16 - 0.025 * k) * s
        P.append(_p(tf(torus(rr, 0.02 * s, 18, 6), t=(0, y, zc), rx=PI / 2),
                    'silver'))
        P.append(_p(tf(torus(rr * 0.7, 0.012 * s, 16, 5), t=(0, y, zc),
                       rx=PI / 2), 'bglow'))
    P.append(_p(tf(sphere(0.05 * s, 8, 6),
                   t=(0, (0.6 + 0.2 * (1 + level)) * s, zc)), 'bglow'))
    # радиаторные плавники сзади
    for a in np.linspace(0, 2 * PI, 4, endpoint=False):
        fin = tf(box(0.04 * s, 0.35 * s, 0.3 * s), t=(0, -0.45 * s, zc))
        V, F = fin
        c, sn = math.cos(a), math.sin(a)
        M = np.array([[c, 0, -sn], [0, 1, 0], [sn, 0, c]])
        V = (V - np.array([0, 0, zc])) @ M.T + np.array([0, 0, zc])
        P.append((V, F, 'silver'))
    P.append(_p(tf(torus(0.3 * s, 0.02 * s, 20, 6), t=(0, -0.1 * s, zc),
                   rx=PI / 2), 'bglow'))
    return merge(P)


def orb_phazer(level=1, seed=0):
    """Три-шип: сфера-хаб с наклонёнными вперёд иглами-эмиттерами
    (мотив OrbitalPhaserRapid_humans_1)."""
    P = []
    s = 0.8 + 0.13 * level
    zc = 1.0
    P.append(_p(tf(sphere(0.3 * s, 18, 11), t=(0, 0, zc)), 'white'))
    P.append(_p(tf(torus(0.32 * s, 0.02 * s, 22, 6), t=(0, 0, zc)), 'bglow'))
    n_sp = 2 + level
    for a in np.linspace(0, 2 * PI, n_sp, endpoint=False):
        x, z = 0.24 * s * math.cos(a), 0.24 * s * math.sin(a)
        tipd = np.array([0.5 * math.cos(a), 1.6, 0.5 * math.sin(a)])
        tipd /= np.linalg.norm(tipd)
        base = np.array([x, 0.1 * s, zc + z])
        tip = base + tipd * 0.85 * s
        P.append(_p(tube(np.stack([base, base + tipd * 0.5 * s, tip]),
                         0.05 * s, 8), 'white'))
        P.append(_p(tf(sphere(0.045 * s, 8, 6), t=tuple(tip)), 'pglow'))
    # кормовой стабилизатор и энергокольцо
    P.append(_p(tf(cyl(0.1 * s, 0.4 * s, 10, r2=0.05 * s),
                   t=(0, -0.4 * s, zc), rx=-PI / 2), 'silver'))
    P.append(_p(tf(torus(0.2 * s, 0.02 * s, 18, 6), t=(0, -0.25 * s, zc),
                   rx=PI / 2), 'pglow'))
    return merge(P)


def orb_phazer_rapid(level=1, seed=0):
    """Массив игл: хаб + корона эмиттеров, центральная линза залпа."""
    P = []
    s = 0.85 + 0.13 * level
    zc = 1.0
    P.append(_p(tf(cyl(0.3 * s, 0.3 * s, 8), t=(0, 0, zc), rx=PI / 2), 'white'))
    P.append(_p(tf(torus(0.3 * s, 0.025 * s, 22, 6), t=(0, 0.12 * s, zc),
                   rx=PI / 2), 'pglow'))
    n_sp = 4 + 2 * level
    for a in np.linspace(0, 2 * PI, n_sp, endpoint=False):
        x, z = 0.26 * s * math.cos(a), 0.26 * s * math.sin(a)
        base = np.array([x, 0.15 * s, zc + z])
        tipd = np.array([0.35 * math.cos(a), 1.7, 0.35 * math.sin(a)])
        tipd /= np.linalg.norm(tipd)
        tip = base + tipd * 0.65 * s
        P.append(_p(tube(np.stack([base, tip]), 0.03 * s, 6), 'silver'))
        P.append(_p(tf(sphere(0.028 * s, 6, 5), t=tuple(tip)), 'pglow'))
    # центральная линза залпа
    P.append(_p(tf(cyl(0.12 * s, 0.06 * s, 12), t=(0, 0.18 * s, zc),
                   rx=PI / 2), 'pglow'))
    # кормовые панели
    for sgn in (-1, 1):
        P.append(_p(tf(box(0.5 * s, 0.02 * s, 0.22 * s),
                       t=(sgn * 0.45 * s, -0.25 * s, zc), rz=sgn * 0.3), 'dark'))
        P.append(_p(tube(np.array([(0, -0.15 * s, zc),
                                   (sgn * 0.3 * s, -0.22 * s, zc)]),
                         0.02 * s, 5), 'silver'))
    return merge(P)


# ============================================================ пропсы

def prop_blocks(variant=1, seed=0):
    """Аккуратно-хаотичные белые капсулы-контейнеры."""
    P = []
    rng = np.random.default_rng(seed + variant * 23)
    tags = ('white', 'silver', 'white', 'dark')
    for k in range(5 + variant * 2):
        r = rng.uniform(0.07, 0.12)
        L = rng.uniform(0.25, 0.5)
        x, y = rng.uniform(-0.45, 0.45, 2)
        a = rng.uniform(0, PI)
        capsule = combine([tf(cyl(r, L, 10), rx=PI / 2),
                           tf(sphere(r, 10, 6), t=(0, L / 2, 0)),
                           tf(sphere(r, 10, 6), t=(0, -L / 2, 0))])
        P.append(_p(tf(capsule, t=(x, y, r), rz=a), tags[k % len(tags)]))
    P.append(_p(tf(torus(0.09, 0.012, 12, 5),
                   t=(rng.uniform(-0.3, 0.3), rng.uniform(-0.3, 0.3), 0.02)),
                'bglow'))
    return merge(P)


def prop_tanks(level=0, seed=0):
    """Белые сферы-резервуары на кольцевых ложементах."""
    P = []
    for (x, y, r) in ((-0.25, 0.1, 0.22), (0.22, 0.18, 0.17), (0.05, -0.25, 0.13)):
        P.append(_p(tf(cyl(r * 0.8, 0.06, 12), t=(x, y, 0.03)), 'silver'))
        P.append(_p(tf(sphere(r, 14, 9), t=(x, y, r + 0.05)), 'white'))
        P.append(_p(tf(torus(r * 0.9, 0.015, 16, 5), t=(x, y, r + 0.05)),
                    'bglow'))
    P.append(_p(tube(np.array([(-0.25, 0.1, 0.05), (0.22, 0.18, 0.05)]),
                     0.02, 6), 'silver'))
    return merge(P)


def prop_pipes(level=0, seed=0):
    """Энерго-кондуит: серебристая магистраль со свето-кольцами."""
    P = []
    path = np.array([(-0.55, -0.05, 0.1), (-0.15, 0.0, 0.1), (0.15, 0.05, 0.16),
                     (0.5, 0.1, 0.16)])
    P.append(_p(tube(path, 0.05, 10), 'silver'))
    for xf in (0.2, 0.55, 0.85):
        pt = path[0] + (path[-1] - path[0]) * xf
        P.append(_p(tf(torus(0.07, 0.014, 12, 5), t=tuple(pt), rx=0, ry=PI / 2),
                    'bglow'))
    P.append(_p(tf(box(0.2, 0.2, 0.18), t=(-0.5, 0.2, 0.09)), 'white'))
    P.append(_p(tf(sphere(0.05, 8, 6), t=(0.5, 0.1, 0.24)), 'bglow'))
    return merge(P)


def prop_mast(level=0, seed=0):
    """Тонкий шпиль-антенна со световым наконечником."""
    P = []
    P.append(_p(tf(cyl(0.12, 0.08, 12, r2=0.09), t=(0, 0, 0.04)), 'white'))
    P.append(_p(spire(0.05, 1.1, 10), 'silver'))
    _glow_band(P, 0.045, 0.35)
    _glow_band(P, 0.035, 0.7)
    P.append(_p(tf(sphere(0.035, 8, 6), t=(0, 0, 1.14)), 'bglow'))
    for a in np.linspace(0, 2 * PI, 3, endpoint=False):
        P.append(_p(tf(dish_mesh(0.07), t=(0.06 * math.cos(a),
                                           0.06 * math.sin(a), 0.5),
                       ry=PI / 2.5, rz=a), 'white'))
    return merge(P)


def prop_pad(level=0, seed=0):
    """Круглая посадочная площадка со светящимся кольцом."""
    P = []
    P.append(_p(tf(cyl(0.6, 0.06, 24, r2=0.55), t=(0, 0, 0.03)), 'white'))
    P.append(_p(tf(torus(0.48, 0.018, 26, 5), t=(0, 0, 0.07)), 'bglow'))
    P.append(_p(tf(cyl(0.12, 0.02, 12), t=(0, 0, 0.075)), 'silver'))
    P.append(_p(tf(cyl(0.05, 0.35, 8, r2=0.03), t=(0.62, -0.25, 0.17)), 'white'))
    P.append(_p(tf(sphere(0.03, 6, 5), t=(0.62, -0.25, 0.38)), 'bglow'))
    return merge(P)
