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

_TONKLIN_MOTOR_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "tonklin_motor_mesh.npz")


def engine_tonklin_motor(seed=0):
    """Заменяет прежнюю процедурную версию — геометрия из
    низкополигонального референса Engine_core_TonklinMotor_2_model.glb
    (6730 верш./14261 треуг., ~247KB; концепт —
    Engine_core_TonklinMotor_2.jpg: обветренный стальной блок-мотор с
    четырьмя стопками тёмно-красных плоских катушек и латунной трубой на
    квадратной плите). Цвет с парной текстурированной модели (позиции
    1:1, топология чуть другая — голосование по 5 ближайшим граням,
    linear->sRGB) в теги: tmsteel (сталь/плита/труба — патина трубы в
    запечённой текстуре десатурирована и k-means не отделяет её от
    стали), tmred (катушки), dark. Родная плита чистая — оставлена.
    Модель отнормирована до макс. габарита 1.0, развёрнута на 90° для
    витринного ракурса. Собственная плита уже в меше — общая плита
    каталога отключена (device_catalog_core.RECIPES, plate=None)."""
    return _load_imported_mesh(_TONKLIN_MOTOR_MESH_PATH)


_ION_BANGER_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "ion_banger_mesh.npz")


def engine_ion_banger(seed=0):
    """Заменяет прежнюю процедурную версию — геометрия из
    низкополигонального референса Engine_core_IonBanger_2_model.glb
    (7148 верш./14728 треуг., ~257KB; концепт —
    Engine_core_IonBanger_2.jpg: серебристый корпус-сфера с голубым
    голо-окном, ряды красных кабельных петель, жёлтые модули-клеммы и
    голубые светящиеся трубы). Цвет с парной текстурированной модели
    (позиции 1:1, топология чуть другая — голосование по 5 ближайшим
    граням, linear->sRGB) в теги: ibsilver (корпус, AO-оттенки слиты),
    ibred (кабели), ibyellow (модули), эмиссивный ibglow (трубы/линза).
    Родная плита чистая — оставлена. Модель отнормирована до макс.
    габарита 1.0, развёрнута на 90° для витринного ракурса. Собственная
    плита уже в меше — общая плита каталога отключена
    (device_catalog_core.RECIPES, plate=None)."""
    return _load_imported_mesh(_ION_BANGER_MESH_PATH)


# ====================================================== STAR LANE DRIVES

_STAR_LANE_DRIVE_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "star_lane_drive_mesh.npz")


def star_lane_drive(seed=0):
    """Заменяет прежнюю процедурную версию («крендель» из торов) —
    геометрия из низкополигонального референса StarLaneDrive_core_2.glb
    (8396 верш./15812 треуг., ~284KB, без цвета). Цвет перенесён с
    StarLaneDrive_core_2_texture.glb — та же геометрия с UV+текстурой
    (масштаб ~2.008, грани совпадают 1:1: медианное расхождение центров
    ~3e-7), поэтому каждая грань раскрашена напрямую по своему UV-сэмплу
    (linear->sRGB). Теги — k-means-группы реальных цветов модели:
    sldwhite/sldgray/sldpeach/sldblue/sldnavy + dark. Родная плита
    референса вырезана по связным компонентам и заменена чистым
    двухступенчатым боксом (белый верх, серая ступень снизу) — как у
    InvasionModule, во избежание z-fighting. Собственная плита уже в
    меше — общая плита каталога отключена (device_catalog_core.RECIPES,
    plate=None)."""
    return _load_imported_mesh(_STAR_LANE_DRIVE_MESH_PATH)


_STAR_LANE_HYPERDRIVE_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "star_lane_hyperdrive_mesh.npz")


def star_lane_hyperdrive(seed=0):
    """Заменяет прежнюю процедурную версию (спираль гофрошлангов) —
    геометрия из низкополигонального референса
    StarLaneDrive_core_HyperDrive_2.glb (7153 верш./14674 треуг., ~257KB,
    без цвета). Цвет с StarLaneDrive_core_HyperDrive_2_texture.glb (та же
    модель, топология близкая, но не 1:1 — 15193 граней; медианное
    расхождение центров ~0.0014, перенос голосованием по 5 ближайшим).
    Теги — k-means-группы: hdsilver (гофрошланги/корпус), hdred
    (малиновые модули), hdrose (потёртые панели), dark (кабели). Меш был
    единой связной компонентой, поэтому родная плита отрезана по
    плоскости (все вершины грани ниже верха плиты), вместо неё чистый
    двухступенчатый бокс, верх заподлицо с линией среза. Модель
    отнормирована до макс. габарита 1.0 (в исходнике была ~1.9).
    Собственная плита уже в меше — общая плита каталога отключена
    (device_catalog_core.RECIPES, plate=None)."""
    return _load_imported_mesh(_STAR_LANE_HYPERDRIVE_MESH_PATH)


