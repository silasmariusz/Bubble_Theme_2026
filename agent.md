# Bubble Theme 2026 — Agent Reference

AI agent knowledge base for the `silasmariusz/Bubble_Theme_2026` repository.
Reference this document when working on theme development, debugging, or new features.

---

## Project Overview

**Type:** Home Assistant (HA) HACS Theme Pack  
**Entry point:** `themes/bubble_2026.yaml` (HACS key: `"filename"`)  
**Theme count:** 289 variants (dark + light mode each)  
**Min HA version:** 2024.2.0  
**Dependencies:** `card-mod` (HACS custom component — required for shadow DOM CSS injection)  
**Designed for:** [`Bubble Card`](https://github.com/Clooos/Bubble-Card) addon

### File Map

```
themes/bubble_2026.yaml          ← Single theme file (HACS entry, ~23k lines)
scripts/generate_preview.py      ← Preview HTML + contrast validator
docs/theme-preview.html          ← Generated visual preview (commit when updated)
www/
  bubble_2026_bfg_background.png
  bubble_2026_bfg_background-light.png
  hui-view-settings.js           ← Column padding override (optional helper)
  popup-background.js            ← Backdrop filter (optional helper)
```

---

## Theme YAML Architecture

### Anchor System (YAML merge keys)

The file uses YAML anchors (`&name`) and merge keys (`<<: *name`) for DRY code.
Do NOT restructure these anchors without testing all 289 themes.

```
x-bubble-shared: &bubble_shared
  └─ card-mod-root-yaml    (mobile: hide header, viewport fix)
  └─ card-mod-more-info-yaml (dialog: blur backdrop, round corners)
  └─ card-mod-view-yaml    (sidebar subview mode)
  └─ card-mod-card         (ha-card CSS: transition, accent fix, text-on-accent)
  └─ card-mod-card-yaml    (shadow DOM CSS injections for .background-on etc.)

x-bubble-colors-base-no-rgb: &bubble_colors_base_no_rgb
  └─ fonts, font weights, font sizes
  └─ all HA standard variable mappings (primary-color, text-color, etc.)
  └─ Mushroom card rgb mappings (mush-rgb-*)

x-bubble-colors-dark: &bubble_colors_dark
  └─ <<: *bubble_colors_base_no_rgb
  └─ bubble-border
  └─ default dark-mode token-rgb-* palette (all 19 colors except semantic 4)

x-bubble-colors-dark-no-rgb: &bubble_colors_dark_no_rgb
  └─ <<: *bubble_colors_base_no_rgb
  └─ bubble-border
  └─ (NO rgb palette — for themes with fully custom token-rgb-* values)

x-bubble-colors-light-base: &bubble_colors_light_base
  └─ <<: *bubble_colors_base_no_rgb
  └─ bubble-border (dark border for light backgrounds)
  └─ (NO rgb palette)

x-bubble-colors-light: &bubble_colors_light
  └─ <<: *bubble_colors_light_base
  └─ light-mode token-rgb-* palette (HA defaults for light backgrounds)
```

### Per-Theme Structure

```yaml
Theme Name:
  card-mod-theme: Theme Name    ← required, must match key exactly
  <<: *bubble_shared            ← injects card-mod CSS
  modes:
    dark:
      token-accent: "rgb(80, 110, 172)"
      token-rgb-primary: 80, 110, 172
      token-text-on-accent: "#ffffff"
      token-bg: "rgba(57, 54, 70, 1)"
      token-bg-secondary: "rgb(92, 83, 103)"
      token-card: "rgba(79, 69, 87, 1)"
      token-text: "#ffffff"
      token-text-secondary: "#b0b0b0"
      token-sidebar-icon: "#98a7b9"
      token-success: "rgba(0, 202, 139, 1)"
      token-rgb-green: 0, 202, 139
      token-warning: "rgba(222, 176, 107, 1)"
      token-rgb-yellow: 222, 176, 107
      token-error: "rgba(247, 53, 67, 1)"
      token-rgb-red: 247, 53, 67
      token-info: "rgba(26, 137, 245, 1)"
      token-rgb-blue: 26, 137, 245
      bubble-accent-color: var(--token-accent)
      bubble-button-accent-color: var(--token-accent)
      <<: *bubble_colors_dark    ← or *bubble_colors_dark_no_rgb for custom RGB palette
    light:
      # ... same structure with light-appropriate colors
      <<: *bubble_colors_light   ← or *bubble_colors_light_base for custom RGB palette
```

---

## Token Reference

### Semantic Color Tokens (required per theme/mode)

| Token | Purpose | Format | Dark example | Light example |
|-------|---------|--------|-------------|---------------|
| `token-accent` | Primary brand color | hex / rgb() / rgba() | `rgb(80,110,172)` | `#e69c9c` |
| `token-bg` | Page background | rgba() | `rgba(57,54,70,1)` | `#eff1f5` |
| `token-bg-secondary` | Secondary bg (panels) | rgb() | `rgb(92,83,103)` | `#ccd0da` |
| `token-card` | Card background | rgba() | `rgba(79,69,87,1)` | `#dce0e8` |
| `token-text` | Primary text | hex | `#ffffff` | `#4c4f69` |
| `token-text-secondary` | Secondary/hint text | hex | `#b0b0b0` | `#6c6f85` |
| `token-text-on-accent` | Text on THEME ACCENT bg (e.g. active card accent color) | hex | `#ffffff` | `#ffffff` |
| `token-state-on-text-color` | Text on entity STATE background (lights on = yellow/cyan). Always dark by default since state colors are always bright. Do NOT set to white. | rgba() | `rgba(0,0,0,0.85)` | `rgba(0,0,0,0.85)` |
| `token-sidebar-icon` | Sidebar icon color | hex | `#98a7b9` | `#8c8fa1` |
| `token-success` | Success state | rgba() | `rgba(0,202,139,1)` | `rgba(46,204,113,1)` |
| `token-warning` | Warning state | rgba() | `rgba(222,176,107,1)` | `rgba(245,166,35,1)` |
| `token-error` | Error state | rgba() | `rgba(247,53,67,1)` | `rgba(231,76,60,1)` |
| `token-info` | Info state | rgba() | `rgba(26,137,245,1)` | `rgba(0,122,255,1)` |

### RGB Tuple Tokens (required per theme/mode)

Bare `R, G, B` tuples — no wrapper. Used by Material Design and Mushroom cards.

| Token | Semantic meaning |
|-------|-----------------|
| `token-rgb-primary` | Must match `token-accent` color |
| `token-rgb-red` | Must match `token-error` color |
| `token-rgb-green` | Must match `token-success` color |
| `token-rgb-yellow` | Must match `token-warning` color |
| `token-rgb-blue` | Must match `token-info` color |

All other `token-rgb-*` are palette colors (non-semantic). Use `<<: *bubble_colors_dark`
to inherit defaults, or override individually. See the anchor definitions in the YAML
header (lines 316-379) for all 19 palette entries.

### Typography Tokens (inherited via anchor, do not redefine per theme)

```
token-weight-font-body: 400
token-weight-font-title: 600
token-size-font-xs … token-size-font-5xl  (calc(Npx * var(--ha-font-size-scale)))
```

---

## Color Formats

| Format | Example | Used for |
|--------|---------|---------|
| Hex | `"#ffffff"` | Simple colors |
| RGB | `"rgb(80, 110, 172)"` | When alpha not needed |
| RGBA | `"rgba(57, 54, 70, 1)"` | Preferred for bg/card (allows overlay math) |
| HSL | `"hsl(from var(--token-accent) h s calc(l - 8))"` | Relative lightness variants |
| RGB tuple | `80, 110, 172` | `token-rgb-*` only — no wrapper! |
| CSS var | `"var(--token-accent)"` | Cross-token references |

---

## HA Standard Variable Mappings

The `*bubble_colors_base_no_rgb` anchor maps our tokens to standard HA variables.
Do not duplicate these in per-theme blocks.

| HA variable | → our token |
|-------------|-------------|
| `primary-color` | `var(--token-accent)` |
| `accent-color` | `var(--token-accent)` |
| `primary-text-color` | `var(--token-text)` |
| `secondary-text-color` | `var(--token-text-secondary)` |
| `text-primary-color` | `var(--token-text-on-accent)` |
| `background-color` | `var(--token-bg)` |
| `primary-background-color` | `var(--token-bg)` |
| `secondary-background-color` | `var(--token-bg-secondary)` |
| `card-background-color` | `var(--token-card)` |
| `ha-card-background` | `var(--token-card)` |
| `sidebar-background-color` | `var(--token-bg)` |
| `sidebar-icon-color` | `var(--token-sidebar-icon)` |
| `sidebar-selected-icon-color` | `var(--token-accent)` |
| `switch-checked-button-color` | `var(--token-accent)` |
| `slider-color` | `var(--token-accent)` |
| `success-color` | `var(--token-success)` |
| `warning-color` | `var(--token-warning)` |
| `error-color` | `var(--token-error)` |
| `info-color` | `var(--token-info)` |
| `ha-card-border-radius` | `"28px"` (fixed) |
| `ha-card-box-shadow` | `"none"` (fixed) |
| `ha-card-border-width` | `"0px"` (fixed) |

---

## HA 2026.5 New Tokens (consider when updating)

Introduced in HA 2026.5. Our theme does not yet set these — they fall back to HA defaults.

```
--ha-color-surface-default    (default surface background)
--ha-color-surface-low        (lower elevation surface)
--ha-color-surface-inverted   (inverted surface)
--ha-box-shadow-s / -m / -l   (elevation shadows)
--ha-switch-size, --ha-switch-thumb-background-color, etc.
--ha-checkbox-size, --ha-checkbox-border-color, etc.
--ha-progress-bar-indicator-color, etc.
```

---

## Bubble Card Integration

### How Bubble Card Uses Theme Variables

1. **Button background (entity ON):**  
   `--bubble-button-accent-color` → `--bubble-accent-color` → `--bubble-default-color`  
   `--bubble-default-color` is computed at runtime as a blue+background blend.

2. **Contrast detection (JS):**  
   Bubble Card calls `calculateLuminance()` on `--primary-text-color` to determine text
   brightness, then multiplies the accent RGB by `0.84` (bright color) or `0.92` (dark).
   Source: `src/tools/utils.js:164-187`.

3. **Sub-button text contrast:**  
   Applies CSS class `.bright-background` when accent is detected as light.  
   That class sets: `color: var(--bubble-sub-button-dark-text-color, rgb(0,0,0))`.  
   Source: `src/components/sub-button/styles.css:287`.

4. **Main button text:** No automatic text-color swap. Text stays `--primary-text-color`.

### Shadow DOM Levels for card-mod CSS

```
card-mod-card: |              → injected at ha-card light DOM
  $: |                         → one shadow root deep (bubble-card's root)
    [selectors here]
card-mod-card-yaml: |
  "ha-card$": |               → one shadow root deep
    [selectors]
  "hui-element$ha-card$": |   → two shadow roots deep
    [selectors]
```

CSS custom properties inherit across shadow boundaries, but class-based selectors
(`.background-on`, `.bubble-name`, etc.) do NOT pierce shadow DOM.

---

## Accent Color Problem — Root Cause Analysis

### Problem

When a Bubble Card button's entity is ON, the card background becomes the accent color.
White text on a bright accent (cyan, lime, yellow) is often unreadable.

### Why Previous CSS Override Failed

1. `--bubble-text-on-accent` is **not** a native Bubble Card variable. It does not affect
   Bubble Card's internal text rendering. Bubble Card reads `--primary-text-color` instead.

2. Bubble Card's auto-darkening is only 8-16% — insufficient for bright accents.

### Current Fix (Option A — active on `dev` branch)

Located in `*bubble_shared` → `card-mod-card`:

```css
ha-card {
  --bubble-button-accent-color: color-mix(in srgb, var(--token-accent) 75%, black 25%);
  --bubble-accent-color: color-mix(in srgb, var(--token-accent) 75%, black 25%);
}
```

**Why it works:** CSS custom properties inherit across shadow DOM boundaries. Setting
`--bubble-button-accent-color` at `ha-card` scope overrides the document-root theme value.
Bubble Card then applies its own 8-16% darkening on top → ~30-35% total.

**Option B (on `dev-optionb` branch):** Per-theme mix via `token-accent-button-mix: "75%"`.
Lower value = darker button. Allows per-theme fine-tuning without touching the shared block.

---

## State Background Text Color Problem

### Problem (confirmed 2026-05-24)

When a Bubble Card sub-button has **both** checked:
- `[x] Show background when entity is on`
- `[x] Background color based on state`

...the background is set by Bubble Card JS to the entity's state color (e.g., warm yellow for
a lit lamp, cyan for a colored light). This is always a bright/vivid color. Text appeared
white (from `--primary-text-color`) = unreadable on bright backgrounds.

