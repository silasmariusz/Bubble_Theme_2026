# Remove all variant blocks: dev-Theme, Header, _w_header, _w_viewbar

import re
import sys
from pathlib import Path

PATH = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "bubble_2026.yaml")

with open(PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

variant_pattern = re.compile(
    r"^(.+ )(?:dev-Theme|Header|_w_header|_w_viewbar):\s*$"
)
theme_pattern = re.compile(r"^(Bubble .*|Dubble .*|Hubba .*):\s*$")

out = []
i = 0
while i < len(lines):
    if variant_pattern.match(lines[i]):
        i += 1
        while i < len(lines):
            if theme_pattern.match(lines[i]):
                break
            if lines[i].strip().startswith("# ======"):
                break
            i += 1
        continue
    out.append(lines[i])
    i += 1

with open(PATH, "w", encoding="utf-8") as f:
    f.writelines(out)

print("Removed all dev-Theme, Header, _w_header, _w_viewbar blocks.")
