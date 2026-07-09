# Рецепты CORE v2 — «1 в 1» по иконкам Ascendancy 1995.
# Ориентация: сопла двигателей смотрят на зрителя (-Y+X в изометрии).

from device_meshes import *
import numpy as np, math
PI = math.pi

def _p(vf, tag): return (vf[0], vf[1], tag)

def platform(size=1.6, with_platform=True):
    if not with_platform: return []
    return [_p(tf(box(size, size, 0.1), t=(0,0,0.05)), 'plat'),
            _p(tf(box(size*0.82, size*0.82, 0.07), t=(0,0,0.14)), 'graph')]

def nozzle(pos, direction_rz, r=0.22, tag_body='white'):
    """Сопло: светлый раструб + тёмное жерло + лопатки + пламя (+Y при rz=PI)."""
    P = []
    bell = revolve([(0.38*r,0.02),(0.5*r,0.25*r),(0.75*r,0.6*r),(0.98*r,1.05*r),(1.06*r,1.15*r),(0.95*r,1.17*r),(0.7*r,0.64*r),(0.45*r,0.28*r),(0.34*r,0.06)], 20)
    P.append(_p(tf(bell, t=pos, rx=PI/2, rz=direction_rz), tag_body))
    P.append(_p(tf(tf(cyl(0.34*r, 0.06*r, 14), t=(0,0,0.03*r)), t=pos, rx=PI/2, rz=direction_rz), 'dark'))
    for a in np.linspace(0, 2*PI, 8, endpoint=False):
        blade = tf(box(0.045*r, 0.5*r, 0.4*r), t=(0.42*r*math.cos(a), 0.42*r*math.sin(a), 0.3*r), rz=a)
        P.append(_p(tf(blade, t=pos, rx=PI/2, rz=direction_rz), 'detail'))
    flame = revolve([(0.01,0.15*r),(0.42*r,0.65*r),(0.28*r,1.5*r),(0.01,2.6*r)], 12)
    P.append(_p(tf(flame, t=pos, rx=PI/2, rz=direction_rz), 'flame'))
    return P

# --- ENGINE: Tonklin Motor / Ion Banger / Graviton Projector ---------------
def engine(level, seed=0, with_platform=True):
    P = platform(1.7, with_platform)
    rz = PI  # раструб раскрывается в +Y (на зрителя)
    n_pipes = 2 + (level >= 2)
    for i in range(n_pipes):
        x = (i - (n_pipes-1)/2) * 0.4
        path = np.array([(x, 0.45, 0.42), (x, 0.1, 0.46), (x, -0.25, 0.55), (x, -0.5, 0.72)])
        P.append(_p(tube(path, 0.16, 14), 'white'))
        P.append(_p(tf(sphere(0.19, 14, 8), t=(x, -0.5, 0.74)), 'white'))
        P += nozzle((x, 0.5, 0.42), rz, r=0.2, tag_body='hull_b')
    n_coil = 3 + level
    for i in range(n_coil):
        y = 0.15 - i * 0.55/n_coil
        P.append(_p(tf(helix_coil(0.1, 0.44*n_pipes, 6, 0.03), t=(0, y, 0.85), ry=PI/2), 'coil'))
    P.append(_p(tf(box(0.44*n_pipes, 0.6, 0.07), t=(0, -0.12, 0.72)), 'coil2'))
    if level >= 2:
        P.append(_p(tf(helix_coil(0.09, 0.5, 5, 0.028), t=(0.45*(n_pipes-1)/2+0.25, -0.2, 0.6), rx=PI/2.4), 'coil2'))
    if level >= 3:
        P.append(_p(tf(sphere(0.15, 14, 8), t=(0, -0.55, 1.0)), 'blue'))
        P.append(_p(tf(torus(0.2, 0.03, 20, 8), t=(0, -0.55, 1.0), rx=PI/3), 'gold'))
    return merge(P)