### Bubble Card Mechanism (from source code analysis)

1. JS function `updateBackground()` in `src/components/sub-button/utils.js`:
   - Adds `.background-on` class to the sub-button element
   - Calls `element.style.setProperty('--bubble-sub-button-light-background-color', color)`
     to set the background as a CSS custom property via inline style
   
2. The text color is NOT set directly by JS — it comes from CSS cascade:
   - `.background-on { background-color: var(--bubble-sub-button-light-background-color); }`
   - `.bright-background { color: var(--bubble-sub-button-dark-text-color, rgb(0,0,0)); }`

3. **The bug:** `.bright-background` class is **never added by JS** in current Bubble Card.
   The infrastructure exists but the luminance check triggering it is missing from
   `updateBackground()`. This is a Bubble Card bug, not ours.

4. Without `.bright-background`, text inherits from parent → `--primary-text-color` → WHITE
   in dark themes → white text on bright yellow background = unreadable.

### Why Our Previous CSS Fix Also Failed

The previous fix applied `color: var(--token-text-on-accent)` to `.bubble-sub-button.background-on`.

This is **semantically wrong**: `token-text-on-accent` is the text color for the THEME ACCENT
background (e.g., white for Nord's dark blue accent). Entity state backgrounds (lights on =
warm yellow, RGB cyan, etc.) are completely DIFFERENT colors — they are always bright and need
DARK text regardless of what the theme accent is.

