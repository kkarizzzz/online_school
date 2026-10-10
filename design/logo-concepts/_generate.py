import math, os, sys, html

OUT = sys.argv[1]
CUR = sys.argv[2]
B = '#1219F3'
LB = '#8F93FA'
Y = '#FFC531'
INK = f'var(--ink,{B})'
RC = 'fill="none" stroke-linecap="round" stroke-linejoin="round"'


def n(v):
    l = math.hypot(*v)
    return (v[0] / l, v[1] / l)


def f(x):
    return f'{x:.2f}'.rstrip('0').rstrip('.')


def head(tip, d, L=6.2, W=4.8):
    d = n(d)
    p = (-d[1], d[0])
    b = (tip[0] - d[0] * L, tip[1] - d[1] * L)
    w1 = (b[0] + p[0] * W, b[1] + p[1] * W)
    w2 = (b[0] - p[0] * W, b[1] - p[1] * W)
    return f'M{f(w1[0])} {f(w1[1])}L{f(tip[0])} {f(tip[1])}L{f(w2[0])} {f(w2[1])}'


BOTTOM = 'M13 34C13 37.5 15 39 17.2 39C20 39 21 36.6 22 33L26 15'
INTEGRAL = BOTTOM + 'C27 11.4 28 9 30.8 9C33 9 35 10.5 35 14'


def ia(E=(35.5, 8.5), t=(1, -0.62), L=6.2, W=4.8):
    """integral whose top hook turns into an arrow"""
    sd = n((4, -18))
    t = n(t)
    c1 = (26 + sd[0] * 3.2, 15 + sd[1] * 3.2)
    c2 = (E[0] - t[0] * 4.5, E[1] - t[1] * 4.5)
    p = BOTTOM + f'C{f(c1[0])} {f(c1[1])} {f(c2[0])} {f(c2[1])} {f(E[0])} {f(E[1])}'
    return p, head(E, t, L, W)


IA, IAH = ia()


def g(paths, color, sw, extra=''):
    return f'<g {RC} stroke="{color}" stroke-width="{sw}" {extra}>' + ''.join(f'<path d="{p}"/>' for p in paths) + '</g>'


def scaled(inner, k, cx=24, cy=24):
    return f'<g transform="translate({cx} {cy}) scale({k}) translate(-24 -24)">{inner}</g>'


def svg(body, vb='0 0 48 48'):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}">{body}</svg>'


L = []  # (file, group, title, note, svg)


def add(key, group, title, note, body, vb='0 0 48 48'):
    L.append((key, group, title, note, svg(body, vb)))


OLD, NEW = 'old', 'new'

# ---------------- based on the old logo ----------------
add('o01-redraw', OLD, 'Бережная перерисовка',
    'Всё как в старом: круг, внутреннее кольцо, ∫-стрелка с перекладиной. Кольцо и линии стали толще, щели шире.',
    f'<circle cx="24" cy="24" r="24" fill="{B}"/><circle cx="24" cy="24" r="20" fill="none" stroke="#fff" stroke-width="2.4"/>'
    + scaled(g([IA, IAH, 'M18.5 24H29.5'], '#fff', 4.6) , .72, 24, 24.6))

oid = 'o02'
add('o02-breakthrough', OLD, 'Прорыв',
    'Стрелка интеграла пробивает границу круга и выходит наружу: «вырваться за пределы».',
    f'<defs><clipPath id="{oid}c"><circle cx="21" cy="27" r="19"/></clipPath></defs>'
    + scaled(g(list(ia(E=(42, 6), t=(1, -.8))), INK, 4.4), .86, 21, 27.5)
    + f'<circle cx="21" cy="27" r="19" fill="{B}"/>'
    + f'<g clip-path="url(#{oid}c)">' + scaled(g(list(ia(E=(42, 6), t=(1, -.8))), '#fff', 4.4), .86, 21, 27.5) + '</g>')

