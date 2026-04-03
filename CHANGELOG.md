## Changelog

### v0.666-ble1 · 2026-04-03

- Pełna eliminacja ostrzeżeń o duplikatach kluczy YAML we wszystkich plikach motywów
- Restrukturyzacja kotwic YAML: nowy anchor `&bubble_colors_base_no_rgb` (bez `bubble-border` i `token-rgb-*`)
- `&bubble_colors_dark` dziedzicy z bazy i zawiera border + 19 niesemazycznych `token-rgb-*` (bez green/yellow/red/blue)
- Nowy anchor `&bubble_colors_dark_no_rgb` dla motywów z w pełni własną paletą RGB
- `&bubble_colors_light_base` dziedziczy z bazy (nie z dark) – eliminacja duplikatu `bubble-border`
- `&bubble_colors_light` zawiera 19 niesemazycznych `token-rgb-*` dla trybu jasnego
- Wszystkie motywy z niestandardową paletą (IDKFA, Dracula, Nord itp.) korzystają z `bubble_colors_dark_no_rgb`
- Usunięto zduplikowane wpisy Bubble Twilight Menubar / Dubble Twilight Menubar (menubar)
- Usunięto zduplikowane wpisy Bubble Twilight Header mod / Dubble Twilight Header mod (dev)
- Naprawiono duplikaty `dark:` / `light:` wewnątrz motywu Dubble Tron (bubble_2026.yaml)
- Wynik: 0 duplikatów w 294/294/293 motywach we wszystkich trzech plikach

### v0.666-ave7 · 2026-03-01

- Naprawa duplikatów YAML (ostrzeżenia HA)
- Usunięto duplikaty Bubble Twilight i Dubble Twilight
- Usunięto zbędny token-rgb-blue-grey z bubble_colors_light
- Usunięto redundantne token-rgb-* z bloków motywów (duplikaty z anchor merge)

### v0.666-ave6 · 2026-03-01

- **Nowe pliki motywów:**
  - `bubble_2026-dev.yaml` – 296 motywów **Header mod** (header widoczny na mobile)
  - `bubble_2026-menubar.yaml` – 296 motywów **Menubar** (header na dole, toolbar)
- Uproszczona struktura: jeden blok `shared` w każdym pliku (bez oddzielnych bloków header/viewbar)
- Usunięto `_w_header` i `_w_viewbar` z głównego pliku `bubble_2026.yaml`
- Aktualizacja README – opis plików dev i menubar

### v0.666-stable1 · 2026-02-11

- First stable cut of the 2026 Bubble theme pack.
- Matches the pre-release visuals from `v0.666-pre1`, but marked as stable for HACS default inclusion.
- Bundles helper assets (`www/`) and documentation refresh for official catalog submission.