Example: Bubble Nord has `token-text-on-accent: "#ffffff"` (white, correct for dark blue accent).
But when a light turns on with warm yellow state color, our CSS applied white text → still broken.

### Current Fix

Added `token-state-on-text-color: "rgba(0, 0, 0, 0.85)"` to `bubble_colors_base_no_rgb`.
This defaults to dark for ALL themes (entity state colors are always bright when "on").

Two separate rule groups in all card-mod injection paths (`$:`, `"ha-card$":`, `"hui-element$ha-card$":`):

```css
/* State/generic on-state → always dark */
.bubble-sub-button.background-on,
.bubble-sub-button[style*="bubble-sub-button-light-background-color"] {
  color: var(--token-state-on-text-color, rgba(0,0,0,0.85)) !important;
}

/* Theme accent background → theme-specific (comes AFTER .background-on rule, wins on overlap) */
.bubble-sub-button[style*="bubble-accent-color"] {
  color: var(--token-text-on-accent, rgba(0,0,0,0.85)) !important;
}
```

The accent rule is ordered AFTER the general `.background-on` rule (same CSS specificity →
source order wins), so it overrides for the accent-color-specific case.

### Per-Theme Override

If a specific theme has unusual entity state colors where dark text doesn't work, add:
```yaml
token-state-on-text-color: "rgba(255, 255, 255, 0.9)"
```
to that theme's dark or light mode block.

