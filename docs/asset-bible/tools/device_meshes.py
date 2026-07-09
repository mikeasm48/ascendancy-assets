# device_meshes.py — процедурные меши устройств (pure numpy, без bpy).
# Используется и для прототипирования (рендер в песочнице), и в Blender
# (bpy строит меши через from_pydata из этих же данных).
import numpy as np
import math

# ---------------------------------------------------------------- примитивы

def _quad_grid(nu, nv, close_u=False, close_v=False):
    """faces для сетки (nu x nv) вершин."""
    F = []
    U = nu if close_u else nu - 1
    V = nv if close_v else nv - 1
    for i in range(U):
        for j in range(V):
            a = i * nv + j
            b = ((i + 1) % nu) * nv + j
            c = ((i + 1) % nu) * nv + (j + 1) % nv
            d = i * nv + (j + 1) % nv
            F += [(a, b, c), (a, c, d)]
    return np.array(F, dtype=np.int64)

def revolve(profile, seg=24, close=True):
    """Тело вращения вокруг Z. profile: [(r,z),...] сверху вниз."""
    prof = np.asarray(profile, float)
    ang = np.linspace(0, 2 * np.pi, seg, endpoint=False)
    V = np.zeros((seg, len(prof), 3))
    V[:, :, 0] = np.cos(ang)[:, None] * prof[None, :, 0]
    V[:, :, 1] = np.sin(ang)[:, None] * prof[None, :, 0]
    V[:, :, 2] = prof[None, :, 1]
    F = _quad_grid(seg, len(prof), close_u=True)
    V = V.reshape(-1, 3)
    # крышки, если края не в нуле радиуса
    caps = []
    nv = len(prof)
    for idx, zrow in ((0, prof[0]), (nv - 1, prof[-1])):
        if zrow[0] > 1e-6 and close:
            center = len(V)
            V = np.vstack([V, [0, 0, zrow[1]]])
            ring = [i * nv + idx for i in range(seg)]
            fl = [(ring[i], ring[(i + 1) % seg], center) for i in range(seg)]
            if idx == 0:
                fl = [(b, a, c) for a, b, c in fl]
            caps.append(np.array(fl))
    if caps:
        F = np.vstack([F] + caps)
    return V, F

def sphere(r=1.0, seg=24, rings=13):
    t = np.linspace(np.pi / 2, -np.pi / 2, rings)
    prof = [(max(r * math.cos(a), 0.0001), r * math.sin(a)) for a in t]
    return revolve(prof, seg)

def cyl(r=0.5, h=1.0, seg=16, r2=None):
    r2 = r if r2 is None else r2
    return revolve([(0.0001, h / 2), (r2, h / 2), (r, -h / 2), (0.0001, -h / 2)], seg)

