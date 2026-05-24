# Wytyczne audytu motywów bubble_2026.yaml

## 1. Zakres – skąd, od kiedy

**Źródło:** Twoje oryginalne instrukcje:
> „w bubble_2026.yaml należy poddać audytowi wszystkie motywy dodane w e684ac2 commit do ostatniego”
> „Audyt (z wyjątkiem motywów przed commitem: e684ac2)”

### 1.1 Commit e684ac2
- **Hash:** `e684ac2` (Update bubble_2026.yaml)
- **Data:** 2026-02-21
- **Zmiana:** +24 030 linii w `themes/bubble_2026.yaml`

### 1.2 Motywy PRZED e684ac2 (wyłączone z audytu)

**Źródło:** `git show e684ac2^:themes/bubble_2026.yaml` – plik przed commitem e684ac2.

Te **26 motywów** nie są audytowane:

| # | Nazwa |
|---|-------|
| 1 | Bubble 2026 |
| 2 | Bubble 2026 BFG |
| 3 | Bubble Silas PEBKAC |
| 4 | Bubble IDKFA |
| 5 | Bubble Dubble |
| 6 | Bubble IDDQD |
| 7 | Bubble GRUVBOX |
| 8 | Bubble Nord |
| 9 | Bubble One Dark Pro |
| 10 | Bubble GitHub Dimmed |
| 11 | Bubble Ayu Mirage |
| 12 | Bubble Catppuccin Macchiato |
| 13 | Bubble Tokyo Night Storm |
| 14 | Bubble Palenight |
| 15 | Bubble Solarized Dark |
| 16 | Bubble Gruvbox Material |
| 17 | Bubble Kanagawa |
| 18 | Bubble Everforest |
| 19 | Bubble Rose Pine |
| 20 | Bubble Night Owl |
| 21 | Bubble Monokai Pro |
| 22 | Bubble Horizon |
| 23 | Bubble Dracula |
| 24 | Bubble Cyberpunk |
| 25 | Bubble Latte |
| 26 | Bubble Matrix |

### 1.3 Motywy OD e684ac2 (objęte audytem)

Wszystkie pozostałe motywy – dodane w e684ac2 lub później. Szacunkowo ok. 180 motywów bazowych, m.in.:

- Dubble Dracula, Dubble Nord, Dubble One Dark Pro, …
- Bubble Gruvbox, Dubble Gruvbox
- Bubble Shades of Purple, Dubble Shades of Purple
- Bubble Cobalt2, Dubble Cobalt2
- … (aż do Bubble Zenburn, Dubble Zenburn)

---

## 2. Zasady audytu (dla motywów OD e684ac2)

### 2.1 Day/Night w jednym motywie
- Motywy muszą mieć `modes: dark:` i `modes: light:` w jednym bloku.
- **Błąd:** oddzielne motywy typu „Bubble X Dark” i „Bubble X Light”.
- **Działanie:** połączyć w jeden motyw z `modes: { dark: {...}, light: {...} }`.
- Przy scalaniu: sprawdzić palety w oficjalnych motywach VS Code (Rose Pine, Nord, Catppuccin itd.).

### 2.2 bubble-accent-color i bubble-button-accent-color
- Zasadniczo: `var(--token-accent)`.
- Jeśli kontrast jest za słaby → regulacja HSL.

### 2.3 Kontrast primary-text-color na tle accent
- Tekst ma być czytelny na tle `--bubble-accent-color`.
- **Motywy jasne (light):** ciemny tekst na ciemnym accent → rozjaśnić accent, np. `hsl(from var(--token-accent) h s calc(l + 15))`.
- **Motywy ciemne (dark):** jasny tekst na jasnym accent → przyciemnić accent, np. `hsl(from var(--token-accent) h calc(s - 15) calc(l - 20))`.

### 2.4 Nazewnictwo wariantów
- Zamiast `-dev` stosować:
  - **_w_header** – header widoczny (card-mod nie chowa headera)
  - **_w_viewbar** – header na dole, viewbar layout

---

## 3. Narzędzia do przygotowania

| Narzędzie | Opis | Status |
|-----------|------|--------|
| `list_themes_for_audit.py` | Listuje motywy OD e684ac2 (do audytu) vs PRZED (pominięte) | Gotowe |
| `audit_bubble_accent.py` | Sprawdza bubble-accent/button-accent w motywach audytowanych | Gotowe |
| `audit_accent_palette.py` | Sprawdza czy accent mieści się w palecie motywu (zlewa się, skrajności) | Gotowe |
| `apply_hsl_fix.py` | Nakłada korekty HSL na wybrane motywy | Do utworzenia (opcjonalnie) |
| `add_dev_themes.py` | Generuje _w_header i _w_viewbar | Istnieje |
| `remove_dev_themes.py` | Usuwa warianty | Istnieje |

---

## 4. Plan działania

1. **Przygotować skrypt** – `list_themes_for_audit.py`, który:
   - odczytuje listę motywów sprzed e684ac2 (np. z pliku/stalej listy),
   - czyta aktualny `bubble_2026.yaml`,
   - wypisuje motywy DO audytu i POMINIĘTE.
2. **Weryfikacja** – ręcznie lub skryptem sprawdzić bubble-accent w motywach audytowanych.
3. **Korekty HSL** – na podstawie testów w HA nanieść regulacje dla motywów z słabym kontrastem.
4. **Uruchomić** `add_dev_themes.py` – po zatwierdzeniu zmian.

---

## 5. Uruchomienie narzędzi

```powershell
cd c:\cards_development\bubble_theme_2026
$yaml = "c:\cards_development\Bubble_Theme_2026_repo\themes\bubble_2026.yaml"

# Lista motywów do audytu vs pominiętych
python list_themes_for_audit.py $yaml

# Weryfikacja bubble-accent-color / bubble-button-accent-color
python audit_bubble_accent.py $yaml
```

## 6. Kontrast WCAG 4.5:1 (zrealizowane)

**Źródło:** WCAG 2.1 Success Criterion 1.4.3 (Contrast Minimum)  
- Mały tekst: **≥ 4.5:1** (AA)  
- Wzór: `(L1 + 0.05) / (L2 + 0.05)` gdzie L = relative luminance (sRGB)

**Narzędzia:**
- `contrast_utils.py` – obliczenia luminance, contrast ratio, delta HSL
- `apply_contrast_fixes.py` – audyt + automatyczne korekty

**Wykonane:** 269 trybów (dark/light) w motywach od e684ac2 skorygowano HSL, aby spełnić 4.5:1.

## 7. Potwierdzenie przed wykonaniem

1. Lista 26 motywów wyłączonych z audytu – potwierdzona  
2. ~262 motywy bazowe objęte audytem – potwierdzone  
3. Korekty HSL zastosowane – zrealizowane