---

## Theme Creation Checklist

For each new theme, the `dark:` and `light:` mode blocks must define:

- [ ] `token-accent` (hex/rgb/rgba)
- [ ] `token-rgb-primary` (bare R,G,B tuple — must match accent)
- [ ] `token-text-on-accent` — **critical:** choose black (`#000000`) for bright accents
      (luminance > 0.5), white (`#ffffff`) for dark accents (luminance < 0.5)
- [ ] `token-bg`, `token-bg-secondary`, `token-card`
- [ ] `token-text`, `token-text-secondary`, `token-sidebar-icon`
- [ ] `token-success` + `token-rgb-green`
- [ ] `token-warning` + `token-rgb-yellow`
- [ ] `token-error` + `token-rgb-red`
- [ ] `token-info` + `token-rgb-blue`
- [ ] `bubble-accent-color: var(--token-accent)` (overridden by card-mod globally)
- [ ] `bubble-button-accent-color: var(--token-accent)` (overridden by card-mod globally)
- [ ] `<<: *bubble_colors_dark` (or `*bubble_colors_dark_no_rgb` if custom rgb palette)
- [ ] `card-mod-theme: Theme Name` at top level

### Choosing `token-text-on-accent`

Use this luminance rule:
- Accent luminance > 0.4 → use `"#000000"` (dark text)
- Accent luminance < 0.4 → use `"#ffffff"` (light text)