# --- STAR LANE DRIVE: горизонтальный драйв, обмотанный трубами --------------
def star_lane(level, seed=0, with_platform=True):
    P = platform(1.7, with_platform)
    zc = 0.55
    P.append(_p(tf(cyl(0.3, 1.0, 18), t=(0, -0.05, zc), rx=PI/2), 'white'))
    P.append(_p(tf(sphere(0.3, 16, 9), t=(0, -0.55, zc)), 'white'))
    col = 'blue' if level == 1 else ('teal' if level == 2 else 'coil')
    rng = np.random.default_rng(level*13)
    for i in range(4 + level):
        a0 = rng.uniform(0, 2*PI)
        path = []
        for t in np.linspace(0, 1.6*PI, 26):
            rr = 0.38 + 0.05*math.sin(3*t + a0)
            path.append((rr*math.cos(t+a0), 0.28*math.sin(0.8*t + a0) - 0.05, zc + rr*math.sin(t+a0)))
        P.append(_p(tube(np.array(path), 0.075, 10), col if i % 2 == 0 else 'white'))
    P += nozzle((0, 0.52, zc), PI, r=0.24, tag_body='hull_b')
    return merge(P)

# --- GENERATOR: 1в1 по референсам -------------------------------------------
def generator(level, seed=0, with_platform=True):
    P = platform(1.6, with_platform)
    if level == 1:  # Proton Shaver
        P.append(_p(tf(cyl(0.06, 1.25, 10), t=(0,0,0.75)), 'hull'))
        for z in (0.45, 0.75, 1.05):
            P.append(_p(tf(helix_coil(0.16, 0.24, 5, 0.04), t=(0,0,z)), 'coil'))
        P.append(_p(tf(sphere(0.11, 12, 7), t=(0,0,1.42)), 'blue'))
        for dx, dy in ((0.52,0.52),(-0.52,0.52),(0.52,-0.52),(-0.52,-0.52)):
            P.append(_p(tf(cyl(0.045, 0.5, 8), t=(dx,dy,0.4)), 'hull'))
            P.append(_p(tf(helix_coil(0.1, 0.2, 4, 0.032), t=(dx,dy,0.48)), 'coil'))
            P.append(_p(tf(sphere(0.065, 10, 6), t=(dx,dy,0.72)), 'blue'))
            P.append(_p(arc_pipe((dx,dy,0.3),(0,0,0.4),(0,0,0.12), 0.025), 'gold'))
    elif level == 2:  # Subatomic Scoop: конус в чешуе + белая воронка
        P.append(_p(tf(cyl(0.55, 0.35, 22, r2=0.42), t=(0,0,0.37)), 'blue'))
        P.append(_p(tf(cyl(0.42, 0.4, 22, r2=0.22), t=(0,0,0.75)), 'teal'))
        P.append(_p(tf(cyl(0.14, 0.25, 14), t=(0,0,1.05)), 'hull'))
        P.append(_p(tf(revolve([(0.1,0.0),(0.48,0.3),(0.54,0.32),(0.5,0.34),(0.16,0.12),(0.12,0.14),(0.08,0.06)], 26), t=(0,0,1.1)), 'white'))
        for a in np.linspace(0, 2*PI, 4, endpoint=False):
            x, y = 0.5*math.cos(a), 0.5*math.sin(a)
            P.append(_p(tf(helix_coil(0.075, 0.32, 4, 0.028), t=(x,y,0.4), rx=0.3*math.sin(a), ry=0.3*math.cos(a)), 'coil'))
    elif level == 3:  # Quark Express: тумба + жёлтый пояс + Y-развилка с катушками
        P.append(_p(tf(cyl(0.58, 0.4, 24), t=(0,0,0.38)), 'blue'))
        P.append(_p(tf(torus(0.56, 0.06, 30, 10), t=(0,0,0.3)), 'gold'))
        P.append(_p(tf(torus(0.5, 0.045, 28, 8), t=(0,0,0.55)), 'gold'))
        P.append(_p(tf(sphere(0.46, 20, 11), t=(0,0,0.8), s=(1,1,0.7)), 'teal'))
        for sgn in (-1, 1):
            P.append(_p(tf(cyl(0.15, 0.55, 14), t=(sgn*0.38,0,1.3), ry=sgn*PI/4.5), 'white'))
            P.append(_p(tf(helix_coil(0.18, 0.45, 5, 0.038), t=(sgn*0.4,0,1.32), ry=sgn*PI/4.5), 'coil'))
            P.append(_p(tf(cyl(0.17, 0.06, 14), t=(sgn*0.55,0,1.48), ry=sgn*PI/4.5), 'gold'))
    elif level == 4:  # Van Creeg Hypersplicer: стеклянный купол + 2 катушки-антенны
        P.append(_p(tf(cyl(0.6, 0.14, 26), t=(0,0,0.2)), 'hull'))
        P.append(_p(tf(dome(0.58, 28, 11), t=(0,0,0.26), s=(1,1,0.85)), 'glass'))
        P.append(_p(tf(sphere(0.16, 14, 8), t=(0,0,0.55)), 'accent'))
        P.append(_p(tf(torus(0.59, 0.05, 30, 10), t=(0,0,0.25)), 'detail'))
        for sgn in (-1, 1):
            P.append(_p(tf(cyl(0.07, 0.8, 10), t=(sgn*0.5,-0.1,0.9), ry=sgn*PI/4), 'hull'))
            P.append(_p(tf(helix_coil(0.12, 0.6, 6, 0.032), t=(sgn*0.52,-0.1,0.92), ry=sgn*PI/4), 'coil'))
            P.append(_p(tf(sphere(0.08, 10, 6), t=(sgn*0.78,-0.1,1.16)), 'blue'))
    else:  # Nanotwirler: лежащая восьмёрка колец + катушка сбоку
        for sgn in (-1, 1):
            for zz in (0.3, 0.5):
                P.append(_p(tf(torus(0.34, 0.13, 30, 12), t=(sgn*0.29, sgn*0.08, zz)), 'coil2'))
        P.append(_p(tf(sphere(0.11, 12, 7), t=(0, 0, 0.58)), 'hull'))
        P.append(_p(tf(helix_coil(0.08, 0.5, 6, 0.03), t=(0.55, -0.45, 0.35), ry=PI/2, rz=PI/4), 'coil'))
        P.append(_p(tf(cyl(0.03, 0.5, 6), t=(0.55, -0.45, 0.32), ry=PI/2, rz=PI/4), 'hull'))
    return merge(P)

