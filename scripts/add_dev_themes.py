# Add _w_header and _w_viewbar variants for every Bubble* / Dubble* / Hubba* theme.
# _w_header: Header widoczny (card-mod nie chowa headera na mobile)
# _w_viewbar: Header na dole, toolbar, viewbar layout

import re
import sys
from pathlib import Path

PATH = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "bubble_2026.yaml")

with open(PATH, "r", encoding="utf-8") as f:
    lines = f.readlines()

theme_pattern = re.compile(r"^(Bubble .*|Dubble .*|Hubba .*):\s*$")

def is_variant(name):
    return (
        name.endswith(" _w_header") or
        name.endswith(" _w_viewbar") or
        name.endswith(" Header") or
        name.endswith(" dev-Theme")
    )

blocks = []
i = 0
while i < len(lines):
    m = theme_pattern.match(lines[i])
    if m:
        name = lines[i].rstrip()[:-1].rstrip()
        if is_variant(name):
            i += 1
            continue
        start = i
        i += 1
        while i < len(lines):
            if theme_pattern.match(lines[i]):
                break
            if lines[i].strip().startswith("# ======"):
                break
            i += 1
        end = i - 1
        blocks.append((start, end, name))
        continue
    i += 1

out = []
prev_end = -1
for start, end, name in blocks:
    for j in range(prev_end + 1, start):
        out.append(lines[j])
    block_lines = lines[start : end + 1]
    out.extend(block_lines)

    # _w_header variant
    w_header_lines = []
    added_mod = False
    for idx, line in enumerate(block_lines):
        if idx == 0:
            w_header_lines.append(name + " _w_header:\n")
            continue
        if line.strip() == "<<: *bubble_shared":
            w_header_lines.append(line)
            if not added_mod:
                w_header_lines.append("  <<: *bubble_w_header_mod\n")
                added_mod = True
            continue
        w_header_lines.append(line)
    out.extend(w_header_lines)

    # _w_viewbar variant
    w_viewbar_lines = []
    added_mod = False
    for idx, line in enumerate(block_lines):
        if idx == 0:
            w_viewbar_lines.append(name + " _w_viewbar:\n")
            continue
        if line.strip() == "<<: *bubble_shared":
            w_viewbar_lines.append(line)
            if not added_mod:
                w_viewbar_lines.append("  <<: *bubble_w_viewbar_mod\n")
                added_mod = True
            continue
        w_viewbar_lines.append(line)
    out.extend(w_viewbar_lines)

    prev_end = end

for j in range(prev_end + 1, len(lines)):
    out.append(lines[j])

with open(PATH, "w", encoding="utf-8") as f:
    f.writelines(out)

print(f"Added {len(blocks) * 2} variants (_w_header + _w_viewbar) for {len(blocks)} themes.")
