#!/usr/bin/env python3
"""
Lista motywów do audytu vs pominiętych.

Zakres: motywy dodane OD commitu e684ac2.
Pominięte: motywy PRZED e684ac2 (26 motywów bazowych).

Użycie:
  python list_themes_for_audit.py [ścieżka_do_bubble_2026.yaml]
  
Domyślnie: themes/bubble_2026.yaml (względem Bubble_Theme_2026_repo)
           lub ../Bubble_Theme_2026_repo/themes/bubble_2026.yaml
"""

import re
import sys
from pathlib import Path

# Motywy sprzed e684ac2 (wyłączone z audytu) – z git show e684ac2^:themes/bubble_2026.yaml
THEMES_BEFORE_E684AC2 = frozenset([
    "Bubble 2026",
    "Bubble 2026 BFG",
    "Bubble Silas PEBKAC",
    "Bubble IDKFA",
    "Bubble Dubble",
    "Bubble IDDQD",
    "Bubble GRUVBOX",
    "Bubble Nord",
    "Bubble One Dark Pro",
    "Bubble GitHub Dimmed",
    "Bubble Ayu Mirage",
    "Bubble Catppuccin Macchiato",
    "Bubble Tokyo Night Storm",
    "Bubble Palenight",
    "Bubble Solarized Dark",
    "Bubble Gruvbox Material",
    "Bubble Kanagawa",
    "Bubble Everforest",
    "Bubble Rose Pine",
    "Bubble Night Owl",
    "Bubble Monokai Pro",
    "Bubble Horizon",
    "Bubble Dracula",
    "Bubble Cyberpunk",
    "Bubble Latte",
    "Bubble Matrix",
])

# Klucze YAML które NIE są motywami (anchory, shared)
NON_THEME_KEYS = frozenset([
    "x-bubble-shared", "x-bubble-w-header-mod", "x-bubble-w-viewbar-mod",
])


def find_yaml_path() -> Path:
    """Znajdź bubble_2026.yaml (repo lub lokalnie)."""
    candidates = [
        Path(__file__).resolve().parent.parent / "Bubble_Theme_2026_repo" / "themes" / "bubble_2026.yaml",
        Path(__file__).resolve().parent / "themes" / "bubble_2026.yaml",
        Path("themes/bubble_2026.yaml"),
        Path("bubble_2026.yaml"),
    ]
    for p in candidates:
        if p.exists():
            return p
    return candidates[0]  # domyślna ścieżka


def extract_themes(content: str) -> list[tuple[str, int]]:
    """
    Wyciąga nazwy motywów (klucze top-level) z YAML.
    Zwraca [(nazwa, linia), ...].
    """
    # Top-level klucze: "Nazwa motywu:" na początku linii (bez wcięcia)
    pattern = re.compile(r"^([A-Za-z][A-Za-z0-9 \-\_\(\)]+):\s*$")
    themes = []
    for i, line in enumerate(content.splitlines(), 1):
        m = pattern.match(line)
        if m:
            name = m.group(1).rstrip()
            if name not in NON_THEME_KEYS and not name.startswith("x-"):
                themes.append((name, i))
    return themes


def main():
    if len(sys.argv) > 1:
        yaml_path = Path(sys.argv[1])
    else:
        yaml_path = find_yaml_path()

    if not yaml_path.exists():
        print(f"Brak pliku: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    content = yaml_path.read_text(encoding="utf-8")
    themes = extract_themes(content)

    excluded = []
    to_audit = []
    for name, line in themes:
        if name in THEMES_BEFORE_E684AC2:
            excluded.append((name, line))
        else:
            to_audit.append((name, line))

    # Unikalne nazwy bazowe (bez duplikatów _w_header, _w_viewbar)
    def base_name(n: str) -> str:
        for suffix in (" Header", " Viewbar"):
            if n.endswith(suffix):
                return n[:-len(suffix)]
        return n

    audit_bases = sorted(set(base_name(n) for n, _ in to_audit))
    excluded_bases = sorted(THEMES_BEFORE_E684AC2)

    print("=" * 60)
    print("AUDYT MOTYWÓW bubble_2026.yaml")
    print("Commit graniczny: e684ac2 (motywy OD tego commitu = audyt)")
    print("=" * 60)
    print()
    print(f"POMINIĘTE (przed e684ac2): {len(excluded_bases)} motywów bazowych")
    print("-" * 40)
    for i, n in enumerate(excluded_bases, 1):
        print(f"  {i:3}. {n}")
    print()
    print(f"DO AUDYTU (od e684ac2): {len(audit_bases)} motywów bazowych")
    print("-" * 40)
    for i, n in enumerate(audit_bases, 1):
        print(f"  {i:3}. {n}")
    print()
    print(f"Łącznie w pliku: {len(themes)} bloków motywów")
    print(f"  - pominięte: {len(excluded)} bloków")
    print(f"  - do audytu: {len(to_audit)} bloków")
    print()


if __name__ == "__main__":
    main()