# --- SHIELD ------------------------------------------------------------------
def shield(level, seed=0, with_platform=True):
    P = platform(1.6, with_platform)
    if level == 1:  # Ion Wrap: сцепленные кольца + лента
        P.append(_p(tf(torus(0.46, 0.1, 32, 12), t=(0.05,0,0.3), rx=PI/12), 'gold'))
        P.append(_p(tf(torus(0.44, 0.1, 32, 12), t=(0,0.05,0.62), rx=PI/2.3), 'coil'))
        P.append(_p(tf(torus(0.4, 0.09, 32, 12), t=(-0.05,-0.08,0.55), rx=PI/2.8, rz=0.9), 'teal'))
        P.append(_p(arc_pipe((-0.5,0.3,0.2),(0.5,-0.3,0.2),(0,0,0.55), 0.09), 'white'))
    elif level == 2:  # Deactotron: пухлый синий тор + оранжевая звезда
        P.append(_p(tf(torus(0.46, 0.2, 32, 14), t=(0,0,0.4)), 'blue'))
        P.append(_p(tf(torus(0.46, 0.07, 32, 10), t=(0,0,0.56)), 'teal'))
        for a in np.linspace(0, 2*PI, 5, endpoint=False):
            tip = (0.72*math.cos(a), 0.72*math.sin(a), 0.58)
            P.append(_p(tube(np.array([(0,0,0.68), (tip[0]*0.5, tip[1]*0.5, 0.78), tip]), 0.032, 8), 'accent'))
        P.append(_p(tf(sphere(0.14, 12, 8), t=(0,0,0.62)), 'gold'))
    elif level == 3:  # Wave Scatterer: ёж на трёх зелёных ногах
        P.append(_p(tf(sphere(0.4, 22, 12), t=(0,0,0.85)), 'white'))
        V, _ = sphere(1.0, 12, 7)
        seen = set()
        for v in V:
            key = tuple((v*4).astype(int))
            if key in seen: continue
            seen.add(key)
            n = v/np.linalg.norm(v)
            P.append(_p(tube(np.array([0.38*n + (0,0,0.85), 0.62*n + (0,0,0.85)]), 0.022, 6), 'teal'))
        for a in np.linspace(PI/6, 2*PI+PI/6, 3, endpoint=False):
            x,y = math.cos(a), math.sin(a)
            P.append(_p(arc_pipe((x*0.62,y*0.62,0.12),(x*0.22,y*0.22,0.72),(0,0,0.3), 0.055), 'green'))
        P.append(_p(tf(torus(0.2, 0.04, 18, 8), t=(0,0,0.14)), 'green'))
    elif level == 4:  # Hyperwave Nullifier ~ Concussion: купол-зонт + катушки-кольца
        for i, (r, z) in enumerate(((0.42, 0.22), (0.36, 0.34), (0.3, 0.46))):
            P.append(_p(tf(helix_coil(r, 0.1, 2, 0.045), t=(0,0,z)), 'coil2' if i%2 else 'coil'))
        for a in np.linspace(0, 2*PI, 6, endpoint=False):
            path = [(0.62*math.cos(a)*math.sin(t), 0.62*math.sin(a)*math.sin(t), 0.5+0.55*math.cos(t)) for t in np.linspace(0.08, PI/2.1, 10)]
            P.append(_p(tube(np.array(path), 0.035, 8), 'gold'))
        P.append(_p(tf(sphere(0.1, 12, 7), t=(0,0,1.08)), 'accent'))
        P.append(_p(tf(dome(0.56, 24, 9), t=(0,0,0.48), s=(1,1,0.9)), 'glass'))
    else:  # Nanoshield: ёж + двойное кольцо
        P.append(_p(tf(sphere(0.34, 20, 11), t=(0,0,0.8)), 'white'))
        V, _ = sphere(1.0, 12, 7)
        seen=set()
        for v in V:
            key = tuple((v*4).astype(int))
            if key in seen: continue
            seen.add(key)
            n = v/np.linalg.norm(v)
            P.append(_p(tube(np.array([0.32*n+(0,0,0.8), 0.5*n+(0,0,0.8)]), 0.018, 6), 'pink'))
        P.append(_p(tf(torus(0.52, 0.06, 32, 10), t=(0,0,0.42), rx=PI/2.6), 'teal'))
        P.append(_p(tf(torus(0.52, 0.06, 32, 10), t=(0,0,0.42), rx=PI/2.6, rz=2*PI/3), 'gold'))
        P.append(_p(tf(cyl(0.16, 0.3, 12, r2=0.22), t=(0,0,0.2)), 'graph'))
    return merge(P)

