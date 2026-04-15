"""Generate the PyReo icon — one continuous white ribbon forming two koru.

A single smooth stripe: koru spiral top-left → gentle diagonal → koru spiral bottom-right.
No sharp angles, no U-turns. The spine never reverses direction.
Tino rangatiratanga colours: red top, black bottom, white ribbon.
"""

import math
from pathlib import Path

SIZE = 128
PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_PATH = PROJECT_ROOT / "vscode-pyreo" / "icon.svg"


def make_spine(n=1200):
    """Generate the spine as one continuous curve.

    Structure:
      1. Top-left koru: tight spiral unwinding outward
      2. Smooth diagonal flow from top-left to bottom-right
      3. Bottom-right koru: winding inward to tight spiral

    The key constraint: the curve always flows generally from
    top-left toward bottom-right. No reversals.
    """
    points = []

    # --- Koru 1: top-left, spiral from tip outward ---
    k1_cx, k1_cy = 26, 26
    k1_tip_r = 3
    k1_end_r = 36
    k1_turns = 1.8
    # Tip angle — the innermost point
    k1_tip_angle = math.pi * 0.8
    # Unwind: tip_angle → tip_angle + turns*2pi (counterclockwise unwinding)
    n1 = n // 3

    for i in range(n1 + 1):
        t = i / n1  # 0=tip, 1=wide end
        angle = k1_tip_angle + t * k1_turns * 2 * math.pi
        ease = t ** 0.6
        r = k1_tip_r + ease * (k1_end_r - k1_tip_r)
        points.append((k1_cx + r * math.cos(angle), k1_cy + r * math.sin(angle)))

    # --- Smooth bridge: wide end of koru1 → wide end of koru2 ---
    # The bridge should be a gentle curve, no sharp turns.
    # Use a cubic bezier-like interpolation.
    p_start = points[-1]

    # Compute tangent at end of koru1 for smooth exit
    dx1 = points[-1][0] - points[-3][0]
    dy1 = points[-1][1] - points[-3][1]
    len1 = math.sqrt(dx1**2 + dy1**2)
    tx1, ty1 = dx1 / len1, dy1 / len1  # unit tangent

    # Koru 2 parameters
    k2_cx, k2_cy = 102, 102
    k2_tip_r = 3
    k2_end_r = 36
    k2_turns = 1.8
    k2_tip_angle = math.pi * 1.8
    # Koru2 winds inward: entry_angle → tip_angle
    k2_entry_angle = k2_tip_angle + k2_turns * 2 * math.pi

    p_end = (
        k2_cx + k2_end_r * math.cos(k2_entry_angle),
        k2_cy + k2_end_r * math.sin(k2_entry_angle),
    )

    # Compute tangent at start of koru2 for smooth entry
    # (first two points of koru2 to get direction)
    t_small = 1 / (n // 3)
    angle_k2_0 = k2_entry_angle
    angle_k2_1 = k2_entry_angle - t_small * k2_turns * 2 * math.pi
    ease_1 = t_small ** 0.75
    r_k2_1 = k2_end_r + ease_1 * (k2_tip_r - k2_end_r)
    pk2_1 = (k2_cx + r_k2_1 * math.cos(angle_k2_1), k2_cy + r_k2_1 * math.sin(angle_k2_1))
    dx2 = pk2_1[0] - p_end[0]
    dy2 = pk2_1[1] - p_end[1]
    len2 = math.sqrt(dx2**2 + dy2**2)
    tx2, ty2 = dx2 / len2, dy2 / len2  # unit tangent into koru2

    # Cubic Hermite interpolation for smooth bridge
    # P(t) = h00*p0 + h10*m0 + h01*p1 + h11*m1
    bridge_len = math.sqrt((p_end[0]-p_start[0])**2 + (p_end[1]-p_start[1])**2)
    tension = bridge_len * 0.6  # controls how far control points extend
    m0x, m0y = tx1 * tension, ty1 * tension
    m1x, m1y = tx2 * tension, ty2 * tension

    n2 = n // 3
    for i in range(1, n2 + 1):
        t = i / n2
        # Hermite basis functions
        h00 = (1 + 2*t) * (1-t)**2
        h10 = t * (1-t)**2
        h01 = t**2 * (3 - 2*t)
        h11 = t**2 * (t - 1)
        x = h00*p_start[0] + h10*m0x + h01*p_end[0] + h11*m1x
        y = h00*p_start[1] + h10*m0y + h01*p_end[1] + h11*m1y
        points.append((x, y))

    # --- Koru 2: bottom-right, spiral from wide end inward to tip ---
    n3 = n // 3
    for i in range(1, n3 + 1):
        t = i / n3  # 0=wide end, 1=tip
        angle = k2_entry_angle - t * k2_turns * 2 * math.pi
        ease = t ** 0.6
        r = k2_end_r + ease * (k2_tip_r - k2_end_r)
        points.append((k2_cx + r * math.cos(angle), k2_cy + r * math.sin(angle)))

    return points


def compute_normals(points):
    """Compute unit normals at each point."""
    normals = []
    n = len(points)
    for i in range(n):
        if i == 0:
            dx = points[1][0] - points[0][0]
            dy = points[1][1] - points[0][1]
        elif i == n - 1:
            dx = points[-1][0] - points[-2][0]
            dy = points[-1][1] - points[-2][1]
        else:
            dx = points[i+1][0] - points[i-1][0]
            dy = points[i+1][1] - points[i-1][1]
        length = math.sqrt(dx*dx + dy*dy)
        if length < 0.001:
            length = 0.001
        normals.append((-dy/length, dx/length))
    return normals


def width_func(t):
    """Ribbon half-width. Tapers at both koru tips, full width in middle."""
    taper_in = min(t / 0.12, 1.0)
    taper_out = min((1-t) / 0.12, 1.0)
    taper = min(taper_in, taper_out)
    taper = taper * taper * (3 - 2*taper)  # smoothstep
    return 1.5 + taper * 6.5


def make_ribbon(points, normals):
    """Create filled ribbon from spine + normals."""
    n = len(points)
    left = []
    right = []

    for i in range(n):
        t = i / (n-1)
        w = width_func(t)
        nx, ny = normals[i]
        px, py = points[i]
        left.append((px + nx*w, py + ny*w))
        right.append((px - nx*w, py - ny*w))

    d = f"M {left[0][0]:.2f},{left[0][1]:.2f}"
    for p in left[1:]:
        d += f" L {p[0]:.2f},{p[1]:.2f}"
    # Round tip at koru2 end
    d += f" A 2,2 0 0,1 {right[-1][0]:.2f},{right[-1][1]:.2f}"
    for p in reversed(right):
        d += f" L {p[0]:.2f},{p[1]:.2f}"
    # Round tip at koru1 start
    d += f" A 2,2 0 0,1 {left[0][0]:.2f},{left[0][1]:.2f}"
    d += " Z"
    return d


def generate_svg():
    red = "#CC2229"
    black = "#1a1a1a"
    white = "#FFFFFF"

    spine = make_spine()
    normals = compute_normals(spine)
    ribbon = make_ribbon(spine, normals)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}">
  <defs>
    <clipPath id="rounded">
      <rect width="{SIZE}" height="{SIZE}" rx="14"/>
    </clipPath>
  </defs>

  <g clip-path="url(#rounded)">
    <!-- Red top - Ranginui -->
    <rect width="{SIZE}" height="{SIZE}" fill="{red}"/>
    <!-- Black bottom - Papatūānuku -->
    <rect y="{SIZE//2}" width="{SIZE}" height="{SIZE//2}" fill="{black}"/>

    <!-- Continuous koru ribbon -->
    <path d="{ribbon}" fill="{white}"/>
  </g>
</svg>'''
    return svg


if __name__ == "__main__":
    svg = generate_svg()
    OUTPUT_PATH.write_text(svg, encoding="utf-8")
    print(f"Written to {OUTPUT_PATH}")