add('o03-limits', OLD, '∫ от 0 до 100',
    'Определённый интеграл с пределами 0 и 100 — математическая запись названия. В мелком размере остаётся просто ∫.',
    scaled(g([INTEGRAL], INK, 4.4), 1, 20, 24)
    + g(['M35.6 6.2l1.6-1.2v8'], INK, 1.9)
    + f'<g fill="none" stroke="{INK}" stroke-width="1.9"><ellipse cx="41.3" cy="9" rx="1.9" ry="3.4"/><ellipse cx="46.3" cy="9" rx="1.9" ry="3.4"/><ellipse cx="33.6" cy="40.5" rx="1.9" ry="3.4"/></g>',
    '0 0 50 48')

add('o04-progress', OLD, '∫ в кольце прогресса',
    'Старый круг превратился в индикатор прогресса: дуга почти замкнута, внутри чистый знак интеграла.',
    f'<circle cx="24" cy="24" r="21" fill="none" stroke="{INK}" stroke-opacity=".2" stroke-width="4"/>'
    + g(['M24 45A21 21 0 1 1 38.85 9.15'], INK, 4)
    + scaled(g([INTEGRAL], INK, 5.4), .66))

add('o05-squircle-dot', OLD, 'Сквиркл с точкой',
    'Скруглённый квадрат, белый ∫ и жёлтая точка из старого лого — она становится акцентом бренда.',
    f'<rect width="48" height="48" rx="14" fill="{B}"/>' + scaled(g([INTEGRAL], '#fff', 5), .8, 23, 24.5)
    + f'<circle cx="37.6" cy="10.2" r="3.3" fill="{Y}"/>')

add('o06-gradient', OLD, 'Градиент',
    'Классический круг с ∫-стрелкой, но с диагональным градиентом синий → фиолетовый. Современнее и объёмнее.',
    '<defs><linearGradient id="o06g" x1="0" y1="48" x2="48" y2="0" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#1219F3"/><stop offset="1" stop-color="#8A3CFF"/></linearGradient></defs>'
    '<circle cx="24" cy="24" r="24" fill="url(#o06g)"/>' + scaled(g([IA, IAH], '#fff', 5.2), .82, 24, 25))

add('o07-open-ring', OLD, 'Разомкнутое кольцо',
    'Контурный круг с разрывом, через который выходит стрелка интеграла. Лёгкий линейный вариант.',
    g(['M42.13 15.55A20 20 0 1 1 30.84 5.21'], INK, 3.6)
    + scaled(g(list(ia(E=(40, 7.5), t=(1, -.85))), INK, 4.8), .8, 23.5, 25.5))

add('o08-zero-disc', OLD, '0 ∫ ●',
    'Пустой круг «ноль» и залитый круг «сотка», соединённые изгибом интеграла.',
    f'<circle cx="12" cy="36" r="7" fill="none" stroke="{INK}" stroke-width="4"/><circle cx="35" cy="13" r="10" fill="{INK}"/>'
    + g(['M17 31C22 26 20 22 24 19.5S28 18 29 18'], INK, 4))

seal_text = 'ИЗ НУЛЯ В СОТКУ • ИЗ НУЛЯ В СОТКУ • '
add('o09-seal', OLD, 'Печать',
    'Круглая печать с названием по окружности. Для крупных форматов: сертификаты, мерч, обложки. В мелком — ставить 01 или 06.',
    f'<defs><path id="o09p" d="M24 24m-18.6 0a18.6 18.6 0 1 1 37.2 0a18.6 18.6 0 1 1 -37.2 0"/></defs>'
    f'<circle cx="24" cy="24" r="24" fill="{B}"/><circle cx="24" cy="24" r="14.2" fill="none" stroke="#fff" stroke-width="1.2"/>'
    f'<text font-family="Mulish,Arial,sans-serif" font-weight="800" font-size="4.3" fill="#fff" textLength="114" lengthAdjust="spacing"><textPath href="#o09p">{seal_text}</textPath></text>'
    + scaled(g([IA, IAH], '#fff', 6.8), .5))