# --- SCANNER -----------------------------------------------------------------
def scanner(level, seed=0, with_platform=True):
    P = platform(1.6, with_platform)
    if level == 1:  # Tonklin Frequency Analyzer
        for (x,y,h) in ((0,0,0.85),(0.38,0.18,0.55),(-0.33,0.24,0.5),(0.14,-0.38,0.46),(-0.28,-0.28,0.42)):
            P.append(_p(tf(cyl(0.05, h, 8), t=(x,y,0.18+h/2)), 'hull'))
            P.append(_p(tf(helix_coil(0.11, h*0.72, 6, 0.032), t=(x,y,0.22+h/2)), 'coil'))
            P.append(_p(tf(sphere(0.06,10,6), t=(x,y,0.25+h)), 'gold'))
        P.append(_p(arc_pipe((0.38,0.18,0.5),(-0.33,0.24,0.45),(0,0,0.25), 0.02), 'gold'))
    elif level == 2:  # Subspace Phase Array
        P.append(_p(tf(cyl(0.18, 0.3, 14, r2=0.28), t=(0,0,0.35)), 'hull'))
        P.append(_p(tf(revolve([(0.04,0.18),(0.58,0.0),(0.62,0.04),(0.08,0.26)], 30), t=(0,0,0.55)), 'white'))
        for rz in (0.4, 1.45, 2.5):
            P.append(_p(tf(cyl(0.02, 1.0, 6), t=(0,0,1.0), rx=PI/3.4, rz=rz), 'gold'))
        P.append(_p(tf(sphere(0.07, 10, 6), t=(0,0,1.0)), 'accent'))
        for a in np.linspace(0, 2*PI, 6, endpoint=False):
            P.append(_p(tf(box(0.08,0.16,0.05), t=(0.45*math.cos(a), 0.45*math.sin(a), 0.2), rz=a), 'coil2'))
    elif level == 3:  # Aural Cloud Constructor
        P.append(_p(tf(cyl(0.52, 0.22, 26), t=(0,0,0.28)), 'teal'))
        P.append(_p(tf(torus(0.5, 0.045, 30, 8), t=(0,0,0.4)), 'gold'))
        for a in np.linspace(0, 2*PI, 8, endpoint=False):
            x,y = 0.35*math.cos(a), 0.35*math.sin(a)
            P.append(_p(tf(cyl(0.1, 0.45, 12), t=(x,y,0.58), rx=PI/7*math.sin(a+PI/2)*(-1), ry=PI/7*math.cos(a+PI/2)), 'blue'))
            P.append(_p(tf(torus(0.1, 0.02, 12, 6), t=(x*1.15,y*1.15,0.78), rx=-PI/7*math.sin(a+PI/2), ry=PI/7*math.cos(a+PI/2)), 'white'))
        P.append(_p(tf(sphere(0.16, 14, 8), t=(0,0,0.68)), 'coil'))
    elif level == 4:  # Hyperwave Tympanum
        for i, r in enumerate((0.52, 0.45, 0.37)):
            P.append(_p(tf(revolve([(0.08,0.09),(r,0.05),(r+0.03,0.0),(0.08,-0.05)], 26), t=(0,0,0.36+0.19*i)), 'coil2'))
        P.append(_p(tf(dome(0.18, 16, 6), t=(0,0,0.85)), 'white'))
        for a in np.linspace(PI/5, 2*PI, 3, endpoint=False):
            x,y = 0.58*math.cos(a), 0.58*math.sin(a)
            P.append(_p(tf(cyl(0.025, 0.65, 6), t=(x,y,0.5)), 'hull'))
            P.append(_p(tf(sphere(0.06, 10, 6), t=(x,y,0.86)), 'gold'))
            P.append(_p(tf(cyl(0.05, 0.04, 8), t=(x,y,0.78)), 'coil'))
    else:  # Nanowave Decoupling Net
        P.append(_p(tf(cyl(0.22, 0.26, 14, r2=0.13), t=(0,0,0.32)), 'hull'))
        P.append(_p(tf(revolve([(0.05,0.14),(0.68,0.0),(0.74,0.05),(0.09,0.22)], 32), t=(0,0,0.48), rx=PI/16), 'coil'))
        P.append(_p(tf(revolve([(0.02,0.08),(0.56,0.0)], 28), t=(0,0,0.54), rx=PI/16), 'blue'))
        for a in np.linspace(0, 2*PI, 7, endpoint=False):
            x, y = 0.3*math.cos(a), 0.3*math.sin(a)
            P.append(_p(tf(torus(0.085, 0.02, 12, 6), t=(x, y*math.cos(PI/16), 0.6 + y*math.sin(PI/16)), rx=PI/16), 'white'))
        P.append(_p(tf(torus(0.085, 0.02, 12, 6), t=(0, 0, 0.6), rx=PI/16), 'white'))
    return merge(P)

