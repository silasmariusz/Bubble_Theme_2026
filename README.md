# Bubble Theme 2026

A modern Home Assistant theme pack designed for [Bubble Card](https://github.com/Clooos/Bubble-Card), with 289 variants covering popular editor color schemes and custom vibes — each available in both dark and light mode.

> **Latest release:** [v0.666-ble1](https://github.com/silasmariusz/Bubble_Theme_2026/releases) — see [`CHANGELOG.md`](CHANGELOG.md) for details.

| Bubble 2026 | sample1 | sample2 |
| :---: | :---: | :---: |
| <img src="https://github.com/user-attachments/assets/6dea7d27-f6d8-49f3-9b16-c59e600cd899" height="400"> | <img src="https://github.com/user-attachments/assets/82f30b75-f39e-42b6-b822-b507eac29e23" height="400"> | <img src="https://github.com/user-attachments/assets/83857607-f988-4fc5-8506-b3862c992b6f" height="400"> |
| Sth | Bubble? | or Dubble? |
| <img src="https://github.com/user-attachments/assets/856d9a18-c79c-4caa-a4ff-4c60c2b713ba" height="400"> | <img src="https://github.com/user-attachments/assets/4564c1b6-0446-4788-98b4-5610a42442b1" height="400"> | <img src="https://github.com/user-attachments/assets/1c5e01c7-c078-4afc-9334-4a71ad6fae65" height="400"> |

**[→ Browse all 289 theme variants — dev preview](https://htmlpreview.github.io/?https://github.com/silasmariusz/Bubble_Theme_2026/blob/dev/docs/theme-preview.html)** · [stable / main](https://htmlpreview.github.io/?https://github.com/silasmariusz/Bubble_Theme_2026/blob/main/docs/theme-preview.html)

---

By Silas Mariusz · [devspark.pl](https://devspark.pl)  
Designed for the [QNAP Club Poland](https://forum.qnap.net.pl) community.  
Thanks to **UberDudePL** for recent fixes.  
Based on the original [Bubble theme](https://github.com/Clooos/Bubble) by Clooos and the [Noctis theme](https://github.com/aFFekopp/noctis) by aFFekopp.

Security issues: silas [at] qnapclub.pl

---

## Requirements

| Dependency | Required | Purpose |
|------------|----------|---------|
| [Bubble Card](https://github.com/Clooos/Bubble-Card) | Recommended | The cards these themes are designed for |
| [card-mod](https://github.com/thomasloven/lovelace-card-mod) | **Required for all themes** | Enables header hiding, dialog blur, and accent contrast fix |

> **card-mod must be installed for every theme variant** — both regular Bubble and Dubble.
> Without it the theme still loads and applies colors, but the CSS enhancements (mobile header,
> blurred dialogs, accent contrast fix) will not work.
>
> Install card-mod via HACS (Frontend category) before selecting any Bubble 2026 theme.

---

## Features

With [card-mod](https://github.com/thomasloven/lovelace-card-mod) installed you get:

- Header hidden on mobile (≤768 px) for a clean full-screen look
- Compact mobile-style layout on desktop when views are set to subview mode
- Blurred backdrop on more-info dialogs
- Automatic accent-color contrast fix — text on active Bubble Card buttons is always readable

---

## Theme file

| File | Description |
|------|-------------|
| `bubble_2026.yaml` | Main theme pack — 289 variants, header hidden on mobile |

HACS installs this file automatically. Select a theme variant in your profile settings.

---

## Installation

### With HACS (recommended)

HACS automatically tracks updates and notifies you when a new release is available.

1. Install HACS by following [https://hacs.xyz/docs/setup/download](https://hacs.xyz/docs/setup/download)
2. Complete the initial setup at [https://hacs.xyz/docs/configuration/basic](https://hacs.xyz/docs/configuration/basic)
3. In the Home Assistant sidebar, go to **HACS**
4. Click the **⋮** (three-dot) menu in the top-right corner, then **Custom repositories**
5. Enter `https://github.com/silasmariusz/Bubble_Theme_2026` as the repository URL
6. Set the category to **Theme** and click **Add**
7. Find **Bubble Theme 2026** in the list and click **Download**
8. Add the following to your `configuration.yaml` if it is not there already:
   ```yaml
   frontend:
     themes: !include_dir_merge_named themes
   ```
9. Save and restart Home Assistant
10. Go to your profile settings and select a **Bubble 2026** theme variant

#### Getting the latest development version

HACS tracks **tagged releases** only — branches are not listed in its version selector.
To install unreleased content from the `dev` branch you have two options:

**Option A — Manual install (simplest):**
1. Download the file directly from the `dev` branch:
   ```
   https://raw.githubusercontent.com/silasmariusz/Bubble_Theme_2026/dev/themes/bubble_2026.yaml
   ```
2. Place it in `<config>/themes/bubble_themes_2026/bubble_2026.yaml` and restart HA.

**Option B — Via HACS pre-release:**
1. In HACS, open **⋮ → Settings** and enable **Show pre-releases**
2. Return to the Bubble Theme 2026 entry; if a pre-release tag exists on `dev` it will
   now appear in the version dropdown — select it and click **Download**

> **Note:** Development versions may contain unfinished changes. Use a tagged release for
> stable production setups. Check the [releases page](https://github.com/silasmariusz/Bubble_Theme_2026/releases)
> to see which pre-release tags (e.g. `v0.666-dev1`) are currently available.

---

### Without HACS (manual)

1. Download the theme file directly:
   - **Latest stable release:** [bubble_2026.yaml](https://raw.githubusercontent.com/silasmariusz/Bubble_Theme_2026/main/themes/bubble_2026.yaml) (from `main`)
   - **Latest development build:** [bubble_2026.yaml](https://raw.githubusercontent.com/silasmariusz/Bubble_Theme_2026/dev/themes/bubble_2026.yaml) (from `dev`)
2. Place the file in `<config>/themes/bubble_themes_2026/bubble_2026.yaml`
   (create the folder if it does not exist)
3. Add the following to your `configuration.yaml` if it is not there already:
   ```yaml
   frontend:
     themes: !include_dir_merge_named themes
   ```
4. Save and restart Home Assistant
5. Go to your profile settings and select a **Bubble 2026** theme variant

---

## Theme Preview

Not sure which variant to pick? Browse them all before installing:

| Branch | Link | When to use |
|--------|------|-------------|
| `dev` | **[Open dev preview →](https://htmlpreview.github.io/?https://github.com/silasmariusz/Bubble_Theme_2026/blob/dev/docs/theme-preview.html)** | Latest unreleased changes |
| `main` | [Open stable preview →](https://htmlpreview.github.io/?https://github.com/silasmariusz/Bubble_Theme_2026/blob/main/docs/theme-preview.html) | Current released version |

The preview shows every theme variant with its dark and light mode side by side,
including a full color palette strip. You can filter by name or show only themes with
known contrast issues.

To regenerate the preview locally after editing the YAML:
```bash
python3 scripts/generate_preview.py
```

---

# FAQ

## Do I need card-mod? What does it do?

**Yes — card-mod is required for all Bubble 2026 themes**, including both Bubble and Dubble variants.

Without card-mod:
- The theme still loads and all colors are applied correctly
- But header hiding on mobile, blurred more-info dialogs, and the accent contrast fix **will not work**

Install [card-mod](https://github.com/thomasloven/lovelace-card-mod) via HACS (Frontend category),
then reload your themes (`Developer Tools → Actions → frontend.reload_themes`).

---

## I can't find the "Bubble 2026 Dubble" themes after installation

If Dubble variants are missing even after card-mod is installed, make sure you reloaded themes
and re-selected one from your profile settings. Dubble themes use additional card-mod CSS layers
for the dual-tone style — they will not appear if card-mod failed to load.

---

## How do I verify everything loaded correctly?

Run through this checklist after any installation or configuration change:

### In Home Assistant

1. Go to **Developer Tools** in the left sidebar
2. Check that your configuration has **no errors** (warnings are acceptable; errors must be
   fixed before continuing)
3. In Developer Tools → **Actions**, search for `frontend.reload_themes` and execute it
4. Go to your profile settings and re-select your theme

### In your browser

5. Press **F12** to open Developer Tools (make sure the Home Assistant tab is active)
6. Open the **Network** tab and check the **Disable cache** checkbox
7. Press **Ctrl+F5** (hard refresh)
8. Switch to the **Console** tab — if there are no red errors, everything is working

### On iOS / Android

1. Open the debug menu by swiping left/right if you have it enabled, or
2. Go to HA **Settings → Companion App** and clear the cache

> These steps should be performed after any change to your HA configuration. Home
> Assistant does not have a built-in "test and revert" mechanism, so a clean reload is
> the most reliable way to confirm changes took effect.

---

## Text on bright accent colors (Lime, Cyan, Yellow) is not readable

This was a known issue caused by how [Bubble Card](https://github.com/Clooos/Bubble-Card)
calculates button background brightness — it only darkened the accent color by 8–16%,
which was insufficient for light accent colors used with white text.

**Fixed** in the current build. The theme now pre-darkens the button accent background
by ~25% using CSS `color-mix()` before Bubble Card applies its own adjustment, giving
~30–35% total darkening. This makes white text readable on all accent colors including
cyan, lime, and yellow.

If you still experience a contrast issue with a specific theme variant, please
[open an issue](https://github.com/silasmariusz/Bubble_Theme_2026/issues).