add('o10-gradient-stroke', OLD, 'Нарастающий цвет',
    'Только глиф: линия интеграла набирает насыщенность снизу вверх — от бледного «нуля» к яркой «сотке».',
    '<defs><linearGradient id="o10g" x1="13" y1="39" x2="36" y2="8" gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#B9BCFC"/><stop offset="1" style="stop-color:var(--ink,#1219F3)"/></linearGradient></defs>'
    + g([IA, IAH], 'url(#o10g)', 5), '4 1 40 42')

add('o11-leaf', OLD, 'Капля-указатель',
    'Форма с одним острым углом сверху справа — сама подложка указывает направление стрелки.',
    f'<path d="M4 24A20 20 0 0 1 24 4H44V24A20 20 0 0 1 24 44A20 20 0 0 1 4 24Z" fill="{B}"/>'
    + scaled(g(list(ia(E=(36, 9), t=(1, -1))), '#fff', 5.2), .78, 23.5, 25))

add('o12-badge', OLD, 'Бейдж ∫100',
    'Горизонтальная плашка: интеграл и «100». Для шапки сайта вместо значка с текстом.',
    f'<rect x="0" y="0" width="96" height="48" rx="24" fill="{B}"/>'
    + scaled(g([INTEGRAL], '#fff', 5.6), .7, 26, 24)
    + g(['M42 16.5l4-3v21'], '#fff', 4.4)
    + f'<g fill="none" stroke="#fff" stroke-width="4.4"><rect x="53" y="13.5" width="11" height="21" rx="5.5"/><rect x="70" y="13.5" width="11" height="21" rx="5.5"/></g>',
    '0 0 96 48')

# ---------------- new ideas ----------------
add('n01-percent', NEW, '100%',
    'Знак процента: пустой «ноль» сверху, залитая «сотка» снизу, черта — стрелка вверх. Отлично читается в 16px.',
    f'<circle cx="13" cy="13" r="6.5" fill="none" stroke="{INK}" stroke-width="4.2"/><circle cx="35" cy="35" r="8.5" fill="{INK}"/>'
    + g(['M8 41L39 10', head((40, 9), (1, -1), 7, 5.6)], INK, 4.2))

add('n02-cap', NEW, 'Ноль в шапочке',
    '«0» в выпускной шапочке: из нуля — в выпускники. Дружелюбно и запоминается.',
    f'<path d="M24 4.5 44 12.5 24 20.5 4 12.5Z" fill="{INK}"/><path d="M13 16.2v6.3c3.5 2.6 18.5 2.6 22 0v-6.3L24 20.5Z" fill="{INK}" opacity=".55"/>'
    + g(['M40.5 14v9'], INK, 2.4) + f'<circle cx="40.5" cy="25" r="2.2" fill="{INK}"/>'
    + f'<circle cx="24" cy="36" r="8.6" fill="none" stroke="{INK}" stroke-width="5"/>')

add('n03-target', NEW, 'В десятку',
    'Мишень и стрела точно в центре — «попасть в сотку».',
    f'<g fill="none" stroke="{INK}" stroke-width="3.6"><circle cx="21" cy="27" r="18"/><circle cx="21" cy="27" r="10"/></g><circle cx="21" cy="27" r="3.8" fill="{INK}"/>'
    + g(['M23 25 43.5 4.5', 'M40.5 2.5V7.5H45.5', 'M36.5 6.5V11.5H41.5'], INK, 3.6))

add('n04-check', NEW, 'Галочка-стрелка',
    'Галочка «сдано», у которой длинный штрих продолжается стрелкой вверх.',
    f'<circle cx="24" cy="24" r="24" fill="{B}"/>' + g(['M11 25l8.5 8.5L36 15', head((36.5, 14.4), (1, -1.1), 6.5, 5)], '#fff', 4.8))