# --- WEAPONS -----------------------------------------------------------------
def weapon_beam(level, family, seed=0, with_platform=True):
    P = platform(1.6, with_platform)
    if family == 'lazer':  # Ueberlaser
        L = 0.85 + 0.14*level
        P.append(_p(tf(box(0.46, 0.5, 0.42), t=(0, -0.42, 0.44)), 'hull'))
        P.append(_p(tf(box(0.52, 0.16, 0.52), t=(0, -0.42, 0.5)), 'coil2'))
        P.append(_p(tf(box(0.07, 0.44, 0.6), t=(0.25, -0.38, 0.52), rz=-0.1), 'coil2'))
        P.append(_p(tf(cyl(0.12, L, 16), t=(0, -0.15 + L/2, 0.52), rx=PI/2), 'white'))
        for k in range(2+level):
            P.append(_p(tf(torus(0.145, 0.03, 18, 8), t=(0, 0.05 + k*(L-0.35)/(1+level), 0.52), rx=PI/2), 'graph'))
        P.append(_p(tf(cyl(0.065, 0.28, 10), t=(0, -0.15 + L + 0.12, 0.52), rx=PI/2), 'teal'))
        P.append(_p(tf(sphere(0.08, 10, 6), t=(0, -0.15 + L + 0.3, 0.52)), 'accent'))
    else:  # Plasmatron
        P.append(_p(tf(sphere(0.4, 22, 12), t=(-0.05, -0.3, 0.58)), 'white'))
        P.append(_p(tf(torus(0.41, 0.05, 26, 8), t=(-0.05, -0.3, 0.58), rx=PI/2.4), 'gold'))
        P.append(_p(tf(cyl(0.3, 0.2, 18), t=(-0.05, -0.3, 0.18)), 'graph'))
        blen = 0.6 + 0.11*level
        P.append(_p(tf(cyl(0.085, blen, 12), t=(0.05, -0.05 + blen/2, 0.6), rx=PI/2), 'hull'))
        P.append(_p(tf(helix_coil(0.13, blen*0.85, 5+level, 0.034), t=(0.05, -0.05 + blen/2, 0.6), rx=PI/2), 'coil'))
        P.append(_p(tf(cyl(0.05, 0.16, 8), t=(0.05, -0.05 + blen + 0.1, 0.6), rx=PI/2), 'teal'))
        P.append(_p(tf(sphere(0.07, 10, 6), t=(0.05, -0.05 + blen + 0.2, 0.6)), 'accent'))
    return merge(P)

