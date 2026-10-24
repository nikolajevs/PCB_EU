"""Create the unrouted EU-LITE board from the EU-0.1 placement and the EU-LITE netlist (KiCad Python).

  kicad-cli sch export netlist --format kicadxml -o netlist.xml hardware/PCB_EU_LITE/PCB_EU_LITE.kicad_sch
  "C:/Program Files/KiCad/10.0/bin/python.exe" hardware/PCB_EU_LITE/tools/build_board.py netlist.xml

Starting point is the EU-0.1 board (../PCB_EU/PCB_EU.kicad_pcb) with all copper (tracks, vias, zones)
removed; stack-up, 100x100 mm outline and silk stay, matching the owner's decision (25.10.2026) to keep
EU-0.1's board size and 4-layer JLC04161H-7628 stack. Every footprint is synchronised with the netlist
like "Update PCB from Schematic":
  * references that no longer exist are removed (the 63 EU-0.1-only parts: second LED channel,
    tachometers, UVLO comparator, ESD protection, ...);
  * a footprint whose library id changed is replaced in place (position, rotation and side kept) —
    this covers the 73 common refs whose footprint shrank or changed package (ST1S14/ST1S10, BSC146N10LS5,
    SBRT15U100SP5, Phoenix terminal blocks, ...);
  * the 28 refs with no EU-0.1 counterpart (RGB status indicator and its passives) are parked in a
    staging grid outside the board outline — they still need real placement;
  * values, fields, schematic paths and pad nets are refreshed from the netlist.
The EU-0.1 mounting holes (H1-H4, board-only, no nets) are kept as-is. The EU-0.1 heatsink legs
footprint (HS1) is dropped: EU-LITE's LED and PTC switches have no heatsink (owner decision, DESIGN.md).
Writes hardware/PCB_EU_LITE/PCB_EU_LITE.kicad_pcb and refuses to overwrite a board that has copper.

CAUTION (observed 25.10.2026): loading the EU-0.1 board from a different project directory has, at
least once, left PCB_EU_LITE.kicad_pro rewritten with EU-0.1's own project settings (wrong top-level
schematic, wrong DESIGN_STAGE, EU-0.1 net classes) after a later `kicad-cli pcb drc` / `sch erc` run
against the new board — root cause not isolated. Always `git diff hardware/PCB_EU_LITE/PCB_EU_LITE.kicad_pro`
after running this script or any kicad-cli command against its output, and `git checkout --` it if it
was touched; nothing in EU-LITE's own project identity should ever come from PCB_EU's.
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pcbnew as p

HERE = Path(__file__).resolve().parents[1]
SOURCE = HERE.parent / 'PCB_EU' / 'PCB_EU.kicad_pcb'
OUT = HERE / 'PCB_EU_LITE.kicad_pcb'
STOCK = Path(os.environ.get('KICAD10_FOOTPRINT_DIR', r'C:\Program Files\KiCad\10.0\share\kicad\footprints'))
LOCAL_LIBS = {
    'EU_Mechanical': HERE.parent / 'PCB_EU' / 'libraries' / 'EU_Mechanical.pretty',
    'EU_Parts': HERE.parent / 'PCB_EU' / 'libraries' / 'EU_Parts.pretty',
    'LITE_Parts': HERE / 'libraries' / 'LITE_Parts.pretty',
}
BOARD_ONLY_KEEP = {'H1', 'H2', 'H3', 'H4'}  # EU-0.1 mounting holes: no nets, not in the netlist, kept as-is
BOARD_ONLY_DROP = {'HS1'}  # EU-0.1 heatsink legs: EU-LITE has no heatsink (DESIGN.md)

netlist = Path(sys.argv[1])
if OUT.exists():
    old = p.LoadBoard(str(OUT))
    if len(old.GetTracks()) or old.GetAreaCount():
        raise SystemExit('PCB_EU_LITE.kicad_pcb already has copper: not overwriting')

board = p.LoadBoard(str(SOURCE))
GRAVEYARD = []  # removed items stay referenced: destroying their Python proxies breaks later pcbnew calls
for item in list(board.GetTracks()) + list(board.Zones()):
    board.Remove(item)
    GRAVEYARD.append(item)
for ref in BOARD_ONLY_DROP:
    item = board.FindFootprintByReference(ref)
    if item is not None:
        board.Delete(item)


def lib_id(fp):
    fpid = fp.GetFPID()
    return f'{fpid.GetLibNickname()}:{fpid.GetLibItemName()}'


def load(fpid):
    nick, name = fpid.split(':', 1)
    lib = LOCAL_LIBS.get(nick, STOCK / f'{nick}.pretty')
    fp = p.FootprintLoad(str(lib), name)
    assert fp, f'footprint not found: {fpid} (looked in {lib})'
    fp.SetFPID(p.LIB_ID(nick, name))
    return fp


root = ET.parse(netlist).getroot()
comps = {c.get('ref'): c for c in root.findall('./components/comp')}
root_uuid = re.search(r'\(uuid "([^"]+)"', (HERE / 'PCB_EU_LITE.kicad_sch').read_text(encoding='utf-8')).group(1)

existing = {f.GetReference() for f in board.GetFootprints()} - BOARD_ONLY_KEEP - BOARD_ONLY_DROP
staging_x, staging_y = 115.0, 0.0  # parking lot for the 28 refs with no EU-0.1 counterpart; outside 100x100
removed = sorted(ref for ref in existing if ref not in comps)
for ref in removed:
    item = board.FindFootprintByReference(ref)
    board.Delete(item)
added, replaced, slot = [], [], 0
for ref, comp in sorted(comps.items()):
    fpid = comp.findtext('footprint')
    old = board.FindFootprintByReference(ref) if ref in existing else None
    if old is None or lib_id(old) != fpid:
        fp = load(fpid)
        fp.SetReference(ref)
        board.Add(fp)  # Flip needs the board's layer stack: add before flipping
        if old is not None:
            pos, orient, flipped = p.VECTOR2I(old.GetPosition()), old.GetOrientation(), old.IsFlipped()
            board.Delete(old)
            fp.SetPosition(pos)
            if flipped:
                fp.Flip(pos, False)
            fp.SetOrientation(orient)
            replaced.append(ref)
        else:
            fp.SetPosition(p.VECTOR2I(p.FromMM(staging_x + (slot % 6) * 15), p.FromMM(staging_y + (slot // 6) * 15)))
            slot += 1
            added.append(ref)
    fp = board.FindFootprintByReference(ref)
    fp.SetReference(ref)
    fp.SetValue(comp.findtext('value'))
    fields = {f.get('name'): f.text or '' for f in comp.findall('fields/field')}
    metadata = {k: fields.get(k, '') for k in ('Manufacturer', 'MPN', 'LCSC', 'Source')}
    metadata['Datasheet'] = comp.findtext('datasheet', '')
    for key, value in metadata.items():
        if value or fp.HasField(key):
            fp.SetField(key, value)
            fp.GetField(key).SetVisible(False)
    path = p.KIID_PATH()
    for u in [root_uuid] + [u for u in comp.find('sheetpath').get('tstamps').split('/') if u] + [comp.findtext('tstamps')]:
        path.push_back(p.KIID(u))
    fp.SetPath(path)

fps = {f.GetReference(): f for f in board.GetFootprints() if f.GetReference() not in BOARD_ONLY_KEEP}
for fp in fps.values():
    for pad in fp.Pads():
        pad.SetNetCode(0)
used = set()
for net in root.findall('./nets/net'):
    name = net.get('name')
    info = board.FindNet(name)
    if info is None:
        info = p.NETINFO_ITEM(board, name)
        board.Add(info)
    used.add(name)
    for node in net.findall('node'):
        pads = [pad for pad in fps[node.get('ref')].Pads() if pad.GetNumber() == node.get('pin')]
        assert pads, (node.attrib, 'missing footprint pad')
        for pad in pads:
            pad.SetNet(info)
stale = [n for n in list(board.GetNetsByName().keys()) if str(n) and str(n) not in used]
for name in stale:
    board.Remove(board.FindNet(str(name)))

tb = board.GetTitleBlock()
tb.SetRevision('EU-LITE-0.1-DRAFT')
tb.SetDate('2026-10-25')
board.SetTitleBlock(tb)

p.SaveBoard(str(OUT), board)
check = p.LoadBoard(str(OUT))
assert {f.GetReference() for f in check.GetFootprints()} == set(comps) | BOARD_ONLY_KEEP
print(f'Removed {len(removed)}: {" ".join(removed)}')
print(f'Replaced {len(replaced)}: {" ".join(replaced)}')
print(f'Added {len(added)} (staged outside the outline, need real placement): {" ".join(added)}')
print(f'Dropped {len(stale)} stale nets; board has {len(comps)} netlisted footprints + {len(BOARD_ONLY_KEEP)} mounting holes, no copper')
