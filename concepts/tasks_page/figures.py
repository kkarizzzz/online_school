"""
Рисунки к тестовым заданиям (SVG).

В реальном проекте картинки скачивает парсер и кладёт в S3/MinIO,
а здесь мы их генерируем, чтобы концепт был самодостаточным.
"""
from typing import Callable

FONT = "font-family='Times New Roman, serif' font-style='italic'"
NUM_FONT = "font-family='Times New Roman, serif'"


def _fmt(value: float) -> str:
    return f'{value:g}'.replace('.', ',')


def right_triangle(ac: float, bc: float) -> str:
    """Прямоугольный треугольник ABC с прямым углом C (длинный катет растягиваем до 200 px)"""
    scale = 200 / max(ac, bc)
    cx, cy = 50, 30 + ac * scale
    ax, ay = cx, 30
    bx, by = cx + bc * scale, cy
    width, height = int(bx + 50), int(cy + 40)
    return f"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {width} {height}' width='{width}' height='{height}'>
  <rect width='100%' height='100%' fill='white'/>
  <polygon points='{ax},{ay} {bx},{by} {cx},{cy}' fill='none' stroke='black' stroke-width='2'/>
  <polyline points='{cx},{cy - 14} {cx + 14},{cy - 14} {cx + 14},{cy}' fill='none' stroke='black' stroke-width='1.5'/>
  <text x='{ax - 22}' y='{ay + 6}' font-size='20' {FONT}>A</text>
  <text x='{bx + 8}' y='{by + 6}' font-size='20' {FONT}>B</text>
  <text x='{cx - 22}' y='{cy + 20}' font-size='20' {FONT}>C</text>
  <text x='{cx - 30}' y='{(ay + cy) / 2 + 6}' font-size='18' {NUM_FONT}>{_fmt(ac)}</text>
  <text x='{(cx + bx) / 2 - 6}' y='{cy + 24}' font-size='18' {NUM_FONT}>{_fmt(bc)}</text>
</svg>"""


def _axes_grid(x_min, x_max, y_min, y_max, scale, x_label, y_label):
    """Сетка, оси со стрелками и подписи единичных отрезков. Возвращает начало svg и функции перевода координат"""
    ox = -x_min * scale + 30
    oy = y_max * scale + 30
    width = (x_max - x_min) * scale + 80
    height = (y_max - y_min) * scale + 60
    sx = lambda x: ox + x * scale
    sy = lambda y: oy - y * scale

    parts = [
        f"<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 {width} {height}' width='{width}' height='{height}'>",
        "<rect width='100%' height='100%' fill='white'/>",
        "<defs><marker id='arr' viewBox='0 0 10 10' refX='9' refY='5' markerWidth='7' markerHeight='7' orient='auto'>"
        "<path d='M0,0 L10,5 L0,10 z' fill='black'/></marker></defs>",
    ]
    for x in range(x_min, x_max + 1):
        parts.append(f"<line x1='{sx(x)}' y1='{sy(y_max)}' x2='{sx(x)}' y2='{sy(y_min)}' stroke='#d0d0d0' stroke-width='1'/>")
    for y in range(y_min, y_max + 1):
        parts.append(f"<line x1='{sx(x_min)}' y1='{sy(y)}' x2='{sx(x_max)}' y2='{sy(y)}' stroke='#d0d0d0' stroke-width='1'/>")
    parts += [
        f"<line x1='{sx(x_min) - 10}' y1='{oy}' x2='{sx(x_max) + 18}' y2='{oy}' stroke='black' stroke-width='1.5' marker-end='url(#arr)'/>",
        f"<line x1='{ox}' y1='{sy(y_min) + 10}' x2='{ox}' y2='{sy(y_max) - 18}' stroke='black' stroke-width='1.5' marker-end='url(#arr)'/>",
        f"<text x='{sx(x_max) + 12}' y='{oy + 22}' font-size='18' {FONT}>{x_label}</text>",
        f"<text x='{ox + 8}' y='{sy(y_max) - 6}' font-size='18' {FONT}>{y_label}</text>",
        f"<text x='{ox - 14}' y='{oy + 18}' font-size='15' {NUM_FONT}>0</text>",
        f"<text x='{sx(1) - 4}' y='{oy + 18}' font-size='15' {NUM_FONT}>1</text>",
        f"<text x='{ox - 14}' y='{sy(1) + 5}' font-size='15' {NUM_FONT}>1</text>",
    ]
    return ''.join(parts), sx, sy


def function_graph(f: Callable[[float], float], x_min: int, x_max: int, y_min: int, y_max: int) -> str:
    """График y = f(x) на интервале (x_min; x_max) с выколотыми концами"""
    head, sx, sy = _axes_grid(x_min, x_max, y_min, y_max, 34, 'x', 'y')
    steps = (x_max - x_min) * 20
    xs = [x_min + i * (x_max - x_min) / steps for i in range(steps + 1)]
    points = ' '.join(f'{sx(x):.1f},{sy(f(x)):.1f}' for x in xs)
    curve = f"<polyline points='{points}' fill='none' stroke='black' stroke-width='2.5'/>"
    ends = ''.join(
        f"<circle cx='{sx(x):.1f}' cy='{sy(f(x)):.1f}' r='4' fill='white' stroke='black' stroke-width='2'/>"
        for x in (x_min, x_max)
    )
    return head + curve + ends + '</svg>'


# f'(x) = k·(x + 2)(x − 1)(x − 3,5) — три экстремума на (−3; 5)
graph_three_extrema = lambda x: 0.25 * (x ** 4 / 4 - 2.5 * x ** 3 / 3 - 2.75 * x ** 2 + 7 * x)
# f'(x) = −k·(x + 1)(x − 2) — два экстремума на (−3; 4)
graph_two_extrema = lambda x: -0.5 * (x ** 3 / 3 - x ** 2 / 2 - 2 * x)


FIGURES = {
    'figures/math-1-triangle-6-8.svg': lambda: right_triangle(6, 8),
    'figures/math-1-triangle-5-12.svg': lambda: right_triangle(5, 12),
    'figures/math-1-triangle-9-12.svg': lambda: right_triangle(9, 12),
    'figures/math-8-graph-a.svg': lambda: function_graph(graph_three_extrema, -3, 5, -4, 5),
    'figures/math-8-graph-b.svg': lambda: function_graph(graph_two_extrema, -3, 4, -3, 4),
}