# ============================================================ GENERATORS
#
# Все пять генераторов заменены импортированными низкополигональными
# референсами (пары <имя>_2_model.glb + _2_texture.glb, позиции граней
# 1:1): цвет перенесён голосованием по 5 ближайшим граням текстурного
# двойника (сэмпл текстуры по UV-центру грани, linear->sRGB), затем
# k-means-кластеры сгруппированы в узкие наборы реальных материалов
# модели (AO-оттенки одного материала слиты, урок InvasionModule).
# Одинокие эмиссивные грани сняты фильтром по соседям (антиспекл).
# Родные плиты чистые — оставлены; общая плита каталога отключена
# (plate=None). Модели отнормированы до макс. габарита 1.0.

_PROTON_SHAVER_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "proton_shaver_mesh.npz")


def generator_proton_shaver(seed=0):
    """Импорт Generator_core_ProtonShaver_2_model.glb (14776 треуг.):
    серебристая плита, синие башни-цилиндры с медно-красными обмотками
    (pscoil), латунная обвязка (psbrass). Теги: pssilver/psblue/
    psbrass/pscoil."""
    return _load_imported_mesh(_PROTON_SHAVER_MESH_PATH)


_SUBATOMIC_SCOOP_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "subatomic_scoop_mesh.npz")


def generator_subatomic_scoop(seed=0):
    """Импорт Generator_core_SubatomicScoop_2_model.glb (14822 треуг.):
    серебристая чаша-воронка на синих опорах, светящиеся цилиндры
    (эмиссивные ssglow/ssteal — в запечённой текстуре свечение выцвело
    до салатово-кремового, эмиссия возвращена через MATS). Теги:
    sssilver/ssblue/ssorange/ssglow/ssteal."""
    return _load_imported_mesh(_SUBATOMIC_SCOOP_MESH_PATH)


_QUARK_EXPRESS_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "quark_express_mesh.npz")


def generator_quark_express(seed=0):
    """Импорт Generator_core_QuarkExpress_2_model.glb (15000 треуг.):
    стально-синий круглый корпус с золотым кольцом, красные светящиеся
    цилиндры (эмиссивный qeglow — в текстуре выцвели до розового, цвет
    возвращён через MATS), зелёные катушки (qegreen). Теги: qeblue/
    qegold/qegreen/qeglow + dark."""
    return _load_imported_mesh(_QUARK_EXPRESS_MESH_PATH)


_VAN_CREEG_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "van_creeg_mesh.npz")


def generator_van_creeg(seed=0):
    """Импорт Generator_core_VanCreegHypersplicer_2_model.glb (13576
    треуг.): стальной корпус-купол (стекло купола в запечённой текстуре
    читается как сталь), золотой узел, медные торцы трубок (тег copper),
    циановые проблески ядра (эмиссивный vcglow). Теги: vcsteel/vcgold/
    vcglow + copper."""
    return _load_imported_mesh(_VAN_CREEG_MESH_PATH)


_NANOTWIRLER_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "nanotwirler_mesh.npz")


def generator_nanotwirler(seed=0):
    """Импорт Generator_core_Nanotwirler_2_model.glb (14486 треуг.):
    серебристая плита с тёмными рёбрами-радиаторами (ntdark), две
    золотые катушки-тороида, красные светящиеся колпаки (эмиссивный
    ntred), сине-фиолетовая трубка (эмиссивный ntblue). Теги: ntsilver/
    ntdark/ntgold/ntred/ntblue."""
    return _load_imported_mesh(_NANOTWIRLER_MESH_PATH)


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

_UEBERLASER_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "ueberlaser_mesh.npz")