def weapon_rapid(level, family, seed=0, with_platform=True):
    P = platform(1.6, with_platform)
    if family == 'lazer':  # Hypersphere Driver
        P.append(_p(tf(sphere(0.42, 24, 13), t=(0.1, -0.25, 0.6)), 'white'))
        P.append(_p(tf(cyl(0.3, 0.25, 16), t=(0.1, -0.25, 0.2)), 'graph'))
        n_pods = 5 + level
        for i, a in enumerate(np.linspace(0, 2*PI, n_pods, endpoint=False)):
            x, z = 0.34*math.cos(a), 0.34*math.sin(a)
            P.append(_p(tf(cyl(0.09, 0.3, 10), t=(0.1 + x, 0.18, 0.6 + z), rx=PI/2), 'accent'))
            P.append(_p(tf(sphere(0.09, 10, 6), t=(0.1 + x, 0.34, 0.6 + z)), 'coil2'))
        P.append(_p(tf(cyl(0.16, 0.4, 12), t=(0.1, 0.25, 0.6), rx=PI/2), 'hull'))
        P.append(_p(tf(cyl(0.1, 0.12, 10), t=(0.1, 0.5, 0.6), rx=PI/2), 'dark'))
    else:  # Nanomanipulator
        blen = 0.85 + 0.08*level
        P.append(_p(tf(cyl(0.09, blen, 12), t=(0, 0, 0.58), rx=PI/2), 'white'))
        P.append(_p(tf(helix_coil(0.26, blen*0.85, 4+level, 0.05), t=(0,0,0.58), rx=PI/2), 'pink'))
        P.append(_p(tf(cyl(0.13, 0.2, 12, r2=0.06), t=(0, blen/2 + 0.08, 0.58), rx=PI/2), 'hull'))
        P.append(_p(tf(sphere(0.07, 10, 6), t=(0, blen/2 + 0.2, 0.58)), 'accent'))
        for sgn in (-1, 1):
            P.append(_p(arc_pipe((sgn*0.4,-0.35,0.14),(sgn*0.4,0.35,0.14),(sgn*0.1,0,0.42), 0.045), 'graph'))
        P.append(_p(tf(box(0.24,0.3,0.18), t=(0, -blen/2-0.1, 0.5)), 'graph'))
    return merge(P)

