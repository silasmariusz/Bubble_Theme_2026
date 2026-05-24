#!/usr/bin/env python3
"""
Generate docs/theme-preview.html from themes/bubble_2026.yaml.

Usage:
    python3 scripts/generate_preview.py
    python3 scripts/generate_preview.py --check   # print broken themes only, exit 1 if any

Output:
    docs/theme-preview.html  — self-contained HTML with no external dependencies
    Exit code 1 if --check and broken themes found.
"""

import yaml
import re
import math
import sys
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Color utilities
# ---------------------------------------------------------------------------

def parse_color(value):
    """Return (r, g, b) int tuple from a CSS color string, or None if unparseable."""
    if not value or not isinstance(value, str):
        return None
    s = value.strip().strip('"\'')
    if 'var(' in s or 'calc(' in s or 'hsl(from' in s:
        return None

    # bare RGB tuple "r, g, b" (used for token-rgb-* values)
    if re.match(r'^\d+,\s*\d+,\s*\d+$', s):
        parts = [int(x.strip()) for x in s.split(',')]
        return tuple(parts)

    # hex
    if s.startswith('#'):
        h = s[1:]
        if len(h) == 3:
            h = ''.join(c * 2 for c in h)
        if len(h) == 6:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        if len(h) == 8:
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        return None

    # rgb() / rgba()
    m = re.match(r'rgba?\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)', s)
    if m:
        return (int(float(m.group(1))), int(float(m.group(2))), int(float(m.group(3))))

    # hsl() / hsla() — static only (no CSS calc inside)
    m = re.match(r'hsla?\(\s*(\d+(?:\.\d+)?)\s*,\s*(\d+(?:\.\d+)?)%\s*,\s*(\d+(?:\.\d+)?)%', s)
    if m:
        h_val = float(m.group(1)) / 360
        s_val = float(m.group(2)) / 100
        l_val = float(m.group(3)) / 100
        if s_val == 0:
            v = int(l_val * 255)
            return (v, v, v)
        def _hue(p, q, t):
            t %= 1
            if t < 1/6: return p + (q - p) * 6 * t
            if t < 1/2: return q
            if t < 2/3: return p + (q - p) * (2/3 - t) * 6
            return p
        q = l_val * (1 + s_val) if l_val < 0.5 else l_val + s_val - l_val * s_val
        p = 2 * l_val - q
        return (
            int(_hue(p, q, h_val + 1/3) * 255),
            int(_hue(p, q, h_val) * 255),
            int(_hue(p, q, h_val - 1/3) * 255),
        )

    return None


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(r, g, b):
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast_ratio(c1, c2):
    """WCAG contrast ratio between two (r,g,b) tuples."""
    if c1 is None or c2 is None:
        return None
    l1 = luminance(*c1) + 0.05
    l2 = luminance(*c2) + 0.05
    return round(max(l1, l2) / min(l1, l2), 2)


def rgb_to_css(rgb):
    if rgb is None:
        return '#888'
    return f'rgb({rgb[0]},{rgb[1]},{rgb[2]})'


def color_mix_black(rgb, pct_str):
    """Simulate color-mix(in srgb, color pct%, black 100-pct%).
    pct_str: '75%' or '75' or 0.75 — percent of the original color kept.
    """
    if rgb is None:
        return None
    try:
        s = str(pct_str).strip().strip('"\'').rstrip('%')
        pct = float(s) / 100.0
    except (ValueError, TypeError):
        pct = 0.75
    pct = max(0.0, min(1.0, pct))
    return (int(rgb[0] * pct), int(rgb[1] * pct), int(rgb[2] * pct))


def to_display_css(value):
    """Best-effort CSS value for display — resolve bare RGB tuples, pass others through."""
    if not value or not isinstance(value, str):
        return '#888'
    s = value.strip().strip('"\'')
    # bare RGB tuple → wrap
    if re.match(r'^\d+,\s*\d+,\s*\d+$', s):
        return f'rgb({s})'
    return s


# ---------------------------------------------------------------------------
# Theme extraction
# ---------------------------------------------------------------------------

