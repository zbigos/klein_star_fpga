from typing import Dict, Tuple, List
import os
import sys
import inspect
import math
from tabulate import tabulate
import collections
import statistics
# small hack to import from toplevel
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir_a = os.path.dirname(currentdir)
sys.path.insert(0, parentdir_a) 
import kicad_parser

pcb_target: str = os.path.dirname(parentdir_a) + "/hardware/klein_star_ein/klein_star_ein.kicad_pcb"
pcb = kicad_parser.KicadPCB.load(pcb_target)
# dict z element -> pinname -> [net, x, y] (globalne)
devicedict: Dict[str, Dict[str, Tuple[str, float, float]]] = {}

LAYERS = ["F.Cu", "In1.Cu", "In2.Cu", "In3.Cu", "In4.Cu", "B.Cu"]
LAYERH = {
    "F.Cu": 0.0175,
    "In1.Cu": 0.309,
    "In2.Cu": 0.618,
    "In3.Cu": 0.927,
    "In4.Cu": 1.236,
    "B.Cu": 1.545
}
VIA_PENALTY = 1.6

def i_want_to_die(rot, dx, dy):
    rot = math.radians(rot)
    fx = dx * math.cos(rot) - dy * math.sin(rot)
    fy = dx * math.sin(rot) + dy * math.cos(rot)
    return (fx, fy)

for f in pcb.footprint:
    footprint_designator = None
    for q in f.fp_text:
        if "SilkS" in q.layer:
            footprint_designator = q[1][1:-1]
    if not footprint_designator:
        print("no designator, failing hard")
        exit(1)

    devicedict[footprint_designator] = {}
    dev_x = f.at[0]
    dev_y = f.at[1]
    if len(f.at) == 3:
        dev_rot = f.at[2]
    else:
        dev_rot = 0

    if f.layer == '"B.Cu"': # -135 > -45 (+90)
        dev_rot += 90

    for p in f.pad:
        if p[0] != '""':
            if len(p.at) == 3:
                ppx, ppy, pprot = p.at
            else:
                ppx, ppy = p.at
                pprot = 0
            pinnet = p.net if "net" in p else "NC"
            rotx, roty = i_want_to_die(dev_rot, ppx, ppy)
            fin_x = round(rotx + dev_x, 3)
            fin_y = round(roty + dev_y, 3)
            devicedict[footprint_designator][p[0][1:-1]] = (pinnet[1][1:-1], fin_x, fin_y, p.layers[0][1:-1])

print(len(devicedict.items()), "devices loaded")

netddict: Dict[int, str] = {}
for n in pcb.net:
    netddict[int(n[0])] = n[1][1:-1]

print(len(netddict.items()), "nets loaded")

viadict: Dict[Tuple[float, float], int] = {}
for v in pcb.via:
    viadict[(v.at[0], v.at[1])] = v.net

print(len(viadict.items()), "vias loaded")

segmentdict = collections.defaultdict(lambda: set())
for s in pcb.segment:
    segmentdict[s.net].add((tuple(s.start), tuple(s.end), s.width, s.layer))

print(len(segmentdict.items()), "segments loaded")

arcdict = collections.defaultdict(lambda: set())
for s in pcb.arc:
    arcdict[s.net].add((tuple(s.start), tuple(s.mid), tuple(s.end), s.width, s.layer))

print(len(arcdict.items()), "arcs loaded")

def length(pa, pb):
    return ((pa[0] - pb[0])**2.0 + (pa[1] - pb[1])**2.0)**0.5