# --- AUX ----------------------------------------------------------------------
def aux(kind, seed=0, with_platform=True):
    P = platform(1.7, with_platform)
    if kind == 'colony':  # Colonizer (HQ): купол, бутыль, канистры, панель, труба
        # бирюзовый купол на белом ободе (передний левый угол)
        P.append(_p(tf(cyl(0.36, 0.05, 22), t=(-0.35,0.28,0.2)), 'white'))
        P.append(_p(tf(dome(0.33, 22, 9), t=(-0.35,0.28,0.22)), 'teal'))
        # зелёная бутыль лежит в центре, горлом к зрителю
        P.append(_p(tf(cyl(0.17, 0.6, 16, r2=0.13), t=(0.05,0.05,0.52), rx=-PI/2.2, rz=0.35), 'bottle'))
        P.append(_p(tf(cyl(0.07, 0.24, 12), t=(-0.06,0.3,0.36), rx=-PI/2.2, rz=0.35), 'bottle'))
        # серебряный ребристый цилиндр-стопка за бутылью
        P.append(_p(tf(cyl(0.17, 0.55, 16), t=(0.28,-0.18,0.72), rx=-PI/2.5, rz=0.35), 'silver'))
        for k in range(4):
            P.append(_p(tf(torus(0.175, 0.02, 18, 6), t=(0.28-0.05*k,-0.18+0.11*k,0.72-0.03*k), rx=-PI/2.5, rz=0.35), 'hull'))
        # деревянная панель вертикально сзади
        P.append(_p(tf(box(0.6, 0.06, 0.62), t=(0.18,-0.45,0.48), rz=-0.3), 'wood'))
        P.append(_p(tf(box(0.45, 0.45, 0.3), t=(0.55,-0.02,0.3), rz=0.3), 'wood'))
        # золотая труба дугой в платформу
        P.append(_p(arc_pipe((0.66,0.12,0.2),(0.1,-0.42,0.24),(0,0,0.55), 0.065), 'gold'))
        # белая ребристая канистра справа-спереди
        P.append(_p(tf(cyl(0.13, 0.38, 14), t=(0.52,0.35,0.38), rx=0.15), 'white'))
        P.append(_p(tf(torus(0.135, 0.018, 16, 6), t=(0.52,0.35,0.44), rx=0.15), 'hull_b'))
        # зелёное стеклянное кольцо перед куполом
        P.append(_p(tf(torus(0.13, 0.045, 18, 8), t=(-0.08,0.52,0.24)), 'bottle'))
        # три бирюзовые сферы спереди
        for dx, dy in ((-0.3,0.62),(-0.14,0.68),(0.02,0.62)):
            P.append(_p(tf(sphere(0.07, 10, 7), t=(dx,dy,0.24)), 'teal'))
        # частокол
        for i in range(5):
            P.append(_p(tf(cyl(0.025, 0.28+0.05*(i%3), 6, r2=0.001), t=(0.2+0.07*i,0.5-0.02*i,0.32)), 'wood'))
        # флаг (задний левый угол)
        P.append(_p(tf(cyl(0.015, 0.9, 6), t=(-0.6,-0.42,0.6)), 'hull'))
        P.append(_p(tf(box(0.2, 0.02, 0.12), t=(-0.51,-0.42,0.98)), 'wood'))
    else:  # Invasion Module (HQ): жёлто-зелёный клиновидный дропшип носом к зрителю
        rzs = -0.5  # нос к нижне-правому углу (+X)
        def sh(vf, t=(0,0,0), **kw):
            return tf(tf(vf, **kw), t=t, rz=rzs)
        # корпус: слоёный клин
        P.append(_p(sh(box(1.15, 0.5, 0.16), t=(0,0,0.32)), 'ygreen'))
        P.append(_p(sh(cyl(0.25, 0.9, 4, r2=0.02), t=(0.55,0,0.32), ry=PI/2, rz=PI/4), 'ygreen'))  # нос-клин
        P.append(_p(sh(box(0.8, 0.36, 0.14), t=(-0.1,0,0.44)), 'dgreen'))
        P.append(_p(sh(box(0.5, 0.24, 0.12), t=(-0.35,0,0.55)), 'ygreen'))
        P.append(_p(sh(box(0.3, 0.5, 0.1), t=(-0.5,0,0.4)), 'dgreen'))
        # крылья-плиты
        for sgn in (-1,1):
            P.append(_p(sh(box(0.45, 0.4, 0.05), t=(-0.15, sgn*0.38, 0.42), rz=sgn*0.5), 'dgreen'))
            P.append(_p(sh(box(0.3, 0.22, 0.06), t=(0.2, sgn*0.3, 0.38), rz=sgn*0.3), 'ygreen'))
        # красные полосы на корпусе
        P.append(_p(sh(box(0.12, 0.52, 0.05), t=(0.18,0,0.42)), 'coil'))
        P.append(_p(sh(box(0.1, 0.38, 0.04), t=(-0.25,0,0.52)), 'coil'))
        # два малых красно-жёлтых пода перед кораблём
        for i, (dx, dy) in enumerate(((0.15,-0.55),(-0.2,-0.6))):
            P.append(_p(tf(box(0.28, 0.16, 0.12), t=(dx,dy,0.24), rz=0.2), 'ygreen'))
            P.append(_p(tf(box(0.1, 0.17, 0.08), t=(dx,dy,0.32), rz=0.2), 'coil'))
    return merge(P)

# --- SPECIAL -------------------------------------------------------------------
def inertia_negator(seed=0, with_platform=True):
    P = platform(1.6, with_platform)
    P.append(_p(tf(torus(0.5, 0.08, 34, 12), t=(0,0,0.68), rx=PI/2), 'blue'))
    P.append(_p(tf(torus(0.5, 0.08, 34, 12), t=(0,0,0.68), rx=PI/2, rz=PI/2), 'teal'))
    P.append(_p(tf(torus(0.36, 0.05, 28, 10), t=(0,0,0.68), rx=PI/4, rz=PI/4), 'gold'))
    P.append(_p(tf(sphere(0.24, 18, 10), t=(0,0,0.68)), 'white'))
    for sgn in (-1,1):
        P.append(_p(tf(cyl(0.06, 0.45, 8), t=(sgn*0.68,0,0.38), ry=sgn*PI/6), 'hull'))
        P.append(_p(tf(sphere(0.1,10,6), t=(sgn*0.78,0,0.18)), 'graph'))
    return merge(P)