REQUIRED_TOKENS = [
    'token-accent', 'token-bg', 'token-bg-secondary', 'token-card',
    'token-text', 'token-text-secondary', 'token-text-on-accent',
    'token-success', 'token-warning', 'token-error', 'token-info',
]

PALETTE_TOKENS = [
    'token-accent', 'token-bg', 'token-bg-secondary', 'token-card',
    'token-text', 'token-text-secondary', 'token-text-on-accent',
    'token-sidebar-icon',
    'token-success', 'token-warning', 'token-error', 'token-info',
    'token-rgb-red', 'token-rgb-green', 'token-rgb-yellow', 'token-rgb-blue',
    'token-rgb-purple', 'token-rgb-pink', 'token-rgb-cyan', 'token-rgb-teal',
    'token-rgb-orange', 'token-rgb-lime', 'token-rgb-amber', 'token-rgb-deep-purple',
    'token-rgb-indigo', 'token-rgb-light-blue', 'token-rgb-light-green',
    'token-rgb-deep-orange', 'token-rgb-brown', 'token-rgb-grey', 'token-rgb-blue-grey',
]


def extract_mode(mode_dict):
    """Pull only token-* values from a (potentially large merged) mode dict."""
    return {k: v for k, v in mode_dict.items() if k.startswith('token-')}


def check_theme_mode(tokens, mode_label, theme_name):
    """Return list of issue strings for a theme mode."""
    issues = []

    # Missing required tokens
    for tok in REQUIRED_TOKENS:
        if tok not in tokens or tokens[tok] is None:
            issues.append(f'missing {tok}')
            continue
        v = str(tokens[tok]).strip().strip('"\'')
        if 'var(' in v:
            issues.append(f'{tok} is an unresolved var() reference')

    # Contrast: text on background
    text_rgb = parse_color(str(tokens.get('token-text', '')))
    bg_rgb = parse_color(str(tokens.get('token-bg', '')))
    if text_rgb and bg_rgb:
        cr = contrast_ratio(text_rgb, bg_rgb)
        if cr is not None and cr < 3.0:
            issues.append(f'text/bg contrast {cr:.1f}:1 < 3:1 WCAG AA')

    # Contrast: text-on-accent on the simulated darkened button accent
    toa_rgb = parse_color(str(tokens.get('token-text-on-accent', '')))
    acc_rgb = parse_color(str(tokens.get('token-accent', '')))
    mix_pct = tokens.get('token-accent-button-mix', '75%')
    btn_rgb = color_mix_black(acc_rgb, mix_pct)
    check_rgb = btn_rgb if btn_rgb else acc_rgb
    if toa_rgb and check_rgb:
        cr = contrast_ratio(toa_rgb, check_rgb)
        if cr is not None and cr < 3.0:
            label = f'button ({mix_pct})' if btn_rgb else 'accent'
            issues.append(f'text-on-accent/{label} contrast {cr:.1f}:1 < 3:1 (button text unreadable even after darkening)')

    return issues


# ---------------------------------------------------------------------------
# HTML generation
# ---------------------------------------------------------------------------

def swatch(color_value, label, size=16):
    rgb = parse_color(str(color_value)) if color_value else None
    css = rgb_to_css(rgb) if rgb else '#555'
    lum = luminance(*rgb) if rgb else 0.5
    border = '1px solid rgba(255,255,255,0.15)' if lum < 0.1 else '1px solid rgba(0,0,0,0.15)'
    return (
        f'<div class="swatch" style="width:{size}px;height:{size}px;background:{css};'
        f'border:{border};display:inline-block;margin:1px;border-radius:3px;" '
        f'title="{label}: {color_value}"></div>'
    )


