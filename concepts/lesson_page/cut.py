"""Нарезка video/logarithms/logarithms.mp4 на короткие ролики урока.

    py -3.12 concepts/lesson_page/cut.py

Границы роликов совпадают с началами сцен (data-dur в logarithms.html) и с полем clip в static/lesson.js.
"""
import subprocess
from pathlib import Path

import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "video" / "logarithms" / "logarithms.mp4"
OUT = Path(__file__).resolve().parent / "static" / "media"

# (файл, начало, конец) в секундах
CLIPS = [
    ("log-1-definition", 0, 56),
    ("log-2-properties", 56, 116),
    ("log-3-new-base", 116, 154),
    ("log-4-ege", 154, 207),
    ("log-5-mistakes", 207, 246),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    for name, start, end in CLIPS:
        base = [ffmpeg, "-y", "-loglevel", "error", "-ss", str(start), "-to", str(end), "-i", str(SRC)]
        subprocess.run(base + [
            "-vf", "scale=1280:-2", "-c:v", "libx264", "-preset", "medium", "-crf", "24",
            "-pix_fmt", "yuv420p", "-an", "-movflags", "+faststart", str(OUT / f"{name}.mp4"),
        ], check=True)
        # постер — кадр за секунду до конца ролика: формулы сцены уже на экране
        subprocess.run(base[:4] + ["-ss", str(end - 1), "-i", str(SRC), "-frames:v", "1",
                                   "-vf", "scale=1280:-2", "-q:v", "4", str(OUT / f"{name}.jpg")], check=True)
        print(name, end - start, "s")


if __name__ == "__main__":
    main()
