# Audyt: bubble-accent-color vs paleta motywu

**Data:** 2025-03-01  
**Narzędzie:** `audit_accent_palette.py`

## Cel

Sprawdzenie, czy zmodyfikowany `bubble-accent-color` (korekty HSL dla WCAG 4.5:1) mieści się w palecie motywu – tzn. czy tła z accent nie wyglądają obco względem `token-bg`, `token-card`, `token-text`.

## Kryteria „nie współmierny”

| # | Kryterium | Opis |
|---|-----------|------|
| 1 | Zlewa się z tłem | Contrast accent/bg < 1.5:1 |
| 2 | Accent skrajny | Luminance < 0.04 (prawie czarny) lub > 0.96 (prawie biały) |
| 3 | Dark: accent ciemniejszy od bg | Accent nie wyróżnia się na tle |
| 4 | Light: accent nadmiernie rozjaśniony | Accent >> card przy ciemnym oryginale |
| 5 | Duża korekta | \|dL\| > 28 lub \|dS\| > 15 |

## Wynik audytu

**Sprawdzone:** 271 trybów (dark/light) z korektą HSL

### Motywy z problemami (accent nie współmierny do palety)

| Motyw | Tryb | Problem |
|-------|------|---------|
| **Bubble Monokai** | light | Accent zlewa się z tłem: contrast accent/bg = 1.43:1 (min 1.5) |

### Rekomendacja dla Bubble Monokai (light)

- **Kontekst:** `token-accent` #ade244 (lime), `token-bg` #f8f8f2 (jasne tło). Korekta `calc(l - 30)` dla kontrastu z białym tekstem daje accent o luminancji ~0.66, który słabo kontrastuje z tłem (1.43:1).
- **Opcje:**  
  1. Przyciemnić accent jeszcze bardziej – może pogorszyć czytelność tekstu na accent.  
  2. Rozważyć alternatywny odcień w palecie Monokai Light, który ma lepszy kontrast zarówno z tłem, jak i z białym tekstem.  
  3. Zaakceptować 1.43:1 – akcent nadal jest widoczny, choć mniej wyrazisty.

## Uruchomienie

```powershell
cd c:\cards_development\bubble_theme_2026
python audit_accent_palette.py "c:\cards_development\Bubble_Theme_2026_repo\themes\bubble_2026.yaml"
```
