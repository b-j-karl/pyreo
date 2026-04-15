"""Generate the PyReo icon: one continuous white ribbon forming two koru.

Tino rangatiratanga colours: red top, black bottom, white ribbon.
Uses the same algorithm as scripts/icon-tuner.html for consistency.

To tune the icon interactively, open scripts/icon-tuner.html in a browser
and copy the exported SVG. To regenerate the default icon, run this script.
"""

import math
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "vscode-pyreo" / "icon.svg"

SIZE = 128
N = 900

# Default parameters (match scripts/icon-tuner.html defaults)
PARAMS = {
    "center": 30,
    "tip_r": 3,
    "end_r": 32,
    "turns": 1.6,
    "tip_angle_pi": 0.8,
    "ease": 0.7,
    "tension_factor": 0.6,
    "w_min": 1.5,
    "w_max": 7.0,
    "taper_len": 0.12,
}


def generate_svg(p=None):
    if p is None:
        p = PARAMS

    center = p["center"]
    tip_r = p["tip_r"]
    end_r = p["end_r"]
    turns = p["turns"]
    tip_angle_pi = p["tip_angle_pi"]
    ease = p["ease"]
    tension_factor = p["tension_factor"]
    w_min = p["w_min"]
    w_max = p["w_max"]
    taper_len = p["taper_len"]

    k1cx, k1cy = center, center
    k2cx, k2cy = SIZE - center, SIZE - center
    k1_tip_angle = math.pi * tip_angle_pi
    k2_tip_angle = math.pi * (tip_angle_pi + 1)

    points = []
    n1 = N // 3
    n2 = N // 3
    n3 = N // 3

    # Koru 1: tip to wide end
    for i in range(n1 + 1):
        t = i / n1
        angle = k1_tip_angle + t * turns * 2 * math.pi
        e = t ** ease
        r = tip_r + e * (end_r - tip_r)
        points.append((k1cx + r * math.cos(angle), k1cy + r * math.sin(angle)))

    # Bridge: Hermite interpolation
    p_start = points[-1]
    p_prev = points[-3]
    dx1, dy1 = p_start[0] - p_prev[0], p_start[1] - p_prev[1]
    len1 = math.sqrt(dx1 * dx1 + dy1 * dy1)
    tx1, ty1 = dx1 / len1, dy1 / len1

    k2_entry_angle = k2_tip_angle + turns * 2 * math.pi
    p_end = (k2cx + end_r * math.cos(k2_entry_angle),
             k2cy + end_r * math.sin(k2_entry_angle))

    # Koru 2 entry tangent (first spiral step)
    t_small = 1 / n3
    a2next = k2_entry_angle - t_small * turns * 2 * math.pi
    # Mirror koru 1's radius profile: at t going wide->tip, radius matches
    # koru 1 at (1-t) going tip->wide.
    e2 = (1 - t_small) ** ease
    r2next = tip_r + e2 * (end_r - tip_r)
    pk2next = (k2cx + r2next * math.cos(a2next),
               k2cy + r2next * math.sin(a2next))
    dx2, dy2 = pk2next[0] - p_end[0], pk2next[1] - p_end[1]
    len2 = math.sqrt(dx2 * dx2 + dy2 * dy2)
    tx2, ty2 = dx2 / len2, dy2 / len2

    bridge_len = math.sqrt((p_end[0] - p_start[0]) ** 2
                           + (p_end[1] - p_start[1]) ** 2)
    tension = bridge_len * tension_factor
    m0x, m0y = tx1 * tension, ty1 * tension
    m1x, m1y = tx2 * tension, ty2 * tension

    for i in range(1, n2 + 1):
        t = i / n2
        h00 = (1 + 2 * t) * (1 - t) * (1 - t)
        h10 = t * (1 - t) * (1 - t)
        h01 = t * t * (3 - 2 * t)
        h11 = t * t * (t - 1)
        points.append((
            h00 * p_start[0] + h10 * m0x + h01 * p_end[0] + h11 * m1x,
            h00 * p_start[1] + h10 * m0y + h01 * p_end[1] + h11 * m1y,
        ))

    # Koru 2: wide end to tip (mirrored from koru 1 under 180 deg rotation)
    for i in range(1, n3 + 1):
        t = i / n3
        angle = k2_entry_angle - t * turns * 2 * math.pi
        # Mirror koru 1's radius profile for symmetry
        e = (1 - t) ** ease
        r = tip_r + e * (end_r - tip_r)
        points.append((k2cx + r * math.cos(angle), k2cy + r * math.sin(angle)))

    # Normals
    normals = []
    npts = len(points)
    for i in range(npts):
        if i == 0:
            dx, dy = points[1][0] - points[0][0], points[1][1] - points[0][1]
        elif i == npts - 1:
            dx, dy = points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]
        else:
            dx, dy = points[i + 1][0] - points[i - 1][0], points[i + 1][1] - points[i - 1][1]
        length = math.sqrt(dx * dx + dy * dy) or 0.001
        normals.append((-dy / length, dx / length))

    # Ribbon edges
    left = []
    right = []
    for i in range(npts):
        t = i / (npts - 1)
        tap_in = min(t / taper_len, 1.0)
        tap_out = min((1 - t) / taper_len, 1.0)
        tap = min(tap_in, tap_out)
        tap = tap * tap * (3 - 2 * tap)
        w = w_min + tap * (w_max - w_min)
        nx, ny = normals[i]
        px, py = points[i]
        left.append((px + nx * w, py + ny * w))
        right.append((px - nx * w, py - ny * w))

    # Build path
    d = f"M {left[0][0]:.2f},{left[0][1]:.2f}"
    for pt in left[1:]:
        d += f" L {pt[0]:.2f},{pt[1]:.2f}"
    d += f" A 2,2 0 0,1 {right[-1][0]:.2f},{right[-1][1]:.2f}"
    for pt in reversed(right):
        d += f" L {pt[0]:.2f},{pt[1]:.2f}"
    d += f" A 2,2 0 0,1 {left[0][0]:.2f},{left[0][1]:.2f} Z"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}">
  <defs><clipPath id="rounded"><rect width="{SIZE}" height="{SIZE}" rx="14"/></clipPath></defs>
  <g clip-path="url(#rounded)">
    <rect width="{SIZE}" height="{SIZE}" fill="#1a1a1a"/>
    <rect y="{SIZE // 2}" width="{SIZE}" height="{SIZE // 2}" fill="#CC2229"/>
    <path d="{d}" fill="#FFFFFF"/>
  </g>
</svg>'''


if __name__ == "__main__":
    svg = generate_svg()
    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    print(f"Written to {OUTPUT_PATH}")
