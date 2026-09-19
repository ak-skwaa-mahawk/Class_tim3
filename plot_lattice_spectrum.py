# plot_lattice_spectrum.py
import json

E_k = [1200.0, 802.2, 593.14, 454.51, 381.46, 351.24, 314.58, 269.84]
dispersion = [0.0000, 0.2929, 1.0000, 1.7071, 2.0000, 1.7071, 1.0000, 0.2929]

width, height = 640, 360
padding = 50

# Map data points to SVG coordinates
max_e = max(E_k)
points = []
for i, e in enumerate(E_k):
    x = padding + (i / (len(E_k) - 1)) * (width - 2 * padding)
    y = height - padding - (e / max_e) * (height - 2 * padding)
    points.append(f"{x:.1f},{y:.1f}")

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <rect width="100%" height="100%" fill="#121316"/>
  <!-- Grid Lines -->
  <line x1="{padding}" y1="{height - padding}" x2="{width - padding}" y2="{height - padding}" stroke="#333" stroke-width="1"/>
  <line x1="{padding}" y1="{padding}" x2="{padding}" y2="{height - padding}" stroke="#333" stroke-width="1"/>
  <!-- Energy Curve -->
  <polyline fill="none" stroke="#00e5ff" stroke-width="3" points="{' '.join(points)}"/>
"""

for i, (pt, e) in enumerate(zip(points, E_k)):
    px, py = pt.split(",")
    svg += f'  <circle cx="{px}" cy="{py}" r="4" fill="#00e5ff"/>\n'
    svg += f'  <text x="{px}" y="{float(py) - 10}" fill="#cfd8dc" font-size="10" text-anchor="middle">M{i}: {e}J</text>\n'

svg += "</svg>"

with open("lattice_spectrum.svg", "w") as f:
    f.write(svg)

print("[OK] Saved lattice_spectrum.svg")
