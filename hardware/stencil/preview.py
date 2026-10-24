"""PNG preview of a stencil in the use orientation, drawn from the built solid (imported by stencil.py)."""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.collections import PolyCollection  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402


def render(side, wp, board, path):
    import stencil
    face = stencil.squeegee_face(stencil.use_orientation(wp))
    verts, tris = face.tessellate(0.002, 0.1)
    polys = [[(verts[i].x, verts[i].y) for i in t] for t in tris]
    fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
    ax.add_collection(PolyCollection(polys, facecolors="#8fb8d9", edgecolors="#8fb8d9", linewidths=0.2))
    ax.add_patch(Rectangle((board["x0"], -board["y1"]), board["x1"] - board["x0"], board["y1"] - board["y0"],
                           fill=False, ec="#c0392b", lw=0.8, ls="--"))
    ax.set_aspect("equal")
    ax.autoscale()
    ax.set_title(f"PCB_EU stencil, {side}: squeegee side up, as laid on the board (board outline dashed)", fontsize=8)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