def box(sx, sy, sz):
    x, y, z = sx / 2, sy / 2, sz / 2
    V = np.array([[-x,-y,-z],[x,-y,-z],[x,y,-z],[-x,y,-z],
                  [-x,-y,z],[x,-y,z],[x,y,z],[-x,y,z]], float)
    F = np.array([(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
                  (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)])
    return V, F

def torus(R=1.0, r=0.25, seg=32, tseg=14):
    a = np.linspace(0, 2*np.pi, seg, endpoint=False)
    b = np.linspace(0, 2*np.pi, tseg, endpoint=False)
    A, B = np.meshgrid(a, b, indexing='ij')
    V = np.stack([(R + r*np.cos(B))*np.cos(A),
                  (R + r*np.cos(B))*np.sin(A),
                  r*np.sin(B)], -1).reshape(-1, 3)
    return V, _quad_grid(seg, tseg, close_u=True, close_v=True)

def tube(path, r=0.06, tseg=10, cap=True):
    """Труба вдоль ломаной (параллельный перенос фрейма)."""
    P = np.asarray(path, float)
    T = np.gradient(P, axis=0)
    T /= np.linalg.norm(T, axis=1, keepdims=True) + 1e-12
    # начальная нормаль
    n = np.array([0, 0, 1.0])
    if abs(np.dot(n, T[0])) > 0.9:
        n = np.array([1.0, 0, 0])
    frames = []
    for t in T:
        n = n - np.dot(n, t) * t
        n /= np.linalg.norm(n) + 1e-12
        bn = np.cross(t, n)
        frames.append((n, bn))
    ang = np.linspace(0, 2*np.pi, tseg, endpoint=False)
    rings = []
    for p, (n, bn) in zip(P, frames):
        ring = p[None] + r*(np.cos(ang)[:, None]*n[None] + np.sin(ang)[:, None]*bn[None])
        rings.append(ring)
    V = np.vstack(rings)
    F = _quad_grid(len(P), tseg, close_u=False, close_v=True)
    # переиндексация: у меня rings идут (point, tseg) → grid ожидает (u=point,v=tseg)
    if cap:
        for end, pt in ((0, P[0]), (len(P)-1, P[-1])):
            c = len(V); V = np.vstack([V, pt])
            ring = [end*tseg + k for k in range(tseg)]
            fl = [(ring[k], ring[(k+1) % tseg], c) for k in range(tseg)]
            if end == 0:
                fl = [(b, a, c2) for a, b, c2 in fl]
            F = np.vstack([F, fl])
    return V, F

def helix_coil(R=0.3, h=0.6, turns=5, r_tube=0.07, seg_per_turn=20, tseg=8):
    n = int(turns * seg_per_turn)
    t = np.linspace(0, turns * 2*np.pi, n)
    z = np.linspace(-h/2, h/2, n)
    path = np.stack([R*np.cos(t), R*np.sin(t), z], -1)
    return tube(path, r_tube, tseg)

def arc_pipe(p0, p1, lift, r=0.08, n=24, tseg=10):
    """Дуга-труба между двумя точками с подъёмом середины."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    mid = (p0 + p1) / 2 + np.asarray(lift, float)
    ts = np.linspace(0, 1, n)
    path = ((1-ts)[:, None]**2)*p0 + 2*(ts*(1-ts))[:, None]*mid + (ts[:, None]**2)*p1
    return tube(path, r, tseg)

def dome(r=1.0, seg=24, rings=8, cut=0.0):
    t = np.linspace(np.pi/2, cut, rings)
    prof = [(max(r*math.cos(a), 1e-4), r*math.sin(a)) for a in t]
    prof.append((r*math.cos(cut), r*math.sin(cut)))
    return revolve(prof, seg)

def ngon_prism(r=0.5, h=0.4, n=8):
    return cyl(r, h, seg=n)

# ------------------------------------------------------------- трансформации

def tf(VF, t=(0, 0, 0), rx=0, ry=0, rz=0, s=1.0):
    V, F = VF
    V = np.asarray(V, float).copy()
    if np.isscalar(s):
        V *= s
    else:
        V *= np.asarray(s, float)[None]
    for ax, a in (('x', rx), ('y', ry), ('z', rz)):
        if a:
            c, sn = math.cos(a), math.sin(a)
            if ax == 'x': M = np.array([[1,0,0],[0,c,-sn],[0,sn,c]])
            if ax == 'y': M = np.array([[c,0,sn],[0,1,0],[-sn,0,c]])
            if ax == 'z': M = np.array([[c,-sn,0],[sn,c,0],[0,0,1]])
            V = V @ M.T
    V += np.asarray(t, float)[None]
    return V, F

def merge(parts):
    """parts: [(V,F,part_id_str), ...] -> (V, F, face_part_ids)"""
    Vs, Fs, tags = [], [], []
    off = 0
    for V, F, tag in parts:
        Vs.append(V); Fs.append(np.asarray(F) + off)
        tags += [tag] * len(F)
        off += len(V)
    return np.vstack(Vs), np.vstack(Fs), tags