add('n05-sqrt', NEW, 'Корень-стрелка',
    'Знак квадратного корня, длинный штрих которого уходит вверх стрелкой. Математика без интеграла.',
    f'<rect width="48" height="48" rx="14" fill="{B}"/>' + g(['M8 27l4.5-2.6L19 37 33 9', head((33.4, 8.2), (14, -28), 6.4, 5)], '#fff', 4.6))

add('n06-parabola', NEW, 'Парабола',
    'y = x²: правая ветка параболы стартует из вершины-нуля и уходит вверх стрелкой.',
    f'<circle cx="24" cy="24" r="24" fill="{B}"/>' + g(['M11 12Q17.5 33 24 33'], '#fff', 4.2, 'stroke-opacity=".45"') + g(['M24 33Q30.5 33 37 12', head((37, 12), (6.5, -21), 6, 4.8)], '#fff', 4.4)
    + f'<circle cx="24" cy="33" r="4" fill="{B}" stroke="#fff" stroke-width="2.8"/>')

T = 2.2 * math.pi
pe = math.radians(225)
raw = []
for i in range(0, 221):
    th = i / 220 * T
    rr = 1.2 + 2.9 * th
    ph = pe - T + th
    raw.append((rr * math.cos(ph), rr * math.sin(ph)))
dx, dy = math.sqrt(.5), -math.sqrt(.5)
tip = (raw[-1][0] + dx * 11, raw[-1][1] + dy * 11)
xs = [p[0] for p in raw] + [tip[0]]
ys = [p[1] for p in raw] + [tip[1]]
ox, oy = 24 - (min(xs) + max(xs)) / 2, 24 - (min(ys) + max(ys)) / 2
pts = [(x + ox, y + oy) for x, y in raw]
tip = (tip[0] + ox, tip[1] + oy)
sp = 'M' + 'L'.join(f'{f(x)} {f(y)}' for x, y in pts) + f'L{f(tip[0])} {f(tip[1])}'
add('n07-spiral', NEW, 'Спираль роста',
    'Спираль раскручивается из точки-нуля и вылетает стрелкой вверх — рост виток за витком.',
    g([sp, head(tip, (dx, dy), 5.8, 4.6)], INK, 3.6)
    + f'<circle cx="{f(pts[0][0])}" cy="{f(pts[0][1])}" r="2.6" fill="{INK}"/>')

add('n08-sunrise', NEW, 'Восход',
    'Солнце поднимается над горизонтом — новый старт, движение вверх.',
    f'<path d="M10 33A14 14 0 0 1 38 33Z" fill="{INK}"/>' + g(['M4 39.5H44', 'M24 4.5v5', 'M4.5 16l4.3 2.6', 'M43.5 16l-4.3 2.6', 'M11 7.8l3 4', 'M37 7.8l-3 4'], INK, 3.6))

add('n09-chevrons', NEW, 'Три шеврона',
    'Нашивка-звание: три шеврона вверх, каждый ярче предыдущего — уровни подготовки.',
    f'<rect width="48" height="48" rx="14" fill="{B}"/>'
    + g(['M13 37 24 30 35 37'], '#fff', 4.6, 'stroke-opacity=".4"') + g(['M13 28 24 21 35 28'], '#fff', 4.6, 'stroke-opacity=".7"') + g(['M13 19 24 12 35 19'], '#fff', 4.6))

add('n10-bars', NEW, '0 → столбики',
    'Диаграмма, где первый столбик — пустое кольцо «0», а последний — до самого верха.',
    f'<circle cx="9.5" cy="37.5" r="4.2" fill="none" stroke="{INK}" stroke-width="3.4"/>'
    f'<rect x="18" y="23" width="9" height="19" rx="3" fill="{INK}" opacity=".6"/><rect x="32" y="6" width="9" height="36" rx="3" fill="{INK}"/>')