Python helper:
```python
import re, math

def lin(c):
    c /= 255
    return c/12.92 if c <= 0.04045 else ((c+0.055)/1.055)**2.4

def accent_luminance(hex_or_rgb):
    m = re.match(r'#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})', hex_or_rgb, re.I)
    if m:
        r,g,b = int(m.group(1),16),int(m.group(2),16),int(m.group(3),16)
    else:
        m = re.match(r'rgba?\((\d+),\s*(\d+),\s*(\d+)', hex_or_rgb)
        r,g,b = int(m.group(1)),int(m.group(2)),int(m.group(3))
    lum = 0.2126*lin(r)+0.7152*lin(g)+0.0722*lin(b)
    return lum, '#000000' if lum > 0.4 else '#ffffff'
```

---

## Architecture Decisions

### Single YAML vs Multiple Files

**Decision: one file (`bubble_2026.yaml`).**

HA loads ALL theme definitions from ALL configured YAML files at startup into memory.
Splitting into multiple files provides zero runtime performance benefit — all theme objects
live in memory regardless. One file is simpler for HACS installation.

HA themes do NOT support `!include` directives (unlike `configuration.yaml`), so there
is no native way to split and assemble. A generator script approach would be needed.

**If the theme library grows significantly:** Create `scripts/build_themes.py` that:
1. Reads `themes/base/shared.yaml` (anchors block)
2. Reads per-theme files from `themes/variants/*.yaml`
3. Assembles and writes `themes/bubble_2026.yaml`

Do not implement this unless the file becomes unmaintainable (~40k+ lines).

---

## Preview Generation

```bash
# Generate docs/theme-preview.html
python3 scripts/generate_preview.py

# Check only (exit 1 if broken themes found)
python3 scripts/generate_preview.py --check
```

The script:
- Parses `themes/bubble_2026.yaml` via PyYAML (anchors expanded automatically)
- Checks WCAG AA contrast (3:1) for text/bg and text-on-accent/accent pairs
- Generates self-contained HTML (no external dependencies)
- Flags broken themes with red border and issue list

**Re-run the generator whenever themes are added or modified, then commit `docs/theme-preview.html`.**

---

## Known Issues & Workarounds

| Issue | Status | Notes |
|-------|--------|-------|
| Bright accent → white text unreadable on button | Fixed (Option A) | `color-mix` in card-mod-card |
| State background text unreadable (lights on = yellow/cyan bg) | **Fixed** | Separate `token-state-on-text-color` token, dark by default |
| `.bright-background` class never added by Bubble Card JS | Documented | This is a Bubble Card bug; our CSS workaround targets `.background-on` instead |
| `--bubble-text-on-accent` not read by Bubble Card JS | Documented | Bubble Card uses `--primary-text-color` |
| `token-text-on-accent` was incorrectly used for state backgrounds | **Fixed** | These are different backgrounds; state needs its own token |
| Mobile header must be hidden via CSS, not HA API | By design | `display:none` at ≤768px breakpoint |
| All themes require card-mod (not just Dubble) | Documented | Fixed in README; without card-mod colors load but CSS enhancements don't |
