"""Собирает ege-map.html из текстового плана (plan.txt) и шаблона (template.html).

    python parse.py [plan.txt] [template.html] [ege-map.html]

Без аргументов читает и пишет файлы рядом со скриптом.
"""
import json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
args = sys.argv[1:] + [None] * 3
SRC = Path(args[0] or HERE / "plan.txt")
TPL = Path(args[1] or HERE / "template.html")
OUT = Path(args[2] or HERE / "ege-map.html")
lines = SRC.read_text(encoding="utf-8").splitlines()

root = {"t": "root", "c": []}
stack = [(-1, root)]
last = None
for raw in lines:
    s = raw.rstrip()
    if not s.strip() or set(s.strip()) <= set("│ "):
        continue
    m = re.match(r"^([│ ]*)([├└]── )?(.*)$", s)
    prefix, conn, text = m.group(1), m.group(2), m.group(3).strip()
    if conn is None and prefix:
        # continuation line
        last["t"] += " · " + text
        continue
    depth = len(prefix) // 4 + (1 if conn else 0)
    node = {"t": text, "c": []}
    while stack[-1][0] >= depth:
        stack.pop()
    stack[-1][1]["c"].append(node)
    stack.append((depth, node))
    last = node

def clean(n):
    out = {"t": n["t"]}
    if n["c"]:
        out["c"] = [clean(x) for x in n["c"]]
    return out

data = [clean(b) for b in root["c"]]
tpl = TPL.read_text(encoding="utf-8")
OUT.write_text(tpl.replace("/*DATA*/", json.dumps(data, ensure_ascii=False)), encoding="utf-8")
print(len(data), [len(b["c"]) for b in data], sum(len(l["c"]) for b in data for l in b["c"]))