def weapon_ueberlaser(seed=0):
    """Заменяет прежнюю процедурную версию — геометрия из
    низкополигонального референса Weapon_core_Ueberlaser_2_model.glb
    (7241 верш./14686 треуг., ~258KB; концепт —
    Weapon_core_Ueberlaser_2.jpg: серебристый гатлинг-лазер в жёлтой
    А-раме на круглом постаменте, зелёно-жёлтые кольца кассеты стволов,
    голубые линзы-дула). Цвет с парной текстурированной модели (позиции
    1:1, топология чуть другая — голосование по 5 ближайшим граням,
    linear->sRGB) в 4 тега: ubsilver (корпус, AO-оттенки слиты), ubyellow
    (рама/пояс), ubgreen (кольца стволов), эмиссивный ubglow (циановые
    линзы). Родная плита чистая (14 пар близких параллельных граней) —
    оставлена. Модель отнормирована до макс. габарита 1.0, дуло в +Y.
    Собственная плита уже в меше — общая плита каталога отключена
    (device_catalog_core.RECIPES, plate=None)."""
    return _load_imported_mesh(_UEBERLASER_MESH_PATH)


_PLASMATRON_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "plasmatron_mesh.npz")


def weapon_plasmatron(seed=0):
    """Заменяет прежнюю процедурную версию — геометрия из
    низкополигонального референса Weapon_core_Plasmatron_2_model.glb
    (7410 верш./14956 треуг., ~263KB; концепт —
    Weapon_core_Plasmatron_2.jpg: белая турель с бронзовыми барабанами и
    раскалённым красным гофростволом на круглом бело-бронзовом
    постаменте). Цвет с парной текстурированной модели (позиции 1:1,
    топология чуть другая — голосование по 5 ближайшим граням,
    linear->sRGB) в 3 тега: plwhite (корпус/постамент), plbronze (барабаны,
    AO-оттенки слиты в один), plglow (эмиссивная красная спираль ствола).
    Родная плита относительно чистая (16 пар близких параллельных граней)
    — оставлена. Модель отнормирована до макс. габарита 1.0, ствол в +Y.
    Собственная плита уже в меше — общая плита каталога отключена
    (device_catalog_core.RECIPES, plate=None)."""
    return _load_imported_mesh(_PLASMATRON_MESH_PATH)


_HYPERSPHERE_DRIVER_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "hypersphere_driver_mesh.npz")


def weapon_hypersphere_driver(seed=0):
    """Заменяет прежнюю процедурную версию — геометрия из
    низкополигонального референса Weapon_core_HypersphereDriver_2_model.glb
    (7491 верш./15218 треуг., ~267KB, без цвета; концепт —
    Weapon_core_HypersphereDriver_2.jpg: тёмная турель-пушка на круглом
    постаменте, сзади гроздь латунных сфер-накопителей, ствол-объектив с
    синим свечением). Цвет с парной текстурированной модели (позиции 1:1,
    топология чуть другая — голосование по 5 ближайшим граням,
    linear->sRGB). Серые AO-оттенки корпуса слиты в общий тег nmgun (тот
    же тёмный ганметал, что у Nanomanipulator), сферы — hsbrass, синее
    свечение линзы — эмиссивный hsglow. Родная плита-постамент чистая —
    оставлена. Модель отнормирована до макс. габарита 1.0, дуло в +Y по
    конвенции оружия. Собственная плита уже в меше — общая плита каталога
    отключена (device_catalog_core.RECIPES, plate=None)."""
    return _load_imported_mesh(_HYPERSPHERE_DRIVER_MESH_PATH)


_NANOMANIPULATOR_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "nanomanipulator_mesh.npz")


def weapon_nanomanipulator(seed=0):
    """Заменяет прежнюю процедурную версию (рупор из дисков) — геометрия
    из низкополигонального референса Weapon_core_Nanomanipulator_2_model.glb
    (7387 верш./14926 треуг., ~262KB, без цвета; концепт —
    Weapon_core_Nanomanipulator_2_concept.png: тёмная турель-бур с
    розовыми светящимися кольцами). Цвет с парной текстурированной модели
    (та же геометрия 1:1 по положению, топология чуть другая —
    голосование по 5 ближайшим граням, linear->sRGB). Серые AO-оттенки
    корпуса слиты в один тег nmgun (урок InvasionModule), розовое
    свечение — nmglow (эмиссия). Родная плита чистая (8 пар близких
    параллельных граней) — оставлена. Модель отнормирована до макс.
    габарита 1.0, дуло развёрнуто в +Y (конвенция оружия). Собственная
    плита уже в меше — общая плита каталога отключена
    (device_catalog_core.RECIPES, plate=None)."""
    return _load_imported_mesh(_NANOMANIPULATOR_MESH_PATH)


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