def mode_preview(tokens, issues, mode_name):
    def c(tok, fallback='#888'):
        v = tokens.get(tok)
        if not v:
            return fallback
        s = str(v).strip().strip('"\'')
        if 'var(' in s:
            return fallback
        if re.match(r'^\d+,\s*\d+,\s*\d+$', s):
            return f'rgb({s})'
        return s

    bg = c('token-bg', '#1a1a2e')
    card = c('token-card', '#16213e')
    bg2 = c('token-bg-secondary', '#0f3460')
    accent = c('token-accent', '#533483')
    text = c('token-text', '#eee')
    text2 = c('token-text-secondary', '#aaa')
    toa = c('token-text-on-accent', '#fff')
    success = c('token-success', '#2ecc71')
    warning = c('token-warning', '#f39c12')
    error = c('token-error', '#e74c3c')
    info = c('token-info', '#3498db')

    # Simulate the color-mix() button darkening
    mix_pct_raw = tokens.get('token-accent-button-mix', '75%')
    mix_pct_str = str(mix_pct_raw).strip().strip('"\'')
    acc_rgb = parse_color(str(tokens.get('token-accent', '')))
    btn_rgb = color_mix_black(acc_rgb, mix_pct_str)
    btn_accent = rgb_to_css(btn_rgb) if btn_rgb else accent
    # mix label shown only when token is explicitly set (Option B)
    has_mix_token = 'token-accent-button-mix' in tokens
    mix_label = f'<span class="mix-label" title="token-accent-button-mix">{mix_pct_str}</span>' if has_mix_token else ''

    broken_class = ' broken' if issues else ''
    issue_html = ''
    if issues:
        issue_list = ''.join(f'<li>{i}</li>' for i in issues)
        issue_html = f'<div class="issues"><strong>⚠ Issues:</strong><ul>{issue_list}</ul></div>'

    # Raw accent swatch + button swatch side by side for comparison
    acc_swatch = swatch(tokens.get('token-accent'), 'raw accent (token-accent)', size=14)
    btn_swatch_css = rgb_to_css(btn_rgb) if btn_rgb else None
    btn_swatch = (
        f'<div class="swatch" style="width:14px;height:14px;background:{btn_swatch_css};'
        f'border:1px solid rgba(0,0,0,0.2);display:inline-block;margin:1px;border-radius:3px;" '
        f'title="button accent after {mix_pct_str} mix"></div>'
    ) if btn_swatch_css else ''

    palette_html = ''.join(
        swatch(tokens.get(tok), tok)
        for tok in PALETTE_TOKENS
    )

    return f"""
<div class="mode-card{broken_class}">
  <div class="mode-label">{mode_name}</div>
  {issue_html}
  <div class="preview-strip" style="background:{bg};padding:10px;border-radius:8px;">
    <div class="card-block" style="background:{card};padding:10px;border-radius:6px;display:flex;flex-wrap:wrap;gap:8px;align-items:center;">
      <span style="color:{text};font-size:13px;font-weight:600;min-width:60px;">Label</span>
      <span style="color:{text2};font-size:11px;">Secondary</span>
      <button style="background:{bg2};color:{text};border:none;padding:5px 12px;border-radius:20px;font-size:12px;cursor:default;">Button</button>
      <span style="display:inline-flex;flex-direction:column;align-items:center;gap:2px;">
        <button style="background:{btn_accent};color:{toa};border:none;padding:5px 12px;border-radius:20px;font-size:12px;cursor:default;font-weight:600;">Active</button>
        <span style="display:flex;gap:2px;align-items:center;">{acc_swatch}{btn_swatch}{mix_label}</span>
      </span>
      <span style="background:{btn_accent};color:{toa};padding:3px 10px;border-radius:20px;font-size:11px;">Sub-pill</span>
      <span style="color:{success};font-size:12px;">✓ OK</span>
      <span style="color:{warning};font-size:12px;">⚠ Warn</span>
      <span style="color:{error};font-size:12px;">✗ Error</span>
      <span style="color:{info};font-size:12px;">ℹ Info</span>
    </div>
  </div>
  <div class="palette" style="margin-top:6px;line-height:1;">{palette_html}</div>
</div>"""


