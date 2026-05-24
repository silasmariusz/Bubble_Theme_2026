#!/usr/bin/env python3
"""
Audyt: czy zmodyfikowany bubble-accent-color mieści się w palecie motywu.

Sprawdza motywy z korektą HSL (bubble-accent-color różne od var(--token-accent)):
- Czy wynikowy accent jest współmierny do palety (token-bg, token-card, token-text)
- Czy accent nie zlewa się z tłem (minimalny kontrast accent/bg)
- Czy korekta nie jest zbyt ekstremalna (akcent nie traci charakteru)

Kryteria "nie współmierny":
1. Accent zbyt blisko bg (contrast accent-bg < 1.5:1) – zlewa się
2. Accent skrajny (luminance < 0.04 lub > 0.96) – prawie czarny/biały
3. Dark theme: accent ciemniejszy od bg – nie wyróżnia się
4. Light theme: accent jaśniejszy od card przy ciemnym oryginale – wygląda obco
5. Duża korekta (|dL| > 28) – znaczące odejście od palety

Użycie:
  python audit_accent_palette.py [ścieżka_do_bubble_2026.yaml]
"""

import re
import sys
from pathlib import Path

from list_themes_for_audit import THEMES_BEFORE_E684AC2, find_yaml_path, extract_themes
from contrast_utils import parse_color, rgb_to_relative_luminance, rgb_to_hsl, hsl_to_rgb, contrast_ratio


def parse_theme_blocks(content: str, theme_infos: list) -> dict:
    """Zwraca {name: (start_line, end_line, block_text)}."""
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


def extract_hsl_delta_from_override(line: str) -> tuple[float, float] | None:
    """
    Parsuje bubble-accent-color: hsl(from var(--token-accent) h s calc(l +/- N))
    lub hsl(from var(--token-accent) h calc(s - X) calc(l - Y))
    Zwraca (delta_s, delta_l) lub None jeśli var(--token-accent).
    """
    if "var(--token-accent)" in line and "hsl(from" not in line:
        return None
    m = re.search(r"hsl\s*\(\s*from\s+var\(--token-accent\)\s+h\s+([^)]+)\)", line)
    if not m:
        return None
    inner = m.group(1)
    delta_s, delta_l = 0.0, 0.0
    # calc(l + N) lub calc(l - N)
    m1 = re.search(r"calc\s*\(\s*l\s*([+-])\s*(\d+)\s*\)", inner)
    if m1:
        sign = 1 if m1.group(1) == "+" else -1
        delta_l = sign * int(m1.group(2))
    # calc(s - N) lub calc(s + N)
    m2 = re.search(r"calc\s*\(\s*s\s*([+-])\s*(\d+)\s*\)", inner)
    if m2:
        sign = 1 if m2.group(1) == "+" else -1
        delta_s = sign * int(m2.group(2))
    return (delta_s, delta_l)


def extract_mode_data(block: str) -> dict:
    """Wyciąga token-accent, token-bg, token-card, bubble-accent-color dla dark/light."""
    out = {"dark": {}, "light": {}}
    mode = None
    for line in block.splitlines():
        if line.strip() == "dark:":
            mode = "dark"
            continue
        if line.strip() == "light:":
            mode = "light"
            continue
        if mode:
            for key, pattern in [
                ("accent", r"token-accent:\s*(.+)"),
                ("bg", r"token-bg:\s*(.+)"),
                ("card", r"token-card:\s*(.+)"),
                ("bubble_accent_line", r"(bubble-accent-color:\s*.+)"),
            ]:
                m = re.match(r"\s+" + pattern, line)
                if m:
                    val = m.group(1).strip().strip('"\'')
                    if key == "bubble_accent_line":
                        out[mode]["bubble_accent_raw"] = val
                        # Parse delta
                        d = extract_hsl_delta_from_override(line)
                        out[mode]["hsl_delta"] = d
                    else:
                        out[mode][key] = val
                    break
    return out


def compute_modified_accent(accent_rgb: tuple, delta_s: float, delta_l: float) -> tuple[float, float, float]:
    """Oblicza RGB po zastosowaniu delty S i L w HSL."""
    h, s, l = rgb_to_hsl(*accent_rgb)
    new_s = max(0, min(100, s + delta_s))
    new_l = max(0, min(100, l + delta_l))
    return hsl_to_rgb(h, new_s, new_l)


