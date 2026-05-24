#!/usr/bin/env python3
"""
Sprawdza bubble-accent-color i bubble-button-accent-color w motywach do audytu.

Kryteria:
- Powinno być: var(--token-accent) lub hsl(from var(--token-accent) ...)
- Zgłasza motywy z innymi wartościami (hardcoded hex, rgb, błędny format)

Użycie:
  python audit_bubble_accent.py [ścieżka_do_bubble_2026.yaml]
"""

import re
import sys
from pathlib import Path

# Import listy motywów do audytu
from list_themes_for_audit import (
    THEMES_BEFORE_E684AC2,
    NON_THEME_KEYS,
    find_yaml_path,
    extract_themes,
)


def parse_theme_blocks(content: str, themes_info: list) -> dict[str, dict]:
    """
    Dla każdego motywu wyciąga fragment YAML (od nazwy do następnego top-level klucza).
    Zwraca {nazwa: {"content": str, "dark": {...}, "light": {...}, "line": int}}
    """
    lines = content.splitlines()
    result = {}

    for name, start_line in themes_info:
        block_lines = []
        i = start_line - 1  # 0-based
        indent = None

        while i < len(lines):
            line = lines[i]
            if i == start_line - 1:
                block_lines.append(line)
                i += 1
                continue
            # Następny top-level klucz: zaczyna się od litery, bez wcięcia
            if line and not line[0].isspace() and ":" in line:
                break
            block_lines.append(line)
            i += 1

        block_content = "\n".join(block_lines)
        result[name] = {"content": block_content, "line": start_line}

    return result


def _is_ok_value(v: str | None) -> bool:
    """Akceptowalne: var(--token-accent) lub hsl(from var(--token-accent) ...)"""
    if not v:
        return False
    v = v.strip().strip('"\'')
    if v == "var(--token-accent)":
        return True
    if "hsl(from var(--token-accent)" in v or "hsl(from var(--token-accent)" in v.replace(" ", ""):
        return True
    return False


def check_accent_in_block(block_content: str) -> dict:
    """
    Szuka bubble-accent-color i bubble-button-accent-color w bloku (dark + light).
    Wszystkie wystąpienia muszą być OK.
    """
    accs = re.findall(r"bubble-accent-color:\s*([^\n]+)", block_content)
    btns = re.findall(r"bubble-button-accent-color:\s*([^\n]+)", block_content)

    a_ok = bool(accs) and all(_is_ok_value(a) for a in accs)
    b_ok = bool(btns) and all(_is_ok_value(b) for b in btns)

    return {
        "bubble-accent-color": accs[0] if accs else None,
        "bubble-button-accent-color": btns[0] if btns else None,
        "accent_ok": a_ok,
        "button_ok": b_ok,
        "ok": a_ok and b_ok,
    }


def main():
    if len(sys.argv) > 1:
        yaml_path = Path(sys.argv[1])
    else:
        yaml_path = find_yaml_path()

    if not yaml_path.exists():
        print(f"Brak pliku: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    content = yaml_path.read_text(encoding="utf-8")
    themes_info = extract_themes(content)

    # Tylko motywy do audytu
    to_audit = [(n, ln) for n, ln in themes_info if n not in THEMES_BEFORE_E684AC2]
    blocks = parse_theme_blocks(content, to_audit)

    issues = []
    ok_count = 0

    for name, meta in blocks.items():
        r = check_accent_in_block(meta["content"])
        if r["ok"]:
            ok_count += 1
        else:
            issues.append((name, meta["line"], r))

    print("=" * 60)
    print("AUDYT: bubble-accent-color / bubble-button-accent-color")
    print("Zakres: motywy od commitu e684ac2")
    print("=" * 60)
    print()
    print(f"Sprawdzono: {len(to_audit)} bloków")
    print(f"OK: {ok_count}")
    print(f"Problemy: {len(issues)}")
    print()

    if issues:
        print("Motywy z problemami:")
        print("-" * 60)
        for name, line, r in issues:
            print(f"  [{line:5}] {name}")
            if not r["accent_ok"]:
                print(f"         bubble-accent-color: {r['bubble-accent-color']}")
            if not r["button_ok"]:
                print(f"         bubble-button-accent-color: {r['bubble-button-accent-color']}")
        print()


if __name__ == "__main__":
    main()
