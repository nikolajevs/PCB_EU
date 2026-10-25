"""Add the EU-LITE ground plane and local high-current copper zones.

The pours are deliberately local around the PTC, pump, 24 V input, LED driver,
and 3.3 V converter. They supplement the routed tracks; they do not replace
current, thermal, or prototype measurements.
SPDX-License-Identifier: MIT
"""
import argparse
import math
from pathlib import Path

import pcbnew as p

from build_board import HERE, identity

MM = p.FromMM
CLEARANCE = 0.2
MIN_THICKNESS = 0.25


def route_corridor(points, half_width):
    """Return a mitered copper corridor around a non-reversing route polyline."""
    directions = []
    for a, b in zip(points, points[1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length == 0:
            raise ValueError('Route corridor has duplicate consecutive points')
        directions.append((dx / length, dy / length))

    def offset_side(sign):
        normals = [(sign * -dy, sign * dx) for dx, dy in directions]
        result = [(points[0][0] + half_width * normals[0][0],
                   points[0][1] + half_width * normals[0][1])]
        for i in range(1, len(points) - 1):
            previous, following = normals[i - 1], normals[i]
            denominator = 1 + previous[0] * following[0] + previous[1] * following[1]
            if denominator < 0.1:
                raise ValueError('Route corridor has an almost reversing corner')
            scale = half_width / denominator
            result.append((points[i][0] + scale * (previous[0] + following[0]),
                           points[i][1] + scale * (previous[1] + following[1])))
        result.append((points[-1][0] + half_width * normals[-1][0],
                       points[-1][1] + half_width * normals[-1][1]))
        return result

    return offset_side(1) + list(reversed(offset_side(-1)))


def add_zone(board, net, layer, name, points, priority=0):
    zone = p.ZONE(board)
    identity(zone, 'lite_power/zone/' + name)
    zone.SetLayer(board.GetLayerID(layer))
    zone.SetNet(board.FindNet(net))
    zone.SetLocalClearance(MM(CLEARANCE))
    zone.SetMinThickness(MM(MIN_THICKNESS))
    solid_power = {'led_feed', 'input_raw', 'pump_return', 'fused_led_feed', 'fused_pump_feed', 'fused_ptc_feed',
                   'fused_main_bus', 'return_q102_bus'}
    connection = p.ZONE_CONNECTION_FULL if name in solid_power else p.ZONE_CONNECTION_THERMAL
    zone.SetPadConnection(connection)
    zone.SetThermalReliefGap(MM(0.3))
    zone.SetThermalReliefSpokeWidth(MM(0.5 if net == 'GND' else 0.35))
    zone.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
    zone.SetAssignedPriority(priority)
    zone.SetZoneName('lite_power/' + name)
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in points:
        outline.Append(MM(x), MM(y))
    board.Add(zone)
    return zone


def add_ground_outline(board, layer, name):
    edges = board.GetBoardEdgesBoundingBox()
    left, top, right, bottom = [p.ToMM(v) for v in
                                (edges.GetLeft(), edges.GetTop(), edges.GetRight(), edges.GetBottom())]
    inset = 0.5
    return add_zone(board, 'GND', layer, name,
                    [(left+inset,top+inset),(right-inset,top+inset),
                     (right-inset,bottom-inset),(left+inset,bottom-inset)], 0)


def add_rule_keepout(board, name, layer, points):
    zone = p.ZONE(board)
    identity(zone, 'lite_power/keepout/' + name)
    zone.SetLayer(board.GetLayerID(layer))
    zone.SetIsRuleArea(True)
    zone.SetDoNotAllowTracks(False)
    zone.SetDoNotAllowVias(False)
    zone.SetDoNotAllowPads(False)
    zone.SetDoNotAllowFootprints(False)
    zone.SetDoNotAllowZoneFills(True)
    zone.SetZoneName('lite_power/keepout/' + name)
    outline = zone.Outline()
    outline.NewOutline()
    for x, y in points:
        outline.Append(MM(x), MM(y))
    board.Add(zone)
    return zone


def set_full_pad_connection(board, ref, number):
    fp = next((f for f in board.GetFootprints() if f.GetReference() == ref), None)
    if fp is None:
        raise RuntimeError(f'Cannot find footprint {ref}')
    pad = next((q for q in fp.Pads() if q.GetNumber() == number), None)
    if pad is None:
        raise RuntimeError(f'Cannot find pad {ref}.{number}')
    pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)


def add_power_zones(board):
    # Keep all GND pours clear of the INA238 IN+ Kelvin branch. It uses two
    # through vias; the plane must not join either via or the trace before the
    # R111.1 shunt pad, where the high-current return is sensed.
    for layer in ('F.Cu','In1.Cu','B.Cu'):
        add_rule_keepout(board, f'ina238_inplus_kelvin_vertical_{layer}', layer,
                         [(17.7,42.9),(18.9,42.9),(18.9,51.9),(17.7,51.9)])
        add_rule_keepout(board, f'ina238_inplus_kelvin_entry_{layer}', layer,
                         [(18.618,51.182),(19.718,52.282),(19.082,52.918),(17.982,51.818)])
    for layer, name in (('In1.Cu', 'gnd_inner'), ('F.Cu', 'gnd_top'), ('B.Cu', 'gnd_bottom')):
        add_ground_outline(board, layer, name)

    # Use direct copper on these compact SMD pins where the thermal relief was
    # starved to one spoke by the nearby zones.
    for ref, number in (('U102','2'), ('U102','7'), ('U201','2'), ('U201','4'),
                        ('U201','6'), ('U501','1'), ('U501','9'), ('D701','1'), ('Q102','2'),
                        ('Q703','2'), ('Q703','3'), ('J701','1'), ('J701','2'), ('Q102','3')):
        set_full_pad_connection(board, ref, number)

    specs = [
        ('+24V_RAW', 'F.Cu', 'input_raw',
         [(5.4,44.5),(24.0,48.8),(24.0,51.2),(5.4,47.0)], 4),
        ('PSU_RTN', 'F.Cu', 'input_return',
         [(5.4,49.4),(17.2,48.4),(17.2,53.0),(5.4,52.7)], 3),
        # Strengthen only the Q102 side of RTN_SHUNT; the existing INA238
        # Kelvin keepout separates this pour from the sense branch.
        ('RTN_SHUNT', 'F.Cu', 'return_q102_bus',
         route_corridor([(15.5,47.92),(16.817,47.92),(16.817,48.952),(17.591,49.725)], 1.5), 4),
        ('+24V_FUSED', 'F.Cu', 'input_24v',
         [(22.3,46.5),(44.5,46.5),(46.8,49.5),(45.2,56.6),(25.0,57.4),(22.3,52.2)], 2),
        # Add a 4 mm copper corridor to F103. The modeled average LED-driver
        # input current reaches about 3.9 A at 75 W, 21.6 V, and 90% efficiency.
        # The pour clips itself around the nearby D101 and LED nets.
        ('+24V_FUSED', 'F.Cu', 'fused_led_feed',
         route_corridor([(44.0,46.5),(53.35,42.15),(55.0,42.15),
                         (56.99,40.16),(56.99,35.29),(56.2,34.5)], 2.0), 3),
        # Widen the source-side segment feeding the pump fuse F105.
        ('+24V_FUSED', 'F.Cu', 'fused_pump_feed',
         route_corridor([(61.5,93.51),(70.01,85.0),(70.75,85.0)], 1.5), 3),
        # Add copper to the source-side bus from F102 toward the lower power rail.
        ('+24V_FUSED', 'F.Cu', 'fused_ptc_feed',
         route_corridor([(48.0,87.3),(48.0,88.65),(48.1,88.76),
                         (48.1,94.08),(50.13,96.11),(60.49,96.11)], 1.5), 4),
        # Follow the long fused distribution run between the input-zone branch,
        # F104 and the F105 feeder; clearances are applied during zone fill.
        ('+24V_FUSED', 'F.Cu', 'fused_main_bus',
         route_corridor([(42.93,59.06),(42.93,67.68),(43.25,68.0),
                         (45.31,70.19),(50.06,70.19),(51.36,71.5),(54.5,71.5),
                         (60.55,77.55),(75.72,77.55),(81.06,82.89),(81.06,87.12),
                         (80.46,87.72),(73.47,87.72),(70.75,85.0)], 1.5), 4),
        ('+12V', 'F.Cu', 'logic_12v',
         [(31.0,31.0),(46.8,31.0),(47.0,36.5),(42.0,36.5),(42.0,41.5),(32.0,41.5)], 2),
        ('+24V_LED', 'F.Cu', 'led_input',
         [(57.5,32.5),(62.5,32.5),(65.7,41.7),(68.0,45.5),(67.7,51.9),
          (63.8,52.6),(61.0,45.0),(57.5,39.5)], 2),
        ('+24V_LED', 'F.Cu', 'led_feed',
         [(57.4,17.8),(64.2,11.1),(66.6,13.5),(60.0,20.2),
          (60.0,34.5),(57.4,34.5)], 3),
        ('+24V_PTC', 'F.Cu', 'ptc_supply',
         [(44.0,82.5),(49.0,82.5),(49.2,95.2),(43.5,95.2)], 3),
        ('PTC_DRAIN', 'F.Cu', 'ptc_return',
         [(49.6,80.0),(56.4,80.0),(56.4,95.2),(49.6,95.2)], 3),
        ('+24V_PUMP', 'F.Cu', 'pump_supply',
         [(56.5,82.5),(80.5,82.5),(80.5,95.2),(56.5,95.2)], 3),
        ('PUMP_DRAIN', 'F.Cu', 'pump_return',
         [(58.0,81.0),(61.0,78.2),(66.5,77.5),(66.5,95.2),
          (62.5,95.2),(62.5,83.5),(58.0,84.5)], 4),
    ]
    for net, layer, name, points, priority in specs:
        add_zone(board, net, layer, name, points, priority)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--board', type=Path, default=HERE/'PCB_EU_LITE.kicad_pcb')
    args = ap.parse_args()
    if not args.board.with_suffix('.kicad_pro').exists():
        raise RuntimeError('Copy the matching .kicad_pro beside the board before zone filling')
    board = p.LoadBoard(str(args.board))
    for zone in list(board.Zones()):
        if zone.GetZoneName().startswith('lite_power/'):
            board.Delete(zone)
    add_power_zones(board)
    p.ZONE_FILLER(board).Fill(board.Zones())
    board.BuildConnectivity()
    p.SaveBoard(str(args.board), board)
    print(f'Added three ground pours and 15 local power pours; tracks/vias={len(board.GetTracks())}; '
          f'unconnected={board.GetConnectivity().GetUnconnectedCount(False)}')


if __name__ == '__main__':
    main()
