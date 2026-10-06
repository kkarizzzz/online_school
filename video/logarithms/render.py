"""Рендер logarithms.html в MP4 покадрово.

    py -3.12 render.py              # полный рендер -> logarithms.mp4
    py -3.12 render.py --stills     # контрольные кадры (конец каждой сцены) -> stills/
"""
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
URL = (HERE / "logarithms.html").as_uri() + "?capture"
FPS = 30
W, H = 1920, 1080


def main():
    stills = "--stills" in sys.argv
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        page = browser.new_page(viewport={"width": W, "height": H})
        page.goto(URL)
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(500)
        duration = page.evaluate("window.__DURATION")

        if stills:
            out = HERE / "stills"
            out.mkdir(exist_ok=True)
            ends = page.evaluate(
                "[...document.querySelectorAll('.scene')].map(s => s._start + s._dur - 0.6)"
            )
            for i, t in enumerate(ends, 1):
                page.evaluate(f"__render({t})")
                page.screenshot(path=str(out / f"scene{i:02d}.png"))
            print("stills ->", out)
            return

        ffmpeg = subprocess.Popen(
            [
                imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                "-movflags", "+faststart", str(HERE / "logarithms.mp4"),
            ],
            stdin=subprocess.PIPE,
        )
        frames = int(duration * FPS)
        for f in range(frames + 1):
            page.evaluate(f"__render({f / FPS})")
            ffmpeg.stdin.write(page.screenshot(type="jpeg", quality=95))
            if f % (FPS * 10) == 0:
                print(f"{f / FPS:6.1f}s / {duration}s", flush=True)
        ffmpeg.stdin.close()
        ffmpeg.wait()
        browser.close()
        print("done ->", HERE / "logarithms.mp4")


if __name__ == "__main__":
    main()