def main():
    yaml_path = Path(sys.argv[1]) if len(sys.argv) > 1 else find_yaml_path()
    if not yaml_path.exists():
        print(f"Brak pliku: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    content = yaml_path.read_text(encoding="utf-8")
    theme_infos = extract_themes(content)
    blocks = parse_theme_blocks(content, theme_infos)

    issues = []  # (theme, mode, reason, details)

    for name, (_, _, block) in blocks.items():
        if name in THEMES_BEFORE_E684AC2:
            continue
        data = extract_mode_data(block)

        for mode in ("dark", "light"):
            d = data.get(mode, {})
            accent_raw = d.get("accent")
            bg_raw = d.get("bg")
            card_raw = d.get("card")
            hsl_delta = d.get("hsl_delta")

            if not accent_raw or not bg_raw:
                continue

            accent_rgb = parse_color(accent_raw)
            bg_rgb = parse_color(bg_raw)
            card_rgb = parse_color(card_raw) if card_raw else None

            if not accent_rgb or not bg_rgb:
                continue

            # Tylko motywy z korektą HSL
            if not hsl_delta:
                continue

            delta_s, delta_l = hsl_delta
            mod_accent_rgb = compute_modified_accent(accent_rgb, delta_s, delta_l)
            mod_accent_lum = rgb_to_relative_luminance(*mod_accent_rgb)
            accent_lum = rgb_to_relative_luminance(*accent_rgb)
            bg_lum = rgb_to_relative_luminance(*bg_rgb)
            card_lum = rgb_to_relative_luminance(*card_rgb) if card_rgb else bg_lum

            # 1. Accent zlewa się z tłem (contrast < 1.5)
            acc_bg_ratio = contrast_ratio(mod_accent_lum, bg_lum)
            if acc_bg_ratio < 1.5:
                issues.append((name, mode, "accent_zlewa_sie_z_tlem",
                    f"contrast accent/bg = {acc_bg_ratio:.2f}:1 (min 1.5)"))

            # 2. Accent skrajny – prawie czarny/biały
            if mod_accent_lum < 0.04:
                issues.append((name, mode, "accent_prawie_czarny",
                    f"luminance = {mod_accent_lum:.3f}"))
            elif mod_accent_lum > 0.96:
                issues.append((name, mode, "accent_prawie_bialy",
                    f"luminance = {mod_accent_lum:.3f}"))

            # 3. Dark theme: accent ciemniejszy od bg
            if bg_lum < 0.25 and mod_accent_lum < bg_lum - 0.02:
                issues.append((name, mode, "dark_accent_ciemniejszy_od_bg",
                    f"accent lum {mod_accent_lum:.3f} < bg {bg_lum:.3f}"))

            # 4. Light theme: accent za jasny względem card (gdy oryginał był ciemny)
            if bg_lum > 0.5 and accent_lum < 0.3 and mod_accent_lum > card_lum + 0.15:
                issues.append((name, mode, "light_accent_wyprany",
                    f"accent {mod_accent_lum:.3f} >> card {card_lum:.3f}"))

            # 5. Bardzo duża korekta
            if abs(delta_l) > 28 or abs(delta_s) > 15:
                issues.append((name, mode, "duza_korekta",
                    f"dL={delta_l}, dS={delta_s}"))

    # Raport
    print("=" * 72)
    print("AUDYT: bubble-accent-color vs paleta motywu")
    print("=" * 72)
    print("\nSprawdzone: motywy z korektą HSL (różne od var(--token-accent))")
    print("Kryteria: zlewa się z tłem, skrajna luminancja, niespójność dark/light,")
    print("          zbyt duża korekta (|dL|>28)")
    print()

    if not issues:
        print("Brak problemów – wszystkie zmodyfikowane accent mieszczą się w palecie.")
        return

    # Grupuj po motywie
    by_theme = {}
    for theme, mode, reason, detail in issues:
        key = (theme, mode)
        if key not in by_theme:
            by_theme[key] = []
        by_theme[key].append((reason, detail))

    # Unikalne motywy z problemami
    themes_with_issues = sorted(set(t for t, m in by_theme.keys()))

    print(f"Motywów z problemami: {len(themes_with_issues)}")
    print("-" * 72)
    for theme in themes_with_issues:
        for mode in ("dark", "light"):
            key = (theme, mode)
            if key not in by_theme:
                continue
            problems = by_theme[key]
            print(f"\n  {theme} ({mode}):")
            for reason, detail in problems:
                reason_pl = {
                    "accent_zlewa_sie_z_tlem": "Accent zlewa się z tłem",
                    "accent_prawie_czarny": "Accent prawie czarny",
                    "accent_prawie_bialy": "Accent prawie biały",
                    "dark_accent_ciemniejszy_od_bg": "Dark: accent ciemniejszy od tła",
                    "light_accent_wyprany": "Light: accent nadmiernie rozjaśniony",
                    "duza_korekta": "Bardzo duża korekta HSL",
                }.get(reason, reason)
                print(f"    - {reason_pl}: {detail}")

    print("\n" + "-" * 72)
    print("LISTA MOTYWÓW – accent nie współmierny do palety:")
    print("-" * 72)
    for t in themes_with_issues:
        print(f"  - {t}")


if __name__ == "__main__":
    main()
