# Audyt motywów bubble_2026.yaml

**Data:** 2025-03-01  
**Zakres:** Motywy dodane od commitu e684ac2 do HEAD  
**Źródło:** Bubble_Theme_2026_repo (po `git pull`)

---

## 1. Wykonane działania

### 1.1 Cofnięcie i aktualizacja
- Cofnięto wcześniejsze zmiany
- `git pull` w Bubble_Theme_2026_repo – pobrano najnowszą wersję (commit 97220a9)
- Plik `themes/bubble_2026.yaml` ma ~26 000 linii, ~200+ motywów

### 1.2 bubble-accent-color i bubble-button-accent-color
**Wykonane:** We wszystkich motywach ustawiono:
```yaml
bubble-accent-color: var(--token-accent)
bubble-button-accent-color: var(--token-accent)
```
Zastąpiono 592 pary (1184 linie) wariantów HSL.

### 1.3 Nazewnictwo: dev-Theme → Header
**Wykonane:** Zaktualizowano skrypty w `bubble_theme_2026/`:
- **add_dev_themes.py** – generuje warianty `"Name Header:"` zamiast `"Name dev-Theme:"`, pomija bloki będące już wariantami Header/dev-Theme
- **remove_dev_themes.py** – usuwa bloki `"Name dev-Theme:"` oraz `"Name Header:"`

---

## 2. Day/Night – konsolidacja

**Stan:** Motywy w repo mają `modes: dark:` i `modes: light:` w jednym bloku – **brak rozdzielonych wariantów**.

Jeśli w przyszłości pojawią się oddzielne motywy typu "Bubble X Dark" i "Bubble X Light":
1. Zidentyfikować pary
2. Połączyć w jeden motyw z `modes: { dark: {...}, light: {...} }`
3. Przy scalaniu palety – odnieść się do oficjalnych motywów VS Code:
   - **Rose Pine:** [rosepinetheme.com/palette](https://rosepinetheme.com/palette)
   - **Nord:** #88C0D0 (accent), #2E3440 (bg)
   - **Catppuccin:** Mocha/Latte/Macchiato
   - **Dracula:** #bd93f9
   - **Gruvbox:** #fe8019 (dark), #af3a03 (light)
   - **Tokyo Night:** #7aa2f7, #24283b

---

## 3. Plan regulacji HSL (gdy kontrast za słaby)

Po ustawieniu `var(--token-accent)` należy przetestować każdy motyw.  
Jeśli `primary-text-color` lub `token-text-on-accent` jest nieczytelny na tle accent:

### Motywy ciemne (jasny accent, np. Rose Pine #ebbcba)
- **Obniżyć L:** `hsl(from var(--token-accent) h s calc(l - 15))`
- **Zwiększyć S:** `hsl(from var(--token-accent) h calc(s + 10) l)`
- Przykład Rose Pine dark: `hsl(from var(--token-accent) h calc(s + 5) calc(l - 20))`

### Motywy jasne (ciemny accent)
- **Zwiększyć L:** `hsl(from var(--token-accent) h s calc(l + 10))`
- **Zmniejszyć S:** `hsl(from var(--token-accent) h calc(s - 10) l)`

**Motyw problematyczny (przykład):** Bubble Rose Pine – `hsl(s-50 l-30)` dawał niemal biały kolor i słaby kontrast. Domyślnie używamy `var(--token-accent)`; w razie potrzeby dostosować HSL tylko dla `bubble-accent-color` i `bubble-button-accent-color`.

**Wykonane korekty (2025-03-01):**
- **WCAG 4.5:1** – automatyczne korekty HSL dla 269 trybów w motywach od e684ac2
- Algorytm: względna luminance (sRGB), contrast ratio, minimalna delta L w HSL
- `apply_contrast_fixes.py` – narzędzie audytu i aplikacji

---

## 4. Bubble Cards – mod do automatycznej podmiany koloru fontu

### 4.1 Obecny mechanizm (Bubble Theme – card-mod)
W `x-bubble-shared` (card-mod-card):
```yaml
.bubble-button-card-container[style*="background-color"],
.bubble-sub-button[style*="background-color"] {
  --primary-text-color: var(--token-text-on-accent) !important;
  --bubble-icon-color: var(--token-text-on-accent) !important;
  ...
}
```
Gdy element ma inline `style*="background-color"` → używany jest `token-text-on-accent`.

### 4.2 System modułów Bubble Cards
- **Module Store** – moduły przez `bubble-modules.yaml` lub interfejs
- **Bubble Card Tools** – integracja dla Module Store
- Moduły pozwalają na CSS, szablony, opcje w edytorze

### 4.3 Możliwość modu dla kontrastu
**Opcje:**
1. **Card-mod (motyw)** – już stosuje `token-text-on-accent` przy tle accent; kluczowe jest poprawne ustawienie `token-text-on-accent` i `bubble-accent-color` w motywach.
2. **Moduł Bubble Cards** – mógłby dodać CSS sprawdzający tło i ustawiający kolor tekstu (np. przez `@supports` lub skrypt), ale wymagałoby to dostępu do kalkulacji kontrastu w JS – nie jest to standardowa funkcja modułów.
3. **Prostsza ścieżka** – regulacja `bubble-accent-color` i `token-text-on-accent` w motywach tak, aby kontrast był zawsze poprawny. Obecny card-mod powinien wystarczyć.

**Uwaga:** Selektor `[style*="background-color"]` może nie obejmować wszystkich przypadków. Rozszerzono selektory o `.background-on`, `[style*="bubble-accent-color"]`, `[style*="bubble-sub-button-light-background-color"]`.

### 4.4 Header / Toolbar – wyłączenie
W `card-mod-root-yaml`:
```yaml
@media only screen and (max-width: 768px) {
  .header { display: none; opacity: 0; }
  #view { padding-top: 0 !important; margin-top: 0 !important; ... }
}
```
- `.header` = główny pasek narzędzi Home Assistant (górny)
- Na viewport ≤768px (mobile) – header jest ukrywany (`display: none`)
- `#view` dostosowuje padding/margin, gdy header jest ukryty

---

## 5. Warianty _w_header i _w_viewbar

- **_w_header**: Header widoczny (card-mod nie chowa headera na mobile)
- **_w_viewbar**: Header na dole, toolbar, viewbar layout (graph card, entities, bottom tabbar)

Anchory: `x-bubble-w-header-mod`, `x-bubble-w-viewbar-mod`  
Skrypt `add_dev_themes.py` generuje dla każdego motywu dwa warianty.

---

## 6. Kolejne kroki

| # | Zadanie | Status |
|---|---------|--------|
| 1 | Ustawienie bubble-accent = token-accent | ✅ Wykonane |
| 2 | Skrypty dev→Header | ✅ Wykonane |
| 3 | Test kontrastu w HA (szczególnie Rose Pine, Catppuccin, One Dark Pro) | Do wykonania |
| 4 | Regulacja HSL dla motywów z słabym kontrastem | Po kroku 3 |
| 5 | Sync bubble_theme_2026 z repo i uruchomienie add_dev_themes | Opcjonalnie |

---

## 7. Użycie skryptów (bubble_theme_2026)

```bash
# 1. Skopiuj themes/bubble_2026.yaml z Bubble_Theme_2026_repo
# 2. Usuń stare warianty:
python remove_dev_themes.py

# 3. Dodaj warianty _w_header i _w_viewbar:
python add_dev_themes.py
```
