#!/usr/bin/env python3
"""Checks of the PCB_EU stencils: printability with a 0.2 mm nozzle, the STL files and registration against the board STEP.

Usage:  python hardware/stencil/check_stencil.py [board.step] [--no-step]
        (default board: hardware/PCB_EU/review/PCB_EU_assembly.step)
Run it in the CadQuery environment (about two minutes). Exit code 1 on any failed rule.

1. Aperture rules on apertures.json: IPC-7525 area and aspect ratio for the film thickness, nozzle limits for the narrowest
   aperture and web, apertures clear of the skirt, no islands.
2. The stencils built by stencil.py: one valid solid, one through hole per aperture, hole area equal to the apertures,
   the skirt clears the board by POCKET_CLEARANCE and does not reach the table, film lies flat on the board.
3. The STL files on disk: closed oriented mesh, volume and size equal to the solid (so they are not stale).
4. Skirt: no part of the KiCad STEP export reaches into the skirt ring around the board edge.
5. Registration: the centre of every hole of the built stencil, laid on the board, must fall over a component body of the
   same side in the KiCad STEP export (within PAD_TOL). The same test with the other side and with the wrong flip is run as
   a control and must match far less, otherwise it says nothing about the mapping.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer
import cadquery as cq

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import stencil  # noqa: E402

BOARD_STEP = HERE.parent / "PCB_EU" / "review" / "PCB_EU_assembly.step"

MIN_APERTURE = 1.5 * stencil.NOZZLE      # narrowest aperture: one and a half extrusion lines
MIN_WEB = stencil.NOZZLE                 # narrowest web between apertures: one extrusion line
MIN_AREA_RATIO = 0.66                    # IPC-7525: aperture area / wall area
MIN_ASPECT = 1.5                         # IPC-7525: aperture width / film thickness
TOL = 1e-3
PAD_TOL = 0.2                            # mm, aperture centre to the nearest part body of the same side
MIN_MATCH = 0.98                         # share of apertures that must be over a part body
MAX_CONTROL = 0.75                       # the control mappings must match less than this
STL_VOLUME_TOL = 0.005                   # relative; the mesh approximates the arcs of the outline and the label


# ---------------------------------------------------------------- aperture geometry
def area(ring):
    r = np.asarray(ring)
    return 0.5 * abs(np.dot(r[:, 0], np.roll(r[:, 1], -1)) - np.dot(r[:, 1], np.roll(r[:, 0], -1)))


def perimeter(ring):
    r = np.asarray(ring)
    return float(np.linalg.norm(np.roll(r, -1, axis=0) - r, axis=1).sum())


def min_width(ring):
    """Narrowest width of a convex ring: the smallest extent across the normal of one of its edges."""
    r = np.asarray(ring)
    e = np.roll(r, -1, axis=0) - r
    n = np.stack([-e[:, 1], e[:, 0]], axis=1)
    n = n[np.linalg.norm(n, axis=1) > 1e-9]
    n /= np.linalg.norm(n, axis=1)[:, None]
    p = r @ n.T
    return float((p.max(axis=0) - p.min(axis=0)).min())


def ring_distance(a, b):
    def point_to_ring(p, q):
        s0, s1 = q, np.roll(q, -1, axis=0)
        d = s1 - s0
        t = np.clip(((p[:, None] - s0[None]) * d[None]).sum(2) / np.maximum((d ** 2).sum(1), 1e-18)[None], 0, 1)
        return np.linalg.norm(p[:, None] - (s0[None] + t[..., None] * d[None]), axis=2).min()
    a, b = np.asarray(a), np.asarray(b)
    return float(min(point_to_ring(a, b), point_to_ring(b, a)))


def check_apertures(side, aps, board):
    bad = []
    rings = [np.asarray(a["outline"]) for a in aps]
    names = [f"{a['ref']}.{a['pad']}" for a in aps]
    t = stencil.FILM_T
    widths = [min_width(r) for r in rings]
    ratios = [area(r) / (perimeter(r) * t) for r in rings]
    lo, hi = np.array([r.min(0) for r in rings]), np.array([r.max(0) for r in rings])
    webs = []
    for i in range(len(rings)):
        near = np.where(np.all(lo < hi[i] + MIN_WEB * 3, axis=1) & np.all(hi > lo[i] - MIN_WEB * 3, axis=1))[0]
        webs += [(ring_distance(rings[i], rings[j]), names[i], names[j]) for j in near if j > i]
    w, r, web = np.argmin(widths), np.argmin(ratios), min(webs)
    edge = MIN_WEB - stencil.POCKET_CLEARANCE      # the film between an aperture and the skirt wall is then at least MIN_WEB
    inside = all(lo[:, 0] >= board["x0"] + edge) and all(hi[:, 0] <= board["x1"] - edge) \
        and all(lo[:, 1] >= board["y0"] + edge) and all(hi[:, 1] <= board["y1"] - edge)
    paste = sum(area(r) for r in rings)
    print(f"{side}: {len(aps)} apertures, paste {paste:.0f} mm2 = {paste * t:.0f} mm3 per print")
    print(f"  narrowest aperture {widths[w]:.3f} mm ({names[w]}), aspect {widths[w] / t:.2f}")
    print(f"  narrowest web {web[0]:.3f} mm ({web[1]} - {web[2]})")
    print(f"  smallest area ratio {ratios[r]:.2f} ({names[r]})")
    for ok, msg in [(widths[w] >= MIN_APERTURE - TOL, f"aperture {names[w]} narrower than {MIN_APERTURE:.2f} mm"),
                    (web[0] >= MIN_WEB - TOL, f"web {web[1]} - {web[2]} thinner than {MIN_WEB:.2f} mm"),
                    (ratios[r] >= MIN_AREA_RATIO, f"area ratio of {names[r]} below {MIN_AREA_RATIO}"),
                    (widths[w] / t >= MIN_ASPECT, f"aspect ratio of {names[w]} below {MIN_ASPECT}"),
                    (inside, f"an aperture is within {edge:.2f} mm of the board edge or outside the board"),
                    (all(not a["holes"] for a in aps), "an aperture has an island (it would drop out of the film)")]:
        if not ok:
            bad.append(f"{side}: {msg}")
    return bad


# ---------------------------------------------------------------- solids (use orientation: contact face at Z = 0)
def check_solid(side, wp, aps, board):
    bad = []
    solid = wp.val()
    bb = solid.BoundingBox()
    face = stencil.squeegee_face(wp)
    expect = sum(area(a["outline"]) for a in aps)
    outer = cq.Face.makeFromWires(face.outerWire()).Area()
    x0, x1, y0, y1 = board["x0"], board["x1"], -board["y1"], -board["y0"]
    p, t = stencil.POCKET_CLEARANCE, board["thickness"]

    def overlap(grow, z0, z1):
        block = cq.Workplane("XY").box(x1 - x0 + 2 * grow, y1 - y0 + 2 * grow, z1 - z0, centered=False).translate((x0 - grow, y0 - grow, z0))
        return sum(s.Volume() for s in wp.intersect(block).solids().vals())

    skirt_in = overlap(p - 0.01, -t, 0)             # the board itself: nothing may touch it
    skirt_out = overlap(p + 0.01, -t, 0)            # 0.01 mm bigger: the skirt wall must be there
    print(f"  solid: valid={solid.isValid()}, solids={len(wp.solids().vals())}, volume {solid.Volume():.1f} mm3, "
          f"{bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.2f} mm, board pocket overlap {skirt_in:.3f} / {skirt_out:.3f} mm3")
    for ok, msg in [(solid.isValid(), "invalid solid"),
                    (len(wp.solids().vals()) == 1, "more than one solid"),
                    (abs(bb.zlen - stencil.Z_TOTAL) < TOL and abs(bb.zmax - stencil.FILM_T) < TOL, "height is not film + skirt"),
                    (len(face.innerWires()) == len(aps), f"{len(face.innerWires())} holes in the film, {len(aps)} apertures"),
                    (abs(outer - face.Area() - expect) < 0.05, f"hole area {outer - face.Area():.2f} mm2 differs from {expect:.2f} mm2"),
                    (skirt_in < 1e-6, f"the stencil overlaps the board by {skirt_in:.3f} mm3"),
                    (skirt_out > 1.0, "no skirt wall at the expected clearance from the board edge"),
                    (stencil.SKIRT_H <= 0.9 * t, "skirt is not shorter than the thinnest board, the film would not touch it")]:
        if not ok:
            bad.append(f"{side}: {msg}")
    return bad, face


# ---------------------------------------------------------------- STL files (print orientation)
def read_stl(path):
    raw = path.read_bytes()
    n = int.from_bytes(raw[80:84], "little")
    if 84 + 50 * n != len(raw):
        raise SystemExit(f"{path.name}: not a binary STL")
    rec = np.frombuffer(raw, dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n, offset=84)
    return rec["v"].astype(float)


def mesh_report(tris):
    """Volume, bounding box and whether every directed edge is used once and has its reverse (closed oriented mesh)."""
    vol = np.einsum("ij,ij->i", tris[:, 0], np.cross(tris[:, 1], tris[:, 2])).sum() / 6
    _, inv = np.unique(np.round(tris.reshape(-1, 3), 4), axis=0, return_inverse=True)
    idx = inv.reshape(-1, 3)
    idx = idx[(idx[:, 0] != idx[:, 1]) & (idx[:, 1] != idx[:, 2]) & (idx[:, 2] != idx[:, 0])]
    edges = np.concatenate([idx[:, [0, 1]], idx[:, [1, 2]], idx[:, [2, 0]]])
    uniq, cnt = np.unique(edges, axis=0, return_counts=True)
    have = {tuple(e) for e in uniq}
    closed = bool((cnt == 1).all() and all((b, a) in have for a, b in have))
    pts = tris.reshape(-1, 3)
    return vol, pts.min(axis=0), pts.max(axis=0), closed


def check_stl(side, path, wp):
    vol, lo, hi, closed = mesh_report(read_stl(path))
    want, bb = wp.val().Volume(), wp.val().BoundingBox()
    print(f"  {path.name}: {len(read_stl(path))} triangles, volume {vol:.1f} mm3, closed={closed}, "
          f"Z {lo[2]:.3f}..{hi[2]:.3f}, {hi[0] - lo[0]:.1f} x {hi[1] - lo[1]:.1f} mm")
    bad = []
    for ok, msg in [(closed, f"{path.name} is not a closed oriented mesh"),
                    (abs(vol - want) <= STL_VOLUME_TOL * want, f"{path.name} volume {vol:.1f} differs from the model {want:.1f} mm3: run stencil.py"),
                    (abs(lo[2]) < TOL and abs(hi[2] - bb.zmax) < TOL, f"{path.name} does not stand on the bed (Z 0..{bb.zmax:.2f})")]:
        if not ok:
            bad.append(f"{side}: {msg}")
    return bad


# ---------------------------------------------------------------- registration against the board STEP
def read_step(path):
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != 1:
        raise SystemExit(f"cannot read {path}")
    reader.TransferRoots()
    out, exp = [], TopExp_Explorer(reader.OneShape(), TopAbs_SOLID)
    while exp.More():
        box = Bnd_Box()
        BRepBndLib.Add_s(exp.Current(), box, False)
        x0, y0, z0, x1, y1, z1 = box.Get()
        out.append((x0, x1, y0, y1, z0, z1))
        exp.Next()
    return np.array(out)


def distance_to_parts(points, parts):
    """Distance of each point to the nearest xy bounding box of the parts (0 inside)."""
    dx = np.maximum(np.maximum(parts[None, :, 0] - points[:, None, 0], points[:, None, 0] - parts[None, :, 1]), 0)
    dy = np.maximum(np.maximum(parts[None, :, 2] - points[:, None, 1], points[:, None, 1] - parts[None, :, 3]), 0)
    return np.hypot(dx, dy).min(axis=1)


def check_skirt_clear(side, parts, board):
    """No part of the STEP may reach into the skirt: the ring around the board edge, over the skirt height."""
    p, w, t = stencil.POCKET_CLEARANCE, stencil.WALL, board["thickness"]
    z0, z1 = (t - stencil.SKIRT_H, t) if side == "top" else (0.0, stencil.SKIRT_H)
    x0, x1, y0, y1 = board["x0"], board["x1"], -board["y1"], -board["y0"]
    in_outer = (parts[:, 0] < x1 + p + w) & (parts[:, 1] > x0 - p - w) & (parts[:, 2] < y1 + p + w) & (parts[:, 3] > y0 - p - w)
    in_pocket = (parts[:, 0] >= x0 - p) & (parts[:, 1] <= x1 + p) & (parts[:, 2] >= y0 - p) & (parts[:, 3] <= y1 + p)
    hits = int((in_outer & ~in_pocket & (parts[:, 4] < z1) & (parts[:, 5] > z0)).sum())
    print(f"  skirt: {hits} parts of the STEP reach into the skirt ring")
    return [] if not hits else [f"{side}: {hits} parts of the board STEP collide with the skirt"]


def check_registration(side, face, parts, aps, board):
    """Hole centres of the stencil in its use frame, converted back to the board frame of the STEP (X = x, Y = -y)."""
    holes = np.array([(c.x, c.y) for c in (cq.Face.makeFromWires(w).Center() for w in face.innerWires())])
    mirror = board["x0"] + board["x1"]
    flipped = holes.copy()
    flipped[:, 0] = mirror - flipped[:, 0]
    mine, wrong_flip = (flipped, holes) if side == "bottom" else (holes, flipped)
    # the holes must be the exported apertures
    exported = np.array([np.mean(a["outline"], axis=0) * [1, -1] for a in aps])
    d = np.linalg.norm(mine[:, None] - exported[None], axis=2)
    names = [f"{aps[i]['ref']}.{aps[i]['pad']}" for i in d.argmin(axis=1)]
    # parts of the two faces: the PCB body and through-hole parts straddle the board and have their centre above the middle
    zc = (parts[:, 4] + parts[:, 5]) / 2
    on_top, on_bottom = parts[zc > board["thickness"]], parts[zc < 0]
    own, other = (on_top, on_bottom) if side == "top" else (on_bottom, on_top)
    dist = distance_to_parts(mine, own)
    rate = float((dist <= PAD_TOL).mean())
    controls = {"other board side": float((distance_to_parts(mine, other) <= PAD_TOL).mean()),
                "wrong flip": float((distance_to_parts(wrong_flip, own) <= PAD_TOL).mean())}
    print(f"  registration: {rate:.1%} of holes over one of {len(own)} {side} parts (within {PAD_TOL} mm); controls "
          + ", ".join(f"{k} {v:.1%}" for k, v in controls.items()) + f"; holes vs export {d.min(axis=1).max():.3f} mm")
    for i in np.where(dist > PAD_TOL)[0]:
        print(f"  note: {names[i]} is {dist[i]:.2f} mm from the nearest {side} part body in the STEP")
    bad = []
    for ok, msg in [(len(holes) == len(aps) and d.min(axis=1).max() < 0.05, "holes do not coincide with the exported apertures"),
                    (rate >= MIN_MATCH, f"only {rate:.1%} of the holes lie over a part of this side")]:
        if not ok:
            bad.append(f"{side}: {msg}")
    for k, v in controls.items():
        if v > MAX_CONTROL:
            bad.append(f"{side}: control '{k}' matches {v:.1%}: the registration test cannot tell the mapping")
    return bad


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    data = json.loads(stencil.APERTURES.read_text())
    board = data["board"]
    parts = None if "--no-step" in sys.argv else read_step(Path(args[0]) if args else BOARD_STEP)
    bad = []
    for side in ("top", "bottom"):
        aps = data[side]
        bad += check_apertures(side, aps, board)
        wp = stencil.build(side, data)
        problems, face = check_solid(side, stencil.use_orientation(wp), aps, board)
        bad += problems
        bad += check_stl(side, HERE / f"PCB_EU_stencil_{side}_print.stl", wp)
        if parts is not None:
            bad += check_skirt_clear(side, parts, board)
            bad += check_registration(side, face, parts, aps, board)
    coupon = HERE / "PCB_EU_stencil_coupon_print.stl"
    vol, lo, hi, closed = mesh_report(read_stl(coupon))
    want = stencil.coupon(data).val().Volume()
    print(f"coupon: {coupon.name}, volume {vol:.2f} mm3, closed={closed}, {hi[0] - lo[0]:.1f} x {hi[1] - lo[1]:.1f} x {hi[2]:.2f} mm")
    if not closed or abs(vol - want) > STL_VOLUME_TOL * want:
        bad.append("coupon STL is not a closed mesh or differs from the model: run stencil.py")
    for p in bad:
        print("FAIL", p)
    print("OK" if not bad else f"{len(bad)} problem(s)")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
