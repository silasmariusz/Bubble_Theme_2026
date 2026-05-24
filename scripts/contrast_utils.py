"""
WCAG 2.1 contrast calculation and HSL adjustment for accessibility.

Target: 4.5:1 minimum for normal/small text (WCAG AA).
Source: https://www.w3.org/WAI/GL/wiki/Relative_luminance
        https://www.w3.org/WAI/GL/wiki/Contrast_ratio
"""

import colorsys
import re
from typing import Tuple

# WCAG AA minimum for normal text
MIN_CONTRAST_RATIO = 4.5


def hex_to_rgb(hex_str: str) -> Tuple[float, float, float]:
    """Convert #RRGGBB or #RGB to normalized RGB (0-1)."""
    hex_str = hex_str.strip().lstrip("#")
    if len(hex_str) == 3:
        hex_str = "".join(c * 2 for c in hex_str)
    if len(hex_str) != 6:
        raise ValueError(f"Invalid hex: {hex_str}")
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0
    return (r, g, b)


def rgb_to_relative_luminance(r: float, g: float, b: float) -> float:
    """WCAG relative luminance (0-1) for sRGB."""
    def linearize(c: float) -> float:
        if c <= 0.04045:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

    r, g, b = linearize(r), linearize(g), linearize(b)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(lum1: float, lum2: float) -> float:
    """WCAG contrast ratio. L1 = lighter, L2 = darker."""
    lighter = max(lum1, lum2)
    darker = min(lum1, lum2)
    return (lighter + 0.05) / (darker + 0.05)


def rgb_to_hsl(r: float, g: float, b: float) -> Tuple[float, float, float]:
    """Convert RGB (0-1) to HSL. H in 0-360, S and L in 0-100."""
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = h * 360 if h >= 0 else (h + 1) * 360
    return (h, s * 100, l * 100)


def hsl_to_rgb(h: float, s: float, l: float) -> Tuple[float, float, float]:
    """Convert HSL (H 0-360, S L 0-100) to RGB (0-1)."""
    h = h / 360.0
    s = s / 100.0
    l = l / 100.0
    return colorsys.hls_to_rgb(h, l, s)


def parse_color(val: str) -> Tuple[float, float, float] | None:
    """Parse hex, rgb(), rgba() from YAML value. Returns RGB (0-1) or None."""
    if not val:
        return None
    val = val.strip().strip('"\'')
    # Hex
    m = re.match(r"#([0-9a-fA-F]{3,8})$", val)
    if m:
        hex_str = m.group(1)
        if len(hex_str) in (3, 6):
            return hex_to_rgb("#" + hex_str)
    # rgb(r, g, b) or rgba(r, g, b, a)
    m = re.match(r"rgba?\s*\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*[\d.]+)?\s*\)", val)
    if m:
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return (r / 255.0, g / 255.0, b / 255.0)
    return None


def find_accent_hsl_delta(
    text_hex: str,
    accent_hex: str,
    min_ratio: float = MIN_CONTRAST_RATIO,
) -> Tuple[float, float, float] | None:
    """
    Find HSL delta (dH, dS, dL) for accent to achieve min_ratio with text.
    Returns (0, 0, dL) - we only adjust lightness for minimal change.
    Returns None if already meets contrast.
    """
    text_rgb = parse_color(text_hex)
    accent_rgb = parse_color(accent_hex)
    if not text_rgb or not accent_rgb:
        return None

    text_lum = rgb_to_relative_luminance(*text_rgb)
    accent_lum = rgb_to_relative_luminance(*accent_rgb)
    ratio = contrast_ratio(text_lum, accent_lum)

    if ratio >= min_ratio:
        return None

    h, s, l = rgb_to_hsl(*accent_rgb)
    step = 2.0
    max_iter = 80
    text_lighter = text_lum > accent_lum

    for i in range(max_iter):
        # Try lighten (increase L) or darken (decrease L)
        if text_lighter:
            # Dark text on light accent: need accent lighter -> higher L
            # Actually: text_lighter means text has higher lum. Ratio = text/accent.
            # To increase ratio we need lower accent lum -> darken accent -> decrease L
            delta_l = -step * (i + 1)
        else:
            # Light text on dark accent: need accent darker -> lower L
            # Actually: accent_lighter. Ratio = accent/text. To increase ratio we need
            # higher accent lum -> lighten accent -> increase L
            delta_l = step * (i + 1)

        new_l = max(0, min(100, l + delta_l))
        new_rgb = hsl_to_rgb(h, s, new_l)
        new_lum = rgb_to_relative_luminance(*new_rgb)
        new_ratio = contrast_ratio(text_lum, new_lum)

        if new_ratio >= min_ratio:
            return (0, 0, new_l - l)

        # Try opposite direction if first didn't work
        if i == 0:
            continue
        delta_l_alt = -delta_l
        new_l_alt = max(0, min(100, l + delta_l_alt))
        new_rgb_alt = hsl_to_rgb(h, s, new_l_alt)
        new_lum_alt = rgb_to_relative_luminance(*new_rgb_alt)
        new_ratio_alt = contrast_ratio(text_lum, new_lum_alt)
        if new_ratio_alt >= min_ratio:
            return (0, 0, new_l_alt - l)

    return None


def get_contrast_info(text_hex: str, accent_hex: str) -> dict:
    """Get contrast ratio and whether it passes WCAG AA."""
    text_rgb = parse_color(text_hex)
    accent_rgb = parse_color(accent_hex)
    if not text_rgb or not accent_rgb:
        return {"ratio": 0, "pass": False, "error": "Invalid color"}
    text_lum = rgb_to_relative_luminance(*text_rgb)
    accent_lum = rgb_to_relative_luminance(*accent_rgb)
    ratio = contrast_ratio(text_lum, accent_lum)
    return {
        "ratio": round(ratio, 2),
        "pass": ratio >= MIN_CONTRAST_RATIO,
        "text_lum": text_lum,
        "accent_lum": accent_lum,
    }
