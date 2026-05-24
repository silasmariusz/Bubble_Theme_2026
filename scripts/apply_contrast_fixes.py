#!/usr/bin/env python3
"""
Audyt kontrastu WCAG 4.5:1 i automatyczne korekty HSL dla bubble-accent-color.

Zakres: motywy od commitu e684ac2.
Kryterium: token-text-on-accent na tle token-accent musi mieć >= 4.5:1 (WCAG AA).

Użycie:
  python apply_contrast_fixes.py [ścieżka.yaml]           # dry-run, raport
  python apply_contrast_fixes.py [ścieżka.yaml] --apply   # zastosuj zmiany
"""

import re
import sys
from pathlib import Path

from list_themes_for_audit import THEMES_BEFORE_E684AC2, find_yaml_path, extract_themes
from contrast_utils import (
    parse_color,
    get_contrast_info,
    find_accent_hsl_delta,
    MIN_CONTRAST_RATIO,
)


def parse_theme_blocks(content: str, theme_infos: list) -> dict:
    """Wyciąga bloki YAML per motyw. Zwraca {name: [(start_line, end_line, block_text)]}."""
    lines = content.splitlines()
    result = {}
    for name, start_line in theme_infos:
        i = start_line - 1
        block_end = len(lines)
        for j in range(i + 1, len(lines)):
            line = lines[j]
            if line and not line[0].isspace() and re.match(r"^[A-Za-z][A-Za-z0-9 \-_()]*:\s*$", line):
                block_end = j
                break
        block_lines = lines[i:block_end]
        result[name] = (start_line, block_end, "\n".join(block_lines))
    return result


def extract_mode_colors(block: str) -> dict:
    """Wyciąga token-accent i token-text-on-accent z dark i light."""
    out = {"dark": {}, "light": {}}
    mode = None
    for line in block.splitlines():
        if "dark:" in line and line.strip().startswith("dark:"):
            mode = "dark"
            continue
        if "light:" in line and line.strip().startswith("light:"):
            mode = "light"
            continue
        if mode:
            m = re.match(r"\s+token-accent:\s*(.+)", line)
            if m:
                out[mode]["accent"] = m.group(1).strip().strip('"\'')
            m = re.match(r"\s+token-text-on-accent:\s*(.+)", line)
            if m:
                out[mode]["text"] = m.group(1).strip().strip('"\'')
    return out


def compute_fixes(themes_to_audit: list, blocks: dict) -> dict:
    """Dla każdego motywu i trybu: sprawdź kontrast, zwróć potrzebne korekty."""
    fixes = {}  # (theme, mode) -> {"delta": (0,0,dL), "info": {...}, "line_start": int}
    for name, (start_line, end_line, block) in blocks.items():
        if name in THEMES_BEFORE_E684AC2:
            continue
        colors = extract_mode_colors(block)
        for mode in ("dark", "light"):
            acc = colors.get(mode, {}).get("accent")
            txt = colors.get(mode, {}).get("text")
            if not acc or not txt:
                continue
            info = get_contrast_info(txt, acc)
            delta = find_accent_hsl_delta(txt, acc)
            if not info.get("pass") or delta:
                key = (name, mode)
                fixes[key] = {
                    "delta": delta,
                    "info": info,
                    "accent": acc,
                    "text": txt,
                }
    return fixes


def hsl_override(delta_l: float) -> str:
    """Generuje wartość CSS hsl(from var(--token-accent) ...) z deltą L."""
    d = int(round(delta_l))
    if d >= 0:
        return f'hsl(from var(--token-accent) h s calc(l + {d}))'
    return f'hsl(from var(--token-accent) h s calc(l - {-d}))'


def apply_fixes_to_content(content: str, fixes: dict, blocks: dict) -> str:
    """Zastosowuje korekty HSL w treści YAML."""
    lines = content.splitlines()
    # Dla każdego (theme, mode) znajdź linie bubble-accent w tym bloku
    for (name, mode), fix in fixes.items():
        if not fix.get("delta"):
            continue
        delta = fix["delta"]
        override = hsl_override(delta[2])
        start_line, end_line, block = blocks[name]
        # Szukamy w bloku linii z bubble-accent w trybie dark/light
        in_block = False
        current_mode = None
        for i in range(start_line - 1, min(end_line, len(lines))):
            line = lines[i]
            stripped = line.strip()
            if stripped == "dark:":
                current_mode = "dark"
                continue
            if stripped == "light:":
                current_mode = "light"
                continue
            if current_mode == mode:
                if "bubble-accent-color:" in line and "var(--token-accent)" in line:
                    if "hsl(from" not in line:
                        lines[i] = re.sub(
                            r'bubble-accent-color:\s*.+',
                            f'bubble-accent-color: {override}',
                            line, count=1
                        )
                if "bubble-button-accent-color:" in line and "var(--token-accent)" in line:
                    if "hsl(from" not in line:
                        lines[i] = re.sub(
                            r'bubble-button-accent-color:\s*.+',
                            f'bubble-button-accent-color: {override}',
                            line, count=1
                        )
    return "\n".join(lines)


def main():
    apply_mode = "--apply" in sys.argv
    args = [a for a in sys.argv[1:] if a != "--apply"]
    yaml_path = Path(args[0]) if args else find_yaml_path()

    if not yaml_path.exists():
        print(f"Brak pliku: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    content = yaml_path.read_text(encoding="utf-8")
    theme_infos = extract_themes(content)
    to_audit = [(n, ln) for n, ln in theme_infos if n not in THEMES_BEFORE_E684AC2]
    blocks = parse_theme_blocks(content, theme_infos)
    fixes = compute_fixes(to_audit, blocks)

    # Raport
    need_fix = [(k, v) for k, v in fixes.items() if v.get("delta")]
    already_bad = [(k, v) for k, v in fixes.items() if not v.get("info", {}).get("pass") and not v.get("delta")]

    print("=" * 70)
    print("AUDYT KONTRASTU WCAG 4.5:1 (token-text-on-accent na token-accent)")
    print("=" * 70)
    print(f"\nKryterium: >= {MIN_CONTRAST_RATIO}:1 (WCAG AA dla małego tekstu)")
    print(f"Sprawdzono: {len(to_audit) * 2} trybów (dark+light) w {len(to_audit)} motywach")
    print(f"Wymaga korekty HSL: {len(need_fix)}")
    if already_bad:
        print(f"Błąd (brak możliwości korekty): {len(already_bad)}")
    print()

    if need_fix:
        print("Korekty do zastosowania:")
        print("-" * 70)
        for (name, mode), fix in sorted(need_fix, key=lambda x: (x[0][0], x[0][1])):
            ratio = fix["info"].get("ratio", "?")
            delta = fix["delta"]
            override = hsl_override(delta[2])
            print(f"  {name} ({mode}): ratio {ratio} -> {override}")
        print()

    if apply_mode and need_fix:
        new_content = apply_fixes_to_content(content, fixes, blocks)
        yaml_path.write_text(new_content, encoding="utf-8")
        print(f"Zapisano {len(need_fix)} korekt do {yaml_path}")
    elif need_fix:
        print("Uruchom z --apply aby zapisać zmiany.")


if __name__ == "__main__":
    main()
