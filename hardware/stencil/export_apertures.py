#!/usr/bin/env python3
"""Export the solder-paste apertures of PCB_EU.kicad_pcb to apertures.json (input of stencil.py); SPDX-License-Identifier: MIT.

Run it with the Python that ships with KiCad (it needs `pcbnew`, nothing else):
    "C:/Program Files/KiCad/10.0/bin/python.exe" hardware/stencil/export_apertures.py [board.kicad_pcb]

Every pad that sits on F.Paste or B.Paste becomes one aperture, taken from KiCad's own effective paste polygon
(so the footprint paste margins, the split thermal-pad windows and the global paste margin are already applied).
Coordinates are KiCad board coordinates in mm (x right, y down), as stored in the PCB; stencil.py flips y and mirrors
the bottom side.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pcbnew

HERE = Path(__file__).resolve().parent
BOARD = HERE.parent / "PCB_EU" / "PCB_EU.kicad_pcb"
OUT = HERE / "apertures.json"


def ring(chain):
    return [[round(pcbnew.ToMM(chain.CPoint(i).x), 4), round(pcbnew.ToMM(chain.CPoint(i).y), 4)]
            for i in range(chain.PointCount())]


def apertures(board, layer):
    out = []
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if not pad.IsOnLayer(layer):
                continue
            poly = pad.GetEffectivePolygon(layer)
            for i in range(poly.OutlineCount()):
                out.append({
                    "ref": fp.GetReference(),
                    "pad": pad.GetNumber(),
                    "outline": ring(poly.COutline(i)),
                    "holes": [ring(poly.CHole(i, k)) for k in range(poly.HoleCount(i))],
                })
    out.sort(key=lambda a: (a["ref"], a["pad"], a["outline"][0]))
    return out


def outline_box(board):
    """Board outline along the centre lines of the Edge.Cuts segments (must be a plain rectangle)."""
    xs, ys = [], []
    for d in board.GetDrawings():
        if d.GetLayer() != pcbnew.Edge_Cuts:
            continue
        if d.GetShapeStr() != "Line":
            raise SystemExit(f"Edge.Cuts has a {d.GetShapeStr()}: stencil.py supports a rectangular outline only")
        if d.GetStart().x != d.GetEnd().x and d.GetStart().y != d.GetEnd().y:
            raise SystemExit("Edge.Cuts has a slanted line: stencil.py supports a rectangular outline only")
        for pt in (d.GetStart(), d.GetEnd()):
            xs.append(pcbnew.ToMM(pt.x))
            ys.append(pcbnew.ToMM(pt.y))
    return {"x0": round(min(xs), 4), "y0": round(min(ys), 4), "x1": round(max(xs), 4), "y1": round(max(ys), 4)}


def dump(data):
    """One aperture per line keeps the file small and the diffs readable."""
    rows = {k: "[\n" + ",\n".join(" " + json.dumps(a, separators=(",", ":")) for a in data[k]) + "\n ]"
            for k in ("top", "bottom")}
    head = json.dumps({k: v for k, v in data.items() if k not in rows}, indent=1)
    return head[:-2] + ",\n" + ",\n".join(f' "{k}": {v}' for k, v in rows.items()) + "\n}\n"


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else BOARD
    board = pcbnew.LoadBoard(str(path))
    data = {
        "source": f"{path.name}, KiCad {pcbnew.Version()}",
        "units": "mm, KiCad board coordinates (y down)",
        "board": dict(outline_box(board), thickness=round(pcbnew.ToMM(board.GetDesignSettings().GetBoardThickness()), 4)),
        "top": apertures(board, pcbnew.F_Paste),
        "bottom": apertures(board, pcbnew.B_Paste),
    }
    OUT.write_text(dump(data), newline="\n")
    print(f"{OUT}: top {len(data['top'])}, bottom {len(data['bottom'])} apertures, board {data['board']}")


if __name__ == "__main__":
    main()
