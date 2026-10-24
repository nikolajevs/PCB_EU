#!/usr/bin/env python3
"""Interference and clearance check of the enclosure against the PCB_EU STEP export (OCP + CadQuery).

Usage:  python hardware/enclosure/check_enclosure.py [board.step] [--fast]
        (default: hardware/PCB_EU/review/PCB_EU_assembly.step)
Run it in the CadQuery environment. Board parts that cannot come within the report margin of the shell
(bounding box test against walls, ceiling, floor, ledge blocks, bosses and button tubes) are skipped; the
rest get an exact overlap and distance test and the closest ones are listed (--fast: only parts closer
than MIN_CLEARANCE). Exit code 1 on interference or a clearance below MIN_CLEARANCE.

The board STEP does not contain the heatsink HS1, so it is added here as a keep-out block taken from
placement.json (heatsink_legs.body_box: x 68..98, y 24.05..39.05 KiCad; 30 mm tall over the 0.3 mm pad).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from OCP.BRepAlgoAPI import BRepAlgoAPI_Common
from OCP.BRepBndLib import BRepBndLib
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepGProp import BRepGProp
from OCP.Bnd import Bnd_Box
from OCP.GProp import GProp_GProps
from OCP.STEPControl import STEPControl_Reader
from OCP.TopAbs import TopAbs_SOLID
from OCP.TopExp import TopExp_Explorer

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import enclosure as enc  # noqa: E402

BOARD_STEP = HERE.parent / "PCB_EU" / "review" / "PCB_EU_assembly.step"
HS1_BOX = (68.0, 98.0, 24.05, 39.05)     # KiCad x0, x1, y0, y1
MIN_CLEARANCE = 0.5      # mm, any board part to the shell (the bare board edge is 0.4 mm by design)
REPORT_MARGIN = 2.5      # mm, parts closer than this are listed
OVERLAP_TOL = 1e-3       # mm3 of overlap treated as numerical noise


def read_step(path):
    reader = STEPControl_Reader()
    if reader.ReadFile(str(path)) != 1:
        raise SystemExit(f"cannot read {path}")
    reader.TransferRoots()
    return reader.OneShape()


def solids(shape):
    out = []
    exp = TopExp_Explorer(shape, TopAbs_SOLID)
    while exp.More():
        out.append(exp.Current())
        exp.Next()
    return out


def bbox(shape):
    box = Bnd_Box()
    BRepBndLib.Add_s(shape, box, False)
    x0, y0, z0, x1, y1, z1 = box.Get()
    return x0, x1, y0, y1, z0, z1


def volume(shape):
    props = GProp_GProps()
    BRepGProp.VolumeProperties_s(shape, props)
    return props.Mass()


def common_volume(a, b):
    return volume(BRepAlgoAPI_Common(a, b).Shape())


def box_hits(a, b, margin):
    return a[0] < b[1] + margin and a[1] > b[0] - margin and a[2] < b[3] + margin and a[3] > b[2] - margin \
        and a[4] < b[5] + margin and a[5] > b[4] - margin


def feature_boxes():
    """Bounding boxes of everything that reaches into the cavity."""
    out = []
    for side, c in enc.LEDGES:
        bb = enc.wall_box(side, c - enc.LEDGE_L / 2, c + enc.LEDGE_L / 2, enc.T, enc.T + enc.LEDGE_W,
                          enc.Z_FLOOR, enc.Z_LEDGE).val().BoundingBox()
        out.append((bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax))
    r = enc.BOSS_OD / 2
    for kx, ky in enc.HOLES:
        out.append((kx - r, kx + r, -ky - r, -ky + r, enc.Z_FLOOR, enc.Z_LEDGE))
    for bx, by, _ in enc.BUTTONS:
        r = enc.TUBE_OD / 2
        out.append((bx - r, bx + r, -by - r, -by + r, enc.TUBE_BOT, enc.Z_CEIL))
    return out


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    board_step = Path(args[0]) if args else BOARD_STEP
    t0 = time.time()
    board = solids(read_step(board_step))
    base, lid = read_step(HERE / "PCB_EU_base.step"), read_step(HERE / "PCB_EU_lid.step")
    print(f"board solids: {len(board)}  (read {time.time() - t0:.0f} s)", flush=True)
    bad = 0

    vol = common_volume(base, lid)
    print(f"base and lid overlap: {vol:.4f} mm3", flush=True)
    bad += vol > OVERLAP_TOL

    cavity = (enc.IX0, enc.IX1, enc.IY0, enc.IY1, enc.Z_FLOOR, enc.Z_CEIL)
    feats = feature_boxes()
    m = MIN_CLEARANCE if "--fast" in sys.argv else REPORT_MARGIN
    rows, tested = [], 0
    hx0, hx1, hy0, hy1 = HS1_BOX
    hs1 = enc.kbox(hx0, hx1, hy0, hy1, enc.BOARD_TOP + 0.3, enc.HS1_TOP).val().wrapped
    parts = [(s, False) for s in board] + [(hs1, True)]
    for s, is_hs1 in parts:
        bb = bbox(s)
        inside = (bb[0] >= cavity[0] + m and bb[1] <= cavity[1] - m and bb[2] >= cavity[2] + m and bb[3] <= cavity[3] - m
                  and bb[4] >= cavity[4] + m and bb[5] <= cavity[5] - m)
        if inside and not any(box_hits(bb, f, m) for f in feats):
            continue
        tested += 1
        for name, shell in (("base", base), ("lid", lid)):
            if common_volume(s, shell) > OVERLAP_TOL:
                tag = "HS1 " if is_hs1 else ""
                print(f"INTERFERENCE {tag}with {name}: x {bb[0]:.2f}..{bb[1]:.2f} y {bb[2]:.2f}..{bb[3]:.2f} z {bb[4]:.2f}..{bb[5]:.2f}",
                      flush=True)
                bad += 1
                continue
            dist = BRepExtrema_DistShapeShape(s, shell)
            if dist.IsDone():
                rows.append((dist.Value(), name + (" (HS1)" if is_hs1 else ""), bb))
    print(f"{len(parts) - tested} board parts cannot reach the shell, {tested} tested exactly ({time.time() - t0:.0f} s)")
    rows.sort(key=lambda r: r[0])
    print("closest board parts (distance, shell part, bounding box):")
    for d, name, bb in rows[:16]:
        print(f"  {d:5.2f} mm  {name:9s} x {bb[0]:.1f}..{bb[1]:.1f} y {bb[2]:.1f}..{bb[3]:.1f} z {bb[4]:.2f}..{bb[5]:.2f}")
    # the bare PCB sits on the ledge blocks and the bosses by design
    for d, name, bb in rows:
        pcb = bb[4] < 0.01 and bb[5] < 1.61 and bb[1] - bb[0] > 90
        if d < MIN_CLEARANCE - 1e-6 and not pcb:
            print(f"TOO CLOSE {d:.2f} mm to {name}: x {bb[0]:.2f}..{bb[1]:.2f} y {bb[2]:.2f}..{bb[3]:.2f} z {bb[4]:.2f}..{bb[5]:.2f}")
            bad += 1
    print("OK" if not bad else f"{bad} problem(s)")
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    main()
