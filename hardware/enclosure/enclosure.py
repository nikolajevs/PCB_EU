#!/usr/bin/env python3
"""PCB_EU controller enclosure (base + lid), parametric CadQuery; SPDX-License-Identifier: MIT.

Same construction as the PCB_V1 enclosure (lap joint, snap fingers without screws, wall ears), with these changes
for PCB_EU: four M3 bosses at the board holes instead of lid ribs, a 33 mm ceiling for the 30 mm heatsink HS1, a deep
floor for the long leads of Q501/Q601 and the back-side inductors, other connector windows.

Rebuild: python -m pip install cadquery==2.8.0
         python hardware/enclosure/enclosure.py            # STEP (board frame) + STL (print orientation)
Check:   python hardware/enclosure/check_enclosure.py      # interference / clearance against the board STEP

Frame (identical to the KiCad STEP export of PCB_EU, review/PCB_EU_assembly.step): X = KiCad x, Y = -KiCad y,
board bottom at Z = 0, board top at Z = 1.6. KiCad coordinates are used for everything that is placed along a wall;
sides are named after the KiCad drawing: L = x 0 edge, R = x 100, T = y 0, B = y 100 (terminal row).
Dimensions in mm. Design notes: hardware/enclosure/README.md.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import cadquery as cq

OUT = Path(__file__).resolve().parent

# ---------------------------------------------------------------- board and shell parameters
BX0, BX1 = 0.0, 100.0                  # board outline, STEP X
BY0, BY1 = -100.0, 0.0                 # board outline, STEP Y
CTR = (50.0, -50.0)
BOARD_TOP = 1.6
GAP = 0.4                              # board edge to inner wall
T = 2.6                                # wall and plate thickness (skin + gap + tongue, 0.4 mm nozzle multiples)
IX0, IX1, IY0, IY1 = BX0 - GAP, BX1 + GAP, BY0 - GAP, BY1 + GAP
OX0, OX1, OY0, OY1 = IX0 - T, IX1 + T, IY0 - T, IY1 + T
R_IN = 0.5
R_OUT = R_IN + T

FLOOR_T = 2.0                          # PETG, 5 perimeters-equivalent at 0.4 mm nozzle
Z_FLOOR = -9.2                         # inner floor: leads of Q501/Q601 and the HS1 pins end at -8.2, +1.0 mm
Z_BOT = Z_FLOOR - FLOOR_T              # outside of the base floor (against the wall)
Z_LEDGE = 0.0                          # board rests here
Z_SPLIT = BOARD_TOP                    # joint plane between base and lid
HS1_TOP = BOARD_TOP + 0.3 + 30.0       # HS1 stands on its 30 mm end face over a 0.3 mm pad (placement.json heatsink_legs)
Z_CEIL = 33.0                          # inner ceiling: HS1 top 31.9 + 1.1
Z_TOP = Z_CEIL + T

# lap joint: tongue on the base (inside), skin on the lid (outside), 0.2 mm clearance
TONGUE_T, SKIN_T, JOINT_GAP = 1.2, 1.2, 0.2
TONGUE_H, GROOVE_H = 9.0, 9.4
assert abs(T - (SKIN_T + JOINT_GAP + TONGUE_T)) < 1e-9
Z_TONGUE = Z_SPLIT + TONGUE_H

# ---------------------------------------------------------------- features (KiCad coordinates along a wall)
# M3 holes of the board (placement.json mounting_holes H1..H4): self-tapping screws into printed bosses
HOLES = [(61.0, 3.5), (96.5, 3.5), (3.5, 85.0), (96.5, 96.5)]
BOSS_OD, BOSS_PILOT, BOSS_DEPTH = 6.4, 2.8, 8.0

# board support blocks under the edge (2.0 mm wide, top at the board bottom). Placed where nothing sits under the
# edge: left x < 1.6 is free except the J411/J421 pin tails (ky 25..47) and the microSD J301 (ky 76..79)
LEDGE_W, LEDGE_L = 2.0, 8.0
LEDGES = [('T', 12.0), ('T', 36.0), ('T', 80.0),
          ('L', 7.0), ('L', 54.0), ('L', 92.0),
          ('R', 12.0), ('R', 30.0), ('R', 55.0), ('R', 95.0),
          ('B', 8.0), ('B', 88.0)]

# wall windows from the connector bodies (STEP bounding boxes, +0.5 mm per side), z from..to absolute.
# Terminals: the wire enters from the outside, so the window is open to the full body height plus wire room.
NOTCHES = [
    ('L', 47.6, 59.3, Z_SPLIT, 10.2, 'J101 power input terminal'),
    ('L', 24.5, 47.1, -2.0, 13.8, 'J411/J421 XH 1x04 (horizontal)'),
    ('L', 64.5, 79.5, 0.6, 4.1, 'J301 microSD (card in/out)'),
    ('B', 14.2, 27.6, 0.6, 8.2, 'J401 XH 1x04 90deg'),
    ('B', 29.4, 41.0, Z_SPLIT, 12.6, 'J403 terminal'),
    ('B', 42.4, 54.0, Z_SPLIT, 12.6, 'J701 terminal'),
    ('B', 54.4, 66.0, Z_SPLIT, 12.6, 'J601 terminal'),
    ('B', 66.3, 77.8, Z_SPLIT, 12.6, 'J602 terminal'),
    ('R', 40.2, 51.8, Z_SPLIT, 12.6, 'J501 terminal'),
    ('R', 56.0, 67.6, Z_SPLIT, 12.6, 'J702 terminal'),
]
# vertical connectors reached through the ceiling: x0, x1, y0, y1 in KiCad coordinates
CEIL_WINDOWS = [
    (1.9, 6.1, 8.0, 24.2, 'J201 UART header 1x06 (Dupont from above)'),
]
# BOOT / RESET: guide tube from the ceiling down to the tact switch
BUTTONS = [(20.0, 30.7, 'SW201'), (31.0, 30.7, 'SW202')]
TUBE_OD, TUBE_ID, TUBE_BOT = 6.4, 2.8, 4.5

# snap fit: windows in the lid skin (fingers), ridges on the base tongue
SNAPS = [('T', 22.0), ('T', 50.0), ('T', 78.0), ('L', 14.0), ('L', 38.0), ('R', 20.0), ('R', 46.0), ('B', 90.0)]
SNAP_WIN = (3.8, 6.4)                  # window z range above the split
SNAP_HALF_WIN, SNAP_SLIT_IN, SNAP_SLIT_OUT = 3.0, 5.6, 6.4
RIDGE_P, RIDGE_RUN_LOW, RIDGE_RUN_UP = 0.6, 1.4, 1.2
PRY = [('T', 62.0), ('R', 74.0)]       # screwdriver notches at the lid bottom edge

# ventilation (HS1 stands under the ceiling at x 68..98, y 24..39: chimney slots above it)
CEIL_VENT_ZONES = [(68, 97, 24, 38), (62, 97, 56, 94), (22, 62, 54, 94), (44, 62, 4, 30)]
VENT_W, VENT_PITCH, VENT_MAX_L = 2.0, 4.2, 16.0
LID_WALL_SLOTS = {'T': [20, 40, 60, 80], 'B': [22, 46, 70, 92], 'L': [20, 50, 80], 'R': [18, 36, 56, 80]}
LID_SLOT_Z, LID_SLOT_L = (24.0, 29.0), 10.0
BASE_WALL_SLOTS = {'L': [16, 62, 84], 'R': [22, 44, 66, 84], 'T': [24, 50, 66, 94], 'B': [30, 50, 70]}
BASE_SLOT_Z, BASE_SLOT_L = (Z_FLOOR + 1.6, Z_FLOOR + 6.6), 10.0

# wall mounting ears, Ø4.5 hole with a 90° countersink for a Ø8.6 head
EAR_R, EAR_T, EAR_HOLE, EAR_HEAD, EAR_DY = 6.0, 3.6, 4.5, 8.6, 46.0
EAR_OFFSET = 7.0


# ---------------------------------------------------------------- helpers
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def kbox(kx0, kx1, ky0, ky1, z0, z1):
    return box(kx0, kx1, -ky1, -ky0, z0, z1)


def rrect(inset, z0, z1):
    """Rounded rectangle, inset mm inside the outer shell outline."""
    x0, x1, y0, y1 = OX0 + inset, OX1 - inset, OY0 + inset, OY1 - inset
    r = max(R_OUT - inset, 0.0)
    w = (cq.Workplane("XY").workplane(offset=z0).center((x0 + x1) / 2, (y0 + y1) / 2)
         .rect(x1 - x0, y1 - y0).extrude(z1 - z0))
    return w.edges("|Z").fillet(r) if r > 0.01 else w


def ring(inset_out, inset_in, z0, z1):
    return rrect(inset_out, z0, z1).cut(rrect(inset_in, z0 - 1, z1 + 1))


def wall_box(side, a0, a1, d0, d1, z0, z1):
    """Box on a wall: a0..a1 KiCad coordinate along the wall, d0..d1 depth inward from the outer face."""
    if side == 'L':
        return box(OX0 + d0, OX0 + d1, -a1, -a0, z0, z1)
    if side == 'R':
        return box(OX1 - d1, OX1 - d0, -a1, -a0, z0, z1)
    if side == 'T':
        return box(a0, a1, OY1 - d1, OY1 - d0, z0, z1)
    return box(a0, a1, OY0 + d0, OY0 + d1, z0, z1)


ROT = {'B': 0.0, 'R': 90.0, 'T': 180.0, 'L': 270.0}


def wall_point(side, c):
    return {'L': (OX0, -c), 'R': (OX1, -c), 'T': (c, OY1), 'B': (c, OY0)}[side]


def to_side(shape, side, c):
    """Place a feature built on wall B (centred on x = along) onto another wall at KiCad position c."""
    px, py = wall_point(side, c)
    a = math.radians(-ROT[side])
    dx, dy = px - CTR[0], py - CTR[1]
    along = CTR[0] + dx * math.cos(a) - dy * math.sin(a)
    return shape.translate((along, 0, 0)).rotate((CTR[0], CTR[1], 0), (CTR[0], CTR[1], 1), ROT[side])


def cut_all(body, tools):
    shape = body.val().cut(*[t.val() for t in tools])
    return cq.Workplane("XY").newObject([shape])


def fuse_all(body, parts):
    shape = body.val().fuse(*[p.val() for p in parts]).clean()
    return cq.Workplane("XY").newObject([shape])


def overlaps(a0, a1, intervals, margin):
    return any(a0 < b1 + margin and a1 > b0 - margin for b0, b1 in intervals)


# ---------------------------------------------------------------- base
def ridge(c, side):
    """Snap ridge on the outer face of the tongue (built on wall B, then moved)."""
    lo, hi = SNAP_WIN
    p = RIDGE_P
    za = Z_SPLIT + lo + JOINT_GAP - JOINT_GAP * RIDGE_RUN_LOW / p
    zb = za + RIDGE_RUN_LOW
    zd = Z_SPLIT + hi - JOINT_GAP + JOINT_GAP * RIDGE_RUN_UP / p
    zc = zd - RIDGE_RUN_UP
    y_t = OY0 + SKIN_T + JOINT_GAP                # tongue outer face
    pts = [(y_t + 0.2, za), (y_t, za), (y_t - p, zb), (y_t - p, zc), (y_t, zd), (y_t + 0.2, zd)]
    half = SNAP_HALF_WIN - 0.3
    prism = cq.Workplane("YZ").polyline(pts).close().extrude(2 * half).translate((-half, 0, 0))
    return to_side(prism, side, c)


def ear(sx, sy):
    hx = CTR[0] + sx * (OX1 - CTR[0] + EAR_OFFSET)
    hy = CTR[1] + sy * EAR_DY
    wall_x = CTR[0] + sx * (OX1 - CTR[0] - 1.0)
    lug = cq.Workplane("XY").workplane(offset=Z_BOT).center(hx, hy).circle(EAR_R).extrude(EAR_T)
    lug = lug.union(box(min(hx, wall_x), max(hx, wall_x), hy - EAR_R, hy + EAR_R, Z_BOT, Z_BOT + EAR_T))
    return lug, (hx, hy)


def boss(kx, ky):
    """Cylinder from the floor to the board bottom at a mounting hole; the pilot hole is cut later."""
    return (cq.Workplane("XY").workplane(offset=Z_FLOOR - 0.1).center(kx, -ky).circle(BOSS_OD / 2)
            .extrude(Z_LEDGE - Z_FLOOR + 0.1))


def build_base():
    outer = rrect(0, Z_BOT, Z_SPLIT).faces("<Z").chamfer(0.8)
    base = outer.cut(rrect(T, Z_FLOOR, Z_SPLIT + 1))
    parts = [ring(SKIN_T + JOINT_GAP, T, Z_SPLIT, Z_TONGUE)]
    for side, c in LEDGES:
        parts.append(wall_box(side, c - LEDGE_L / 2, c + LEDGE_L / 2, T - 0.1, T + LEDGE_W, Z_FLOOR - 0.1, Z_LEDGE))
    parts += [boss(kx, ky) for kx, ky in HOLES]
    for side, c in SNAPS:
        parts.append(ridge(c, side))
    ears = [ear(sx, sy) for sx in (-1, 1) for sy in (-1, 1)]
    parts += [e[0] for e in ears]
    base = fuse_all(base, parts)
    tools = []
    for kx, ky in HOLES:
        tools.append(cq.Workplane("XY").workplane(offset=Z_LEDGE - BOSS_DEPTH).center(kx, -ky)
                     .circle(BOSS_PILOT / 2).extrude(BOSS_DEPTH + 0.5))
    for side, a0, a1, zbot, ztop, _ in NOTCHES:
        tools.append(wall_box(side, a0, a1, -1.0, T + 0.05, zbot, ztop + 1.0))
    ledge_iv = {s: [(c - LEDGE_L / 2, c + LEDGE_L / 2) for sd, c in LEDGES if sd == s] for s in 'LRTB'}
    for side, centers in BASE_WALL_SLOTS.items():
        for c in centers:
            if overlaps(c - BASE_SLOT_L / 2, c + BASE_SLOT_L / 2, ledge_iv[side], 0.5):
                continue
            tools.append(wall_box(side, c - BASE_SLOT_L / 2, c + BASE_SLOT_L / 2, -1.0, T + 0.05, *BASE_SLOT_Z))
    for _, (hx, hy) in ears:
        tools.append(cq.Workplane("XY").workplane(offset=Z_BOT - 1).center(hx, hy).circle(EAR_HOLE / 2).extrude(EAR_T + 2))
        depth = (EAR_HEAD - EAR_HOLE) / 2
        cone = cq.Solid.makeCone(EAR_HOLE / 2, EAR_HEAD / 2 + 0.5, depth + 0.5,
                                 pnt=cq.Vector(hx, hy, Z_BOT + EAR_T - depth), dir=cq.Vector(0, 0, 1))
        tools.append(cq.Workplane("XY").newObject([cone]))
    return cut_all(base, tools)


# ---------------------------------------------------------------- lid
def build_lid():
    lid = rrect(0, Z_SPLIT, Z_TOP).faces(">Z").chamfer(1.0)
    lid = lid.cut(rrect(T, Z_SPLIT - 1, Z_CEIL))
    lid = lid.cut(rrect(SKIN_T, Z_SPLIT - 1, Z_SPLIT + GROOVE_H))
    parts = []
    for bx, by, _ in BUTTONS:
        tube = (cq.Workplane("XY").workplane(offset=TUBE_BOT).center(bx, -by).circle(TUBE_OD / 2)
                .extrude(Z_CEIL + 0.1 - TUBE_BOT))
        parts.append(tube)
    lid = fuse_all(lid, parts)

    tools = []
    for side, a0, a1, _, ztop, _ in NOTCHES:
        tools.append(wall_box(side, a0, a1, -1.0, T + 0.05, Z_SPLIT - 1, ztop))
    for x0, x1, y0, y1, _ in CEIL_WINDOWS:
        tools.append(kbox(x0, x1, y0, y1, Z_CEIL - 0.1, Z_TOP + 1))
    for bx, by, _ in BUTTONS:
        tools.append(cq.Workplane("XY").workplane(offset=TUBE_BOT - 1).center(bx, -by).circle(TUBE_ID / 2)
                     .extrude(Z_TOP + 2 - TUBE_BOT))
    lo, hi = SNAP_WIN
    for side, c in SNAPS:
        tools.append(wall_box(side, c - SNAP_HALF_WIN, c + SNAP_HALF_WIN, -1.0, SKIN_T + 0.05,
                              Z_SPLIT + lo, Z_SPLIT + hi))
        for sgn in (-1, 1):
            a0, a1 = sorted((c + sgn * SNAP_SLIT_IN, c + sgn * SNAP_SLIT_OUT))
            tools.append(wall_box(side, a0, a1, -1.0, SKIN_T + 0.05, Z_SPLIT - 1, Z_SPLIT + GROOVE_H - 0.6))
    for side, c in PRY:
        tools.append(wall_box(side, c - 4, c + 4, -1.0, SKIN_T + 0.05, Z_SPLIT - 1, Z_SPLIT + 1.2))
    excl = [(x0 - 2, x1 + 2, y0 - 2, y1 + 2) for x0, x1, y0, y1, _ in CEIL_WINDOWS]
    excl += [(bx - TUBE_OD / 2 - 2, bx + TUBE_OD / 2 + 2, by - TUBE_OD / 2 - 2, by + TUBE_OD / 2 + 2) for bx, by, _ in BUTTONS]
    for x0, x1, y0, y1 in CEIL_VENT_ZONES:
        n = int((x1 - x0 - VENT_W) // VENT_PITCH) + 1
        x_start = x0 + VENT_W / 2 + (x1 - x0 - VENT_W - (n - 1) * VENT_PITCH) / 2
        length = min(y1 - y0, VENT_MAX_L)
        yc = (y0 + y1) / 2
        for i in range(n):
            xc = x_start + i * VENT_PITCH
            if any(xc - VENT_W / 2 < ex1 and xc + VENT_W / 2 > ex0 and yc - length / 2 < ey1 and yc + length / 2 > ey0
                   for ex0, ex1, ey0, ey1 in excl):
                continue
            tools.append(cq.Workplane("XY").workplane(offset=Z_CEIL - 0.1).center(xc, -yc)
                         .slot2D(length, VENT_W, 90).extrude(T + 0.2))
    blocked = {s: [(a0, a1) for sd, a0, a1, _, zt, _ in NOTCHES if sd == s and zt > LID_SLOT_Z[0]] for s in 'LRTB'}
    for side, centers in LID_WALL_SLOTS.items():
        for c in centers:
            if overlaps(c - LID_SLOT_L / 2, c + LID_SLOT_L / 2, blocked[side], 1.0):
                continue
            tools.append(wall_box(side, c - LID_SLOT_L / 2, c + LID_SLOT_L / 2, -1.0, T + 0.05, *LID_SLOT_Z))
    return cut_all(lid, tools)


# ---------------------------------------------------------------- output
COUPON_X = (43.0, 57.0)                # KiCad x range of the T-wall snap at x = 50, for a quick fit test print


def coupon(wp):
    cutter = box(COUPON_X[0], COUPON_X[1], OY1 - 7.0, OY1 + 1.0, Z_BOT - 1, Z_TOP + 1)
    return cq.Workplane("XY").newObject([wp.val().intersect(cutter.val())])


def print_orientation(wp, flip):
    s = wp.val()
    if flip:
        s = s.rotate(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), 180)
    bb = s.BoundingBox()
    return s.translate(cq.Vector(-bb.xmin, -bb.ymin, -bb.zmin))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-stl", action="store_true")
    args = ap.parse_args()
    base, lid = build_base(), build_lid()
    for name, wp, flip in (("base", base, False), ("lid", lid, True)):
        shape = wp.val()
        bb = shape.BoundingBox()
        print(f"{name}: {len(shape.Solids())} solid(s), volume {shape.Volume() / 1000:.1f} cm3, "
              f"x {bb.xmin:.1f}..{bb.xmax:.1f} y {bb.ymin:.1f}..{bb.ymax:.1f} z {bb.zmin:.1f}..{bb.zmax:.1f}")
        cq.exporters.export(wp, str(OUT / f"PCB_EU_{name}.step"))
        if not args.no_stl:
            cq.exporters.export(cq.Workplane("XY").newObject([print_orientation(wp, flip)]),
                                str(OUT / f"PCB_EU_{name}_print.stl"), tolerance=0.03, angularTolerance=0.15)
            cq.exporters.export(cq.Workplane("XY").newObject([print_orientation(coupon(wp), flip)]),
                                str(OUT / f"PCB_EU_{name}_coupon_print.stl"), tolerance=0.03, angularTolerance=0.15)


if __name__ == "__main__":
    main()