def _load_imported_mesh(npz_path):
    """Общий загрузчик для устройств, чья геометрия — готовый меш из
    внешнего референса (а не процедурная генерация): npz хранит V/F и
    tag_idx/tag_names (тег материала на грань, см. build_device_sets.MATS).
    Модель опускается так, чтобы её нижняя точка лежала на уровне плиты."""
    data = np.load(npz_path)
    V, F = data["V"], data["F"]
    tag_idx, tag_names = data["tag_idx"], data["tag_names"]
    tags = [str(tag_names[i]) for i in tag_idx]
    V = V.astype(float).copy()
    V[:, 2] += PLATE_TOP - V[:, 2].min()
    return V, F.astype(int), tags


def aux_invasion_module(seed=0):
    """Десантный штурмовой модуль — геометрия взята из точного
    низкополигонального референса Aux_core_InvasionModule_3.glb (5723
    верш./9840 треуг., ~90KB, без цвета в исходнике). Цвет перенесён с
    Aux_core_InvasionModule_3_texture.glb — той же геометрии с
    UV+текстурой (грани совпадают 1:1 в исходном порядке, медианное
    расхождение центров граней ~5e-7 — точное соответствие, без
    кросс-топологического шума). Ранее цвет ошибочно снимался с
    высокополигонального Aux_core_InvasionModule_2.glb (другая топология,
    129MB) методом ближайшей точки — давало шумный "камуфляжный" результат;
    текстура на точном референсе сняла необходимость в голосовании по
    соседям, каждая грань раскрашена напрямую по своему UV-сэмплу
    (linear->sRGB), снэпнутому к ближайшему из реальных цветов модели
    (tan/teal/redbright/copper/invgray — найдены через k-means, остальные
    теги палитры исключены). Родная плита референса (1176 граней с
    почти-совпадающими параллельными плоскостями — давала z-fighting
    «квадратами» при вращении, плюс зубцы с изнанки) вырезана по связным
    компонентам и заменена чистым боксом с двумя красными полосами по
    кромкам в цветах оригинала. Результат сохранён заранее
    (tools/invasion_module_mesh.npz) и просто грузится здесь. Собственная
    плита уже есть в меше — общая плита каталога для этого узла отключена
    (device_catalog_core.RECIPES, plate=None)."""
    return _load_imported_mesh(_INVASION_MESH_PATH)


_COLONIZER_NEW_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "colonizer_new_mesh.npz")


def aux_colonizer_new(seed=0):
    """Альтернативная версия Colonizer (не заменяет существующий
    aux_colonizer) — геометрия из низкополигонального референса
    Aux_core_Colonizer_low_poly.glb (5763 верш./9871 треуг., ~188KB, без
    цвета). Цвет перенесён с Aux_core_Colonizer_low_poly_texture.glb —
    той же геометрии с UV+текстурой (2x масштаб, лица совпадают почти
    точно: медианное расстояние ближайшей точки ~0.003), поэтому перенос
    близок к точному, без кросс-топологического шума, как у
    InvasionModule. K-means по образцам текстуры показал реальную
    палитру: несколько серых AO-оттенков одного материала (усреднены в
    один тег colgray), бледно-зелёный двигатель (colgreen), бежевые
    стойки (coltan), золотистые шланги (colgold), тёмные экраны (dark).
    Собственная плита уже есть в меше — общая плита каталога для этого
    узла отключена (device_catalog_core.RECIPES, plate=None)."""
    return _load_imported_mesh(_COLONIZER_NEW_MESH_PATH)



_LANE_MAGNETRON_MESH_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "lane_magnetron_mesh.npz")


def aux_lane_magnetron(seed=0):
    """Заменяет прежнюю процедурную версию — геометрия из
    низкополигонального референса Aux_core_LaneMagnetron_3.glb (4394
    верш./10792 треуг., ~179KB, без цвета; более чистая ретопология,
    чем у версии 2). Цвет перенесён с Aux_core_LaneMagnetron_3_texture.glb
    (та же модель, 4096-текстура; топология близкая, но не 1:1 —
    голосование по 5 ближайшим граням, linear->sRGB) в узкий набор
    реальных цветов модели (lmgray/lmtan/lmbrass/lmteal/lmglow/lmgreen/
    dark, найденных k-means). Родная плита-решётка чистая (без
    почти-совпадающих граней) и оставлена как есть. Модель отнормирована
    до макс. габарита 1.0 и развёрнута на 90° для витринного ракурса.
    Собственная плита уже есть в меше — общая плита каталога отключена
    (device_catalog_core.RECIPES, plate=None)."""
    return _load_imported_mesh(_LANE_MAGNETRON_MESH_PATH)
