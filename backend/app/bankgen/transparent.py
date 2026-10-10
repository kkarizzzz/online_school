"""
Картинки ФИПИ → прозрачные PNG вдвое крупнее (data/fipi/img → data/bank/fipi/<имя>@2x.png).
Суффикс @2x фронтенд понимает как плотность 2x: картинка показывается в прежнем размере, но чётче.

Белый фон «вычитается»: пиксель (r, g, b) на белом считаем смесью цвета c с прозрачностью a,
a = 255 − min(r, g, b), c = (p − (255 − a)) / a. Чёрное остаётся чёрным, белое становится прозрачным,
цветные линии сохраняют цвет. Фронтенд в тёмной теме инвертирует такие картинки — линии становятся светлыми.

Нужен Pillow, которого нет в зависимостях backend, поэтому запускается отдельно, например в контейнере:
    docker run --rm -v <backend>/data:/data python:3.12-slim sh -c \
        "pip install -q pillow numpy && python /t.py /data"  (с -v <backend>/app/bankgen/transparent.py:/t.py)
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

SCALE = 2


def convert(src: Path, dst: Path) -> None:
    im = Image.open(src).convert('RGBA')
    bg = Image.new('RGBA', im.size, 'white')
    im = Image.alpha_composite(bg, im).convert('RGB')        # своя прозрачность у gif — на белый
    im = im.resize((im.width * SCALE, im.height * SCALE), Image.LANCZOS)
    p = np.asarray(im).astype(np.float32)
    a = 255 - p.min(axis=2)
    a = np.clip((a - 8) * 255 / (255 - 8), 0, 255)           # шум JPEG/GIF около белого — в ноль
    safe = np.maximum(a, 1)[..., None]
    c = np.clip((p - (255 - safe)) * 255 / safe, 0, 255)
    out = np.dstack([c, a]).astype(np.uint8)
    Image.fromarray(out, 'RGBA').save(dst, optimize=True)


def main(data: Path) -> None:
    src, dst = data / 'fipi' / 'img', data / 'bank' / 'fipi'
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted(src.iterdir()):
        out = dst / (f.stem + '@2x.png')
        if out.exists() and out.stat().st_mtime >= f.stat().st_mtime:
            continue
        convert(f, out)
        n += 1
    print(f'прозрачных картинок: {n} новых, всего {len(list(dst.iterdir()))}')


if __name__ == '__main__':
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parents[2] / 'data')