def generate_html(themes_data):
    theme_blocks = []

    for name, data in themes_data.items():
        if name.startswith('x-'):
            continue

        modes = data.get('modes', {})
        dark_raw = modes.get('dark', {})
        light_raw = modes.get('light', {})

        dark_tokens = extract_mode(dark_raw)
        light_tokens = extract_mode(light_raw)

        dark_issues = check_theme_mode(dark_tokens, 'dark', name)
        light_issues = check_theme_mode(light_tokens, 'light', name)

        has_issues = bool(dark_issues or light_issues)
        broken_class = ' theme-broken' if has_issues else ''

        dark_html = mode_preview(dark_tokens, dark_issues, 'Dark')
        light_html = mode_preview(light_tokens, light_issues, 'Light')

        theme_blocks.append(f"""
<div class="theme-block{broken_class}" id="{name.replace(' ', '-')}">
  <h2 class="theme-name">
    {'⚠ ' if has_issues else ''}{name}
    {'<span class="broken-badge">CONTRAST ISSUE</span>' if has_issues else ''}
  </h2>
  <div class="mode-row">
    {dark_html}
    {light_html}
  </div>
</div>""")

    theme_html = '\n'.join(theme_blocks)

    total = len([k for k in themes_data if not k.startswith('x-')])
    broken = sum(
        1 for name, data in themes_data.items()
        if not name.startswith('x-') and (
            check_theme_mode(extract_mode(data.get('modes', {}).get('dark', {})), 'dark', name) or
            check_theme_mode(extract_mode(data.get('modes', {}).get('light', {})), 'light', name)
        )
    )

    # Detect Option B by checking for token-accent-button-mix in any theme's base tokens
    all_keys = [k for k in themes_data if not k.startswith('x-')]
    has_optionb_token = any(
        'token-accent-button-mix' in {
            **themes_data[k].get('modes', {}).get('dark', {}),
            **themes_data[k].get('modes', {}).get('light', {}),
        }
        for k in all_keys
    )
    if has_optionb_token:
        variant_label = '<span class="variant-badge optionb" title="Per-theme mix % via token-accent-button-mix">Option B — per-theme mix</span>'
        variant_note = 'Active button shows simulated <code>color-mix()</code> darkening. Blue <code>75%</code> labels are per-theme mix values (Option B).'
    else:
        variant_label = '<span class="variant-badge optiona" title="Fixed 25% darkening via color-mix(accent 75%, black)">Option A — fixed 75% mix</span>'
        variant_note = 'Active button shows simulated <code>color-mix(accent 75%, black)</code> darkening (Option A fixed value).'

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bubble Theme 2026 — Preview</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #0d0d0d;
    color: #ddd;
    font-family: Inter, system-ui, sans-serif;
    font-size: 14px;
    padding: 20px;
  }}
  h1 {{ font-size: 24px; margin-bottom: 6px; color: #fff; }}
  .stats {{ color: #888; font-size: 13px; margin-bottom: 20px; }}
  .stats .broken-count {{ color: #e74c3c; font-weight: 600; }}
  .filter-bar {{
    position: sticky; top: 0; background: #0d0d0d; padding: 8px 0 12px;
    z-index: 10; display: flex; gap: 10px; align-items: center;
    border-bottom: 1px solid #222; margin-bottom: 16px;
  }}
  .filter-bar input {{
    background: #1a1a1a; border: 1px solid #333; color: #ddd;
    padding: 6px 12px; border-radius: 20px; font-size: 13px;
    width: 260px; outline: none;
  }}
  .filter-bar label {{ font-size: 13px; color: #aaa; cursor: pointer; }}
  .filter-bar input[type=checkbox] {{ width: auto; margin-right: 4px; }}

  .theme-block {{
    border: 1px solid #222;
    border-radius: 10px;
    padding: 14px;
    margin-bottom: 14px;
    background: #111;
  }}
  .theme-block.theme-broken {{ border-color: rgba(231,76,60,0.4); background: #130d0d; }}
  .theme-name {{
    font-size: 15px;
    font-weight: 600;
    color: #eee;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }}
  .broken-badge {{
    background: #c0392b;
    color: #fff;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 20px;
    font-weight: 700;
    letter-spacing: 0.5px;
  }}
  .mode-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
  }}
  @media (max-width: 700px) {{ .mode-row {{ grid-template-columns: 1fr; }} }}
  .mode-card {{
    border: 1px solid #1e1e1e;
    border-radius: 8px;
    padding: 8px;
    background: #0a0a0a;
  }}
  .mode-card.broken {{ border-color: rgba(231,76,60,0.5); }}
  .mode-label {{
    font-size: 11px;
    color: #666;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 6px;
  }}
  .issues {{
    background: rgba(231,76,60,0.08);
    border: 1px solid rgba(231,76,60,0.3);
    border-radius: 6px;
    padding: 6px 10px;
    margin-bottom: 8px;
    font-size: 11px;
    color: #e74c3c;
  }}
  .issues ul {{ padding-left: 16px; margin-top: 4px; }}
  .palette {{ padding: 2px 0; }}
  .swatch {{ cursor: help; }}
  .hidden {{ display: none !important; }}
  .mix-label {{
    font-size: 9px; color: #7ecbff; background: rgba(126,203,255,0.12);
    border-radius: 3px; padding: 0 3px; font-family: monospace; cursor: help;
  }}
  .variant-badge {{
    display: inline-block; font-size: 11px; font-weight: 700;
    padding: 2px 10px; border-radius: 20px; margin-left: 10px;
    vertical-align: middle;
  }}
  .variant-badge.optionb {{ background: #7ecbff22; color: #7ecbff; border: 1px solid #7ecbff55; }}
  .variant-badge.optiona {{ background: #a3e63522; color: #a3e635; border: 1px solid #a3e63555; }}
</style>
</head>
<body>
<h1>Bubble Theme 2026 — Theme Preview {variant_label}</h1>
<div class="stats">
  {total} theme variants &nbsp;|&nbsp;
  <span class="broken-count">{broken} with contrast issues</span>
  &nbsp;|&nbsp; Generated from <code>themes/bubble_2026.yaml</code>
  <br><span style="color:#888;font-size:12px;">{variant_note}</span>
</div>
<div class="filter-bar">
  <input type="text" id="search" placeholder="Filter by name…" oninput="filterThemes()">
  <label><input type="checkbox" id="brokenOnly" onchange="filterThemes()"> Show broken only</label>
  <label><input type="checkbox" id="hideOk" onchange="filterThemes()"> Hide passing themes</label>
</div>
{theme_html}
<script>
function filterThemes() {{
  const q = document.getElementById('search').value.toLowerCase();
  const brokenOnly = document.getElementById('brokenOnly').checked;
  const hideOk = document.getElementById('hideOk').checked;
  document.querySelectorAll('.theme-block').forEach(el => {{
    const name = el.querySelector('.theme-name').textContent.toLowerCase();
    const isBroken = el.classList.contains('theme-broken');
    const matchSearch = !q || name.includes(q);
    const matchFilter = (!brokenOnly && !hideOk) ||
                        (brokenOnly && isBroken) ||
                        (hideOk && isBroken);
    el.classList.toggle('hidden', !matchSearch || !matchFilter);
  }});
}}
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    check_mode = '--check' in sys.argv

    repo_root = Path(__file__).parent.parent
    yaml_path = repo_root / 'themes' / 'bubble_2026.yaml'
    out_path = repo_root / 'docs' / 'theme-preview.html'

    print(f'Loading {yaml_path}…')
    with open(yaml_path, encoding='utf-8') as f:
        data = yaml.safe_load(f)

    themes = {k: v for k, v in data.items() if not k.startswith('x-')}
    print(f'Found {len(themes)} theme variants')

    # Collect broken themes for report
    broken = []
    for name, theme_data in themes.items():
        modes = theme_data.get('modes', {})
        dark_issues = check_theme_mode(extract_mode(modes.get('dark', {})), 'dark', name)
        light_issues = check_theme_mode(extract_mode(modes.get('light', {})), 'light', name)
        if dark_issues or light_issues:
            broken.append((name, dark_issues, light_issues))

    print(f'Themes with issues: {len(broken)}')
    for name, di, li in broken:
        print(f'  [ISSUE] {name}')
        for issue in di:
            print(f'    dark:  {issue}')
        for issue in li:
            print(f'    light: {issue}')

    if check_mode:
        if broken:
            print(f'\n{len(broken)} themes have contrast or structural issues.')
            sys.exit(1)
        else:
            print('All themes pass checks.')
            sys.exit(0)

    print(f'Generating {out_path}…')
    html = generate_html(data)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'Done! {len(html):,} bytes written to {out_path}')


if __name__ == '__main__':
    main()