add('n11-book', NEW, 'Книга-стрелка',
    'Открытая книга, страницы которой складываются в стрелку вверх: учёба и есть движение вверх.',
    f'<path d="M24 8 5 18.5V42l19-9Z" fill="{INK}"/><path d="M24 8 43 18.5V42l-19-9Z" fill="{INK}" opacity=".55"/>'
    + g(['M9 24.5 20.5 18', 'M9 30.5 20.5 24', 'M39 24.5 27.5 18', 'M39 30.5 27.5 24'], '#fff', 2.2, 'stroke-opacity=".85"'))

cells = [(2, 0), (3, 0), (4, 0), (4, 1), (4, 2), (3, 1), (2, 2), (1, 3)]
px = ''.join(f'<rect x="{f(0.5 + c * 9.6)}" y="{f(0.5 + r * 9.6)}" width="8.2" height="8.2" rx="2" fill="{INK}"/>' for c, r in cells)
px += f'<rect x="1.6" y="{f(1.6 + 4 * 9.6)}" width="6" height="6" rx="1.4" fill="none" stroke="{INK}" stroke-width="2.2"/>'
add('n12-pixel', NEW, 'Пиксельная стрелка',
    'Стрелка из квадратиков, первый пустой — «ноль». Пиксельная сетка даёт идеальную чёткость на 16px.', px)

add('n13-lines', NEW, 'Три полосы',
    'Три шкалы прогресса: пустая, наполовину, полная — от нуля до ста.',
    f'<rect width="48" height="48" rx="14" fill="{B}"/>' + g(['M12 14H36', 'M12 24H36', 'M12 34H36'], '#fff', 5.4, 'stroke-opacity=".3"') + g(['M12 14h.01', 'M12 24H24', 'M12 34H36'], '#fff', 5.4))

add('n14-peak', NEW, 'Вершина',
    'Гора с флагом на пике: взятая вершина = 100 баллов.',
    f'<path d="M3 42 16.5 21l5.5 8 8-13 15 26Z" fill="{INK}"/>' + g(['M30 16V5'], INK, 2.6) + f'<path d="M30 4.5 39 8l-9 3.5Z" fill="{INK}"/>')

add('n15-hundred', NEW, 'Сотка',
    'Цифры 100: единица — это стрелка вверх, нули сцеплены, второй ярче первого.',
    g(['M8 42V9', head((8, 7), (0, -1), 5.5, 4.6)], INK, 4.2)
    + f'<circle cx="23" cy="26" r="8.5" fill="none" stroke="{INK}" stroke-opacity=".45" stroke-width="4.2"/><circle cx="36" cy="26" r="8.5" fill="none" stroke="{INK}" stroke-width="4.2"/>')

grid = ''
for r in range(3):
    for c in range(3):
        d = c + (2 - r)
        x, y = c * 17.5, r * 17.5
        if d == 0:
            grid += f'<rect x="{x + 1.5}" y="{y + 1.5}" width="10" height="10" rx="2.6" fill="none" stroke="{INK}" stroke-width="2.6"/>'
        else:
            grid += f'<rect x="{x}" y="{y}" width="13" height="13" rx="3.4" fill="{INK}" opacity="{f(.2 + d * .2)}"/>'
add('n16-grid', NEW, 'Сетка прогресса',
    'Квадраты заполняются по диагонали от пустого «нуля» к самому яркому — как тепловая карта успехов.', grid)

add('n17-pencil', NEW, 'Карандаш-стрелка',
    'Карандаш, направленный вверх-вправо, работает как стрелка; на ластике — «ноль».',
    '<g transform="rotate(45 24 24)">'
    f'<path d="M16 17 24 1.5 32 17Z" fill="{INK}" opacity=".55"/><path d="M21.6 6.2 24 1.5l2.4 4.7Z" fill="{INK}"/>'
    f'<rect x="16" y="17" width="16" height="20" fill="{INK}"/>'
    f'<rect x="17.6" y="39.2" width="12.8" height="7.4" rx="3.2" fill="none" stroke="{INK}" stroke-width="2.6"/></g>')