def define_circle(p1, p2, p3):
    """
    Returns the center and radius of the circle passing the given 3 points.
    In case the 3 points form a line, returns (None, infinity).
    """
    temp = p2[0] * p2[0] + p2[1] * p2[1]
    bc = (p1[0] * p1[0] + p1[1] * p1[1] - temp) / 2
    cd = (temp - p3[0] * p3[0] - p3[1] * p3[1]) / 2
    det = (p1[0] - p2[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p2[1])

    if abs(det) < 1.0e-6:
        return (None, np.inf)

    # Center of circle
    cx = (bc*(p2[1] - p3[1]) - cd*(p1[1] - p2[1])) / det
    cy = ((p1[0] - p2[0]) * cd - (p2[0] - p3[0]) * bc) / det

    radius = ((cx - p1[0])**2 + (cy - p1[1])**2)**0.5
    return ((cx, cy), radius)

def arc_length(pa, pm, pb): # znam trzy punkty
    (ccx, ccy), rad = define_circle(pa, pm, pb)
    ta = (pa[0] - ccx, pa[1] - ccy)
    tm = (pm[0] - ccx, pm[1] - ccy)
    tb = (pb[0] - ccx, pb[1] - ccy)
    am_angle = math.atan2(ta[1], ta[0]) - math.atan2(tm[1], tm[0])
    bm_angle = math.atan2(tb[1], tb[0]) - math.atan2(tm[1], tm[0])
    ab_angle = math.atan2(ta[1], ta[0]) - math.atan2(tb[1], tb[0])

    amd = math.degrees(am_angle)
    bmd = math.degrees(bm_angle)
    abd = math.degrees(ab_angle)
    
    if amd < 0.0:
        amd += 360.0
    if bmd < 0.0:
        bmd += 360.0
    if abd < 0.0:
        abd += 360.0

    asol = [amd, 360 - amd]
    bsol = [bmd, 360 - bmd]
    csol = [abd, 360 - abd]
    solutions = []
    for a in asol:
        for b in bsol:
            for c in csol:
                if abs(a+b - c) < 0.00001:
                    solutions.append((a, b, c))

    if len(solutions) > 1:
        print(solutions)
        exit(1)

    if len(solutions) == 0:
        print(solutions)
        exit(1)

    return math.radians(solutions[0][2]) * rad    

class Board:
    def __init__(self, devices, nets, vias, segments, arcs):
        self.devices = devices
        self.nets = nets
        self.vias = vias
        self.segments = segments
        self.arcs = arcs
        self.matchrules = []
        self.solutions = {}

    def add_matchrule(self, matchrule):
        self.matchrules.append(matchrule)

    def ask_matchrules(self):
        for mr in self.matchrules:
            for requirement in mr.registered_nets:
                net, dev1, dev2 = requirement
                if (net, dev1, dev2) in self.solutions:
                    mr.registered_nets[(net, dev1, dev2)] = self.solutions[(net, dev1, dev2)]
                if (net, dev2, dev1) in self.solutions:
                    mr.registered_nets[(net, dev1, dev2)] = self.solutions[(net, dev2, dev1)]

            mr.validate()

    def extract_requests(self) -> List[Tuple[str, str, str]]:
        requests = []
        for mr in self.matchrules:
            for arch in mr.registered_nets:
                requests.append(arch)
        return requests
    
    def record_solution(self, netname, device1, device2, cl):
        self.solutions[(netname, device1, device2)] = cl

    def calculate_distance(self, netname, device1, device2):
        dev1_pindata = []
        dev2_pindata = []
        
        for pin, data in self.devices[device1].items():
            if netname == data[0]:
                dev1_pindata.append((data[1], data[2], data[3]))
        for pin, data in self.devices[device2].items():
            if netname == data[0]:
                dev2_pindata.append((data[1], data[2], data[3]))

        if len(dev1_pindata) != 1 or len(dev2_pindata) != 1:
            print(dev1_pindata, dev2_pindata)
            print("failing hard")
            exit(1)

        BFS_reachability = {dev1_pindata[0]}
        BFS_costmap: Dict[Tuple[float, float], float] = {}
        BFS_costmap[dev1_pindata[0]] = 0.0
        BFS_epoch = 0
        last_BFS_power = 0
        while True:
            for net in self.segments.items():
                if(self.nets[net[0]] == netname):
                    for segment in net[1]:
                        sp = (segment[0][0], segment[0][1], segment[3][1:-1])
                        se = (segment[1][0], segment[1][1], segment[3][1:-1])
                        if sp in BFS_reachability:
                            BFS_reachability.add(se)
                            if (se not in BFS_costmap) or (BFS_costmap[sp] + length(se, sp) < BFS_costmap[se]):
                                BFS_costmap[se] = BFS_costmap[sp] + length(se, sp)
                        if se in BFS_reachability:
                            BFS_reachability.add(sp)
                            if (sp not in BFS_costmap) or (BFS_costmap[se] + length(se, sp) < BFS_costmap[sp]):
                                BFS_costmap[sp] = BFS_costmap[se] + length(se, sp)
            
            for vpos, vnet in self.vias.items():
                if self.nets[vnet] == netname:
                    via_origin = None
                    for l in LAYERS:
                        nvia = (vpos[0], vpos[1], l)
                        if nvia in BFS_reachability:
                            via_origin = nvia

                    if via_origin:
                        for l in LAYERS:
                            nvia = (vpos[0], vpos[1], l)
                            BFS_reachability.add(nvia)
                            via_penalty = abs(LAYERH[l] - LAYERH[via_origin[2]])
                            if (nvia not in BFS_costmap) or (BFS_costmap[via_origin] + via_penalty) < BFS_costmap[nvia]:
                                BFS_costmap[nvia] = BFS_costmap[via_origin] + via_penalty

            for anet, adata in self.arcs.items():
                if self.nets[anet] == netname:
                    for archchunk in adata:
                        sp = (archchunk[0][0], archchunk[0][1], archchunk[4][1:-1])
                        sm = (archchunk[1][0], archchunk[1][1])
                        se = (archchunk[2][0], archchunk[2][1], archchunk[4][1:-1])
                        if sp in BFS_reachability:
                            BFS_reachability.add(se)
                            if (se not in BFS_costmap) or (BFS_costmap[sp] + arc_length(se, sm, sp) < BFS_costmap[se]):
                                BFS_costmap[se] = BFS_costmap[sp] + arc_length(se, sm, sp)
                        if se in BFS_reachability:
                            BFS_reachability.add(sp)
                            if (sp not in BFS_costmap) or (BFS_costmap[se] + arc_length(se, sm, sp) < BFS_costmap[sp]):
                                BFS_costmap[sp] = BFS_costmap[se] + arc_length(se, sm, sp)

            if len(BFS_reachability) != last_BFS_power:
                last_BFS_power = len(BFS_reachability)
                BFS_epoch += 1
            else:
                break
        
        distmap = [(BFS_costmap[k], k) for k in BFS_costmap.keys()]
        if dev2_pindata[0] in BFS_costmap:
            return BFS_costmap[dev2_pindata[0]]
        else:
            for d, v in BFS_costmap.items():
                propd = (d[0], d[1])
                print(d, v, length(propd, dev2_pindata[0]))
            raise RuntimeError()

board = Board(devicedict, netddict, viadict, segmentdict, arcdict)

class matchrule:
    def __init__(self, board, name):
        self.registered_nets = {}
        self.required_length = None
        self.required_deviation = None
        self.boardref = board
        self.name = name

    def validate(self):
        print(f"========== {self.name} ==========")            
        for reqnet, netlen in self.registered_nets.items():
            if netlen is None:
                print(f"{reqnet} NOT ROUTED!")
                exit(1)

        distances = list(self.registered_nets.values())
        if not self.required_length:
            self.required_length = round(statistics.mean(distances), 3)
            print(f"no required length provided, using mean {self.required_length}")

        info = {
            'signal': [],
            'from': [],
            'to': [],
            'length': [],
            'deviation': []
        }

        for mrk, mrv in self.registered_nets.items():
            info['signal'].append(mrk[0])
            info['from'].append(mrk[1])
            info['to'].append(mrk[2])
            info['length'].append(mrv)
            info['deviation'].append(mrv - self.required_length)

        print(tabulate(info, headers='keys'))

    def register_net(self, net: str, device1: str, device2: str):
        for pin, data in self.boardref.devices[device1].items():
            if net == data[0]:
                break
        else:
            print(f"no net {net} in {device1} failing hard")
            exit(1)

        for pin, data in self.boardref.devices[device2].items():
            if net == data[0]:
                break
        else:
            print(f"no net {net} in {device2} failing hard")
            exit(1)

        self.registered_nets[(net, device1, device2)] = None

    def __str__(self):
        return f"match {self.registered_nets}"


## FPGA to DRAM bank 1 matchrules.
DQ0_matchrule = matchrule(board, "DQ0 matchrule")
for datapin in range(0, 8):
    DQ0_matchrule.register_net(f"/DRAM_DATA_{datapin}", "U2", "U1")
DQ0_matchrule.register_net(f"/DRAM_DQS0_P", "U2", "U1")
DQ0_matchrule.register_net(f"/DRAM_DQS0_N", "U2", "U1")
DQ0_matchrule.register_net(f"/DRAM_DM0", "U2", "U1")
board.add_matchrule(DQ0_matchrule)

DQ1_matchrule = matchrule(board, "DQ1 matchrule")
for datapin in range(8, 16):
    DQ1_matchrule.register_net(f"/DRAM_DATA_{datapin}", "U2", "U1")
DQ1_matchrule.register_net(f"/DRAM_DQS1_P", "U2", "U1")
DQ1_matchrule.register_net(f"/DRAM_DQS1_N", "U2", "U1")
DQ1_matchrule.register_net(f"/DRAM_DM1", "U2", "U1")
board.add_matchrule(DQ1_matchrule)

DQ2_matchrule = matchrule(board, "DQ2 matchrule")
for datapin in range(16, 24):
    DQ2_matchrule.register_net(f"/DRAM_DATA_{datapin}", "U3", "U1")
DQ2_matchrule.register_net(f"/DRAM_DQS2_P", "U3", "U1")
DQ2_matchrule.register_net(f"/DRAM_DQS2_N", "U3", "U1")
DQ2_matchrule.register_net(f"/DRAM_DM2", "U3", "U1")
board.add_matchrule(DQ2_matchrule)

DQ3_matchrule = matchrule(board, "DQ3 matchrule")
for datapin in range(24, 32):
    DQ3_matchrule.register_net(f"/DRAM_DATA_{datapin}", "U3", "U1")
DQ3_matchrule.register_net(f"/DRAM_DQS3_P", "U3", "U1")
DQ3_matchrule.register_net(f"/DRAM_DQS3_N", "U3", "U1")
DQ3_matchrule.register_net(f"/DRAM_DM3", "U3", "U1")
board.add_matchrule(DQ3_matchrule)


U2_CMD_matchrule = matchrule(board, "CMD U2 matchrule")
for addrpin in range(0, 16):
    U2_CMD_matchrule.register_net(f"/DRAM_ADDR_{addrpin}", "U2", "U1")
for bapin in range(0, 3):
    U2_CMD_matchrule.register_net(f"/DRAM_ADDR_BA{bapin}", "U2", "U1")


U2_CMD_matchrule.register_net(f"/DRAM_CLK_P", "U2", "U1")
U2_CMD_matchrule.register_net(f"/DRAM_CLK_N", "U2", "U1")
U2_CMD_matchrule.register_net(f"/DRAM_CKE", "U2", "U1")

U2_CMD_matchrule.register_net(f"/DRAM_nRAS", "U2", "U1")
U2_CMD_matchrule.register_net(f"/DRAM_nCAS", "U2", "U1")
U2_CMD_matchrule.register_net(f"/DRAM_nWE", "U2", "U1")
U2_CMD_matchrule.register_net(f"/DRAM_nCS", "U2", "U1")
U2_CMD_matchrule.register_net(f"/DRAM_nRESET", "U2", "U1")

#U2_CMD_matchrule.register_net(f"/DRAM_ODT", "U2", "U1")
board.add_matchrule(U2_CMD_matchrule)

U3_CMD_matchrule = matchrule(board, "CMD U3 matchrule")
for addrpin in range(0, 16):
    U3_CMD_matchrule.register_net(f"/DRAM_ADDR_{addrpin}", "U3", "U1")
for bapin in range(0, 3):
    U3_CMD_matchrule.register_net(f"/DRAM_ADDR_BA{bapin}", "U3", "U1")


U3_CMD_matchrule.register_net(f"/DRAM_CLK_P", "U3", "U1")
U3_CMD_matchrule.register_net(f"/DRAM_CLK_N", "U3", "U1")
U3_CMD_matchrule.register_net(f"/DRAM_CKE", "U3", "U1")

U3_CMD_matchrule.register_net(f"/DRAM_nRAS", "U3", "U1")
U3_CMD_matchrule.register_net(f"/DRAM_nCAS", "U3", "U1")
U3_CMD_matchrule.register_net(f"/DRAM_nWE", "U3", "U1")
U3_CMD_matchrule.register_net(f"/DRAM_nCS", "U3", "U1")
U3_CMD_matchrule.register_net(f"/DRAM_nRESET", "U3", "U1")

#U2_CMD_matchrule.register_net(f"/DRAM_ODT", "U2", "U1")
board.add_matchrule(U3_CMD_matchrule)


reqs = board.extract_requests()
for r in reqs:
    print(r)
    cl = board.calculate_distance(*r)
    board.record_solution(*r, cl)

board.ask_matchrules()