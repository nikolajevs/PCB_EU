#!/usr/bin/env python3
"""PCB_EU solder-paste stencils (top and bottom) for FDM printing with a 0.2 mm nozzle, parametric CadQuery; SPDX-License-Identifier: MIT.

One stencil per board side. Each is a 0.12 mm film with an aperture for every F.Paste / B.Paste pad (apertures.json,
exported from the PCB by export_apertures.py) and a 0.96 mm skirt that locates the film on the board edge. The film
rests on the board, the skirt hangs down around the PCB. Printed film-down, no supports.

Rebuild: python -m pip install cadquery==2.8.0 matplotlib
         "C:/Program Files/KiCad/10.0/bin/python.exe" hardware/stencil/export_apertures.py   # only after the PCB changed
         python hardware/stencil/stencil.py            # STL (print orientation), coupon, PNG previews
Check:   python hardware/stencil/check_stencil.py      # printability rules + registration against the board STEP

Frames. Print frame (STL): X = KiCad x, Y = KiCad y, squeegee face on the bed (Z = 0), film up to Z = FILM_T, skirt up to
Z_TOTAL. The bottom stencil is mirrored, X = board X0 + X1 - x, because that side is stencilled with the board turned
over its vertical axis. Use frame (use_orientation): the stencil turned over its X axis, as laid on the board: X as in
the print frame, Y = -KiCad y, contact face at Z = 0, film above, skirt below. For the top stencil it is the frame of the
KiCad STEP export of PCB_EU (X = x, Y = -y), for the bottom stencil that frame after turning the board over.
Dimensions in mm. Design notes: hardware/stencil/README.md.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
APERTURES = HERE / "apertures.json"

# ---------------------------------------------------------------- printing parameters (0.2 mm nozzle)
NOZZLE = 0.2
LAYER = 0.06                           # 2 layers make the film; 18 layers make the whole part
FILM_T = 0.12                          # the LM3429 paste windows (DESIGN.md) are drawn for a 0.125 mm stencil
SKIRT_H = 0.96                         # below the film; shorter than any 1.6 mm +-10 % board, so the film lies on the board
Z_TOTAL = FILM_T + SKIRT_H
WALL = 6 * NOZZLE                      # skirt wall: six perimeters
POCKET_CLEARANCE = 0.15                # board edge to skirt, per side
MARGIN = 12.0                          # film beyond the board edge: room for the paste bead and the squeegee run
CORNER_R = 5.0
KEY_CHAMFER = 14.0                     # cuts the film corner above the board corner x = 0, y = 0
LABEL_H, LABEL_RAISE = 4.5, 0.48       # raised text on the contact side, outside the skirt (8 layers)

# print test piece: the finest apertures of the board (U102 VSSOP-10, 0.3 mm apertures, 0.2 mm webs)
COUPON = {"side": "bottom", "ref": "U102", "margin": 5.0}

assert abs(FILM_T / LAYER - round(FILM_T / LAYER)) < 1e-9 and abs(Z_TOTAL / LAYER - round(Z_TOTAL / LAYER)) < 1e-9


# ---------------------------------------------------------------- geometry
def signed_area(pts):
    return 0.5 * sum(x0 * y1 - x1 * y0 for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]))


def prepare(ring, flip_x, ccw):
    """Ring in print-frame coordinates, without the repeated end point, wound as requested."""
    pts = [(flip_x - x if flip_x is not None else x, y) for x, y in ring]
    if pts[0] == pts[-1]:
        pts.pop()
    if (signed_area(pts) > 0) != ccw:
        pts.reverse()
    return pts


def wire(pts, z):
    return cq.Wire.makePolygon([cq.Vector(x, y, z) for x, y in pts], close=True)


def aperture_solid(ap, flip_x, z0, z1):
    outer = wire(prepare(ap["outline"], flip_x, True), z0)
    inner = [wire(prepare(h, flip_x, False), z0) for h in ap["holes"]]
    return cq.Solid.extrudeLinear(cq.Face.makeFromWires(outer, inner), cq.Vector(0, 0, z1 - z0))


def slab(x0, y0, x1, y1, z0, z1, r=0.0):
    wp = cq.Workplane("XY").workplane(offset=z0).center((x0 + x1) / 2, (y0 + y1) / 2).rect(x1 - x0, y1 - y0).extrude(z1 - z0)
    return wp.edges("|Z").fillet(r) if r else wp


def cut_apertures(body, apertures, flip_x):
    tools = [aperture_solid(a, flip_x, -0.1, FILM_T + 0.1) for a in apertures]
    return body.cut(cq.Workplane("XY").newObject([cq.Compound.makeCompound(tools)]))


def outline(data):
    b = data["board"]
    return b["x0"], b["y0"], b["x1"], b["y1"]


def build(side, data):
    """Stencil of one side in the print frame (a cq.Workplane with one solid)."""
    x0, y0, x1, y1 = outline(data)
    flip_x = x0 + x1 if side == "bottom" else None
    film = slab(x0 - MARGIN, y0 - MARGIN, x1 + MARGIN, y1 + MARGIN, 0, FILM_T, CORNER_R)
    # key corner: the film corner above the board corner x = 0, y = 0 (x = X1 on the mirrored bottom stencil)
    kx, ky = (x1 + MARGIN, y0 - MARGIN) if side == "bottom" else (x0 - MARGIN, y0 - MARGIN)
    sx = -1 if side == "bottom" else 1
    key = (cq.Workplane("XY").workplane(offset=-0.1)
           .polyline([(kx - sx * 1.0, ky - 1.0), (kx + sx * KEY_CHAMFER, ky - 1.0), (kx - sx * 1.0, ky + KEY_CHAMFER)]).close()
           .extrude(Z_TOTAL + 0.2))
    p = POCKET_CLEARANCE
    skirt = (slab(x0 - p - WALL, y0 - p - WALL, x1 + p + WALL, y1 + p + WALL, FILM_T, Z_TOTAL)
             .cut(slab(x0 - p, y0 - p, x1 + p, y1 + p, FILM_T - 0.1, Z_TOTAL + 0.1)))
    cx, cy = (x0 + x1) / 2, y0 - (p + WALL + MARGIN) / 2       # middle of the strip between the skirt and the film edge
    label = (cq.Workplane("XY").workplane(offset=FILM_T).center(cx, cy)
             .text(f"PCB_EU {side.upper()[:3]} {FILM_T:g}", LABEL_H, LABEL_RAISE, kind="bold", halign="center", valign="center"))
    body = film.union(skirt).union(label).cut(key)
    return cut_apertures(body, data[side], flip_x)


def coupon(data):
    """Flat film around one part of the board, apertures only: the cheap first print."""
    side, ref = COUPON["side"], COUPON["ref"]
    flip_x = data["board"]["x0"] + data["board"]["x1"] if side == "bottom" else None
    mine = [a for a in data[side] if a["ref"] == ref]
    xs = [x for a in mine for x, _ in a["outline"]]
    ys = [y for a in mine for _, y in a["outline"]]
    m = COUPON["margin"]
    wx0, wx1, wy0, wy1 = min(xs) - m, max(xs) + m, min(ys) - m, max(ys) + m
    inside, cut = [], []
    for a in data[side]:
        ax = [x for x, _ in a["outline"]]
        ay = [y for _, y in a["outline"]]
        if min(ax) >= wx0 and max(ax) <= wx1 and min(ay) >= wy0 and max(ay) <= wy1:
            inside.append(a)
        elif max(ax) > wx0 and min(ax) < wx1 and max(ay) > wy0 and min(ay) < wy1:
            cut.append(a)
    if cut:
        raise SystemExit(f"coupon window cuts through apertures of {sorted({a['ref'] for a in cut})}: change COUPON margin")
    px = [wx0, wx1] if flip_x is None else [flip_x - wx1, flip_x - wx0]
    film = slab(px[0], wy0, px[1], wy1, 0, FILM_T, 1.0)
    return cut_apertures(film, inside, flip_x).translate((-px[0], -wy0, 0))


def use_orientation(wp):
    """Turn the stencil over its X axis and put the contact face at Z = 0."""
    return wp.rotate((0, 0, 0), (1, 0, 0), 180).translate((0, 0, FILM_T))


def squeegee_face(wp):
    """Film seen from the squeegee side (stencil in use orientation): the largest planar face at Z = FILM_T, apertures as holes."""
    faces = [f for f in wp.faces().vals() if abs(f.Center().z - FILM_T) < 1e-6 and abs(f.normalAt().z) > 0.999]
    return max(faces, key=lambda f: f.Area())


def stl(wp, path):
    cq.exporters.export(wp, str(path), tolerance=0.002, angularTolerance=0.05)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--no-preview", action="store_true", help="skip the PNG previews (they need matplotlib)")
    args = ap.parse_args()
    data = json.loads(APERTURES.read_text())
    for side in ("top", "bottom"):
        wp = build(side, data)
        stl(wp, HERE / f"PCB_EU_stencil_{side}_print.stl")
        print(f"{side}: {len(data[side])} apertures, volume {wp.val().Volume():.1f} mm3")
        if not args.no_preview:
            import preview
            preview.render(side, wp, data["board"], HERE / f"PCB_EU_stencil_{side}.png")
    stl(coupon(data), HERE / "PCB_EU_stencil_coupon_print.stl")


if __name__ == "__main__":
    main()