add('n18-pennant', NEW, 'Стрела-флажок',
    'Силуэт закладки, превращённый в стрелку вверх, с «нулём» внутри.',
    f'<path d="M11 45V19.5L24 3l13 16.5V45l-13-8.5Z" fill="{B}"/><circle cx="24" cy="23" r="5" fill="none" stroke="#fff" stroke-width="3.2"/>')

# ---------------- page ----------------
os.makedirs(OUT, exist_ok=True)
for key, *_rest, s in L:
    with open(os.path.join(OUT, key + '.svg'), 'w', encoding='utf-8') as fh:
        fh.write(s)

cur = open(CUR, encoding='utf-8').read()
cur = cur[cur.index('<svg'):].replace('width="1760.000000pt" height="2402.000000pt"', '')


def card(num, title, note, s, fname, cls=''):
    sizes = ''.join(f'<span class=s style="width:{z}px;height:{z}px">{s}</span>' for z in (64, 32, 24, 16))
    lock = f'<span class=s style="width:30px;height:30px">{s}</span>Из нуля в сотку'
    return (f'<article class="{cls}"><header><b>{num}</b> {html.escape(title)}</header><div class=hero>{s}</div>'
            f'<div class=row>{sizes}</div><div class="row dark">{sizes}</div>'
            f'<div class=lock>{lock}</div><div class="lock dark">{lock}</div>'
            f'<p>{html.escape(note)}</p><code>{fname}</code></article>')


old = ''.join(card(f'{i + 1:02}', t, nt, s, k + '.svg') for i, (k, gr, t, nt, s) in enumerate(L) if gr == OLD)
new = ''.join(card(f'{i + 1:02}', t, nt, s, k + '.svg') for i, (k, gr, t, nt, s) in enumerate(L) if gr == NEW)
curcard = card('—', 'Текущий', 'Для сравнения.', cur, 'frontend/src/shared/assets/icons/logo.svg', 'cur')

page = f'''<!doctype html><html lang=ru><meta charset=utf-8><title>Логотип — 30 концептов</title>
<style>
body{{margin:0;padding:24px;background:#f4f5fb;font:14px/1.45 Mulish,system-ui,sans-serif;color:#14151f}}
h1{{font-size:22px;margin:0 0 4px}}h2{{font-size:17px;margin:28px 0 12px}}.sub{{color:#666;margin:0 0 8px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(270px,1fr));gap:14px}}
article{{background:#fff;border-radius:16px;padding:14px;box-shadow:0 1px 3px #0001}}
article.cur{{outline:2px dashed #c33}}
header{{font-size:15px;font-weight:700;margin-bottom:8px}}header b{{color:#1219F3;margin-right:6px}}
.hero{{width:120px;height:120px;margin:4px auto 12px;display:flex;align-items:center;justify-content:center}}
.hero svg,.s svg{{width:100%;height:100%;display:block}}
.row{{display:flex;align-items:center;gap:14px;padding:9px 12px;border-radius:10px;border:1px solid #eee;margin-bottom:6px}}
.s{{display:inline-flex;align-items:center;flex:none}}
.dark{{background:#16171f;border-color:#16171f;color:#f5f5f5;--ink:#7C81FF}}
.lock{{display:flex;align-items:center;gap:10px;font-weight:800;font-size:18px;letter-spacing:-.03em;padding:8px 12px;border-radius:10px;border:1px solid #eee;margin-bottom:6px}}
p{{margin:10px 0 4px;color:#444}}code{{color:#999;font-size:12px}}
</style><body>
<h1>Логотип «Из нуля в сотку» — 30 концептов</h1>
<p class=sub>Сетка 48×48. Ряды: 64 / 32 / 24 / 16px на светлом и тёмном фоне, ниже — шапка сайта. Контурные знаки на тёмном фоне автоматически светлеют.</p>
<div class=grid>{curcard}</div>
<h2>Развитие старого лого (12)</h2><div class=grid>{old}</div>
<h2>Новые идеи (18)</h2><div class=grid>{new}</div>
</body></html>'''
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(page)
print(len(L))
