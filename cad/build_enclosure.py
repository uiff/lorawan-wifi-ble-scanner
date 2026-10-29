"""Parametric FreeCAD enclosure for the Heltec WiFi LoRa 32 V2 LoRaWAN Network Finder (Rev. 5).

Improvements in Rev. 5 based on hardware build feedback:
  1. IoTUeli Logo + Button Symbols (‹ • ›) integrated as 0.60 mm flush multi-color inlays
     on the front face of TopCover (Gehaeuse_Oben) above the OLED window.
  2. Multi-color Bambu Lab .3mf export (Extruder 1 = Enclosure Body, Extruder 2 = IoTUeli Logo + Button Labels).
  3. Removed underside ribs on TopCover (hold_rib_top & hold_rib_bot_l) that collided with
     top-soldered GPIO wires and PCB components; added extra wire clearance channel under TopCover.
  4. Added wide open wire pass-through channels (Durchgang) in BottomShell under the ESP32
     towards both the 3 tactile switches (-Y) and the power switch (+Y) so pre-soldered wires
     drop straight in while keeping solid corner & rear (J=47.80..52.00 mm) PCB ledges.
  5. Extended the top antenna bay (+Y) by +8.0 mm (to Y = +47.0 mm) and opened the internal
     U.FL-to-SMA routing zone so the 18 mm SMA bulkhead + heatshrink boot + coax cable fit effortlessly.
"""

import json
import math
import os
import zipfile
from PIL import Image

import FreeCAD as App
import Mesh
import MeshPart
import Part

V = App.Vector
ROOT = r"C:\Users\uiff\Documents\coding\ESP_LoraWan_Finder"
CAD_DIR = os.path.join(ROOT, "cad")
EXPORT_DIR = os.path.join(CAD_DIR, "export")
FCSTD_PATH = os.path.join(CAD_DIR, "LoraWanFinder.FCStd")
LOGO_PNG_PATH = os.path.join(ROOT, "assets", "iotueli-logo.png")

# ----------------------------------------------------------------------
# 1. Main Enclosure Dimensions (mm)
#    Bottom edge stays at Y_MIN_OUT = -39.0 mm; Top edge extended by +8.0 mm
#    to Y_MAX_OUT = +47.0 mm (total length L_OUT = 86.0 mm, center Y_BOX_CENTER = +4.0 mm)
#    for spacious SMA antenna routing and the IoTUeli logo above the OLED!
# ----------------------------------------------------------------------
W_OUT = 66.0          # X width (-33.0 .. +33.0) -> inner X: -30.6 .. +30.6 (61.2 mm)
Y_MIN_OUT = -39.0
Y_MAX_OUT = 47.0
L_OUT = Y_MAX_OUT - Y_MIN_OUT              # 86.0 mm
Y_BOX_CENTER = (Y_MIN_OUT + Y_MAX_OUT) / 2.0  # +4.0 mm

H_TOTAL = 23.2        # Total Z height (0.0 .. 23.2 mm, calibrated to G=7.0 so OLED sits flush!)
Z_SPLIT = 17.5        # Split plane between BottomShell and TopCover
R_CORNER = 6.5        # Outer XY corner fillet radius
CHAMFER_OUT = 1.0     # Top/bottom outer edge bevel
WALL = 2.4            # Perimeter wall thickness
FLOOR = 2.0           # Bottom floor thickness
ROOF = 1.4            # Top cover roof thickness above OLED glass (21.8 .. 23.2 mm)
INLAY_DEPTH = 0.60    # 3 layers at 0.20 mm for crisp 2-color AMS printing

# Interlocking lip at Z_SPLIT
LIP_H = 1.6           # Lip height into TopCover
LIP_W = 1.1           # Lip wall thickness
LIP_CLEAR = 0.25      # Radial clearance between lip and TopCover recess

# ----------------------------------------------------------------------
# 2. Heltec WiFi LoRa 32 V2 PCB Dimensions & Placement (from A..N)
# ----------------------------------------------------------------------
PCB_L = 52.00         # A: 52.00 mm
PCB_W = 25.33         # B: 25.33 mm
PCB_T = 1.60          # Standard PCB thickness
PCB_CLEAR_X = 0.35    # Axial pocket clearance
PCB_CLEAR_Y = 0.30    # Lateral pocket clearance

X_PCB_MIN = -30.40
X_PCB_MAX = X_PCB_MIN + PCB_L            # +21.60 mm

# With Y_MAX_OUT = +47.0 mm (inner wall at +44.60 mm), Y_PCB_MAX = +17.20 mm leaves
# a full 27.40 mm of open space in the +Y bay for the 18 mm SMA connector + coax loop!
Y_PCB_MAX = 17.20
Y_PCB_MIN = Y_PCB_MAX - PCB_W            # -8.13 mm
Y_PCB_CENTER = (Y_PCB_MIN + Y_PCB_MAX) / 2.0   # +4.535 mm

Z_PCB_BOT = 14.80     # Underside of PCB
Z_PCB_TOP = Z_PCB_BOT + PCB_T            # 16.40 mm
Z_OLED_TOP = Z_PCB_BOT + 7.00            # G = 7.00 mm -> 21.80 mm

# OLED Frame & Visible Window (from C, D, E, J, M, N):
PCB_STRAIGHT_J = 47.80
X_J = X_PCB_MIN + PCB_STRAIGHT_J         # +17.40 mm
X_FRAME_MAX = X_J                        # +17.40 mm
X_FRAME_MIN = X_FRAME_MAX - 33.07        # -15.67 mm
X_OLED_CENTER = (X_FRAME_MIN + X_FRAME_MAX) / 2.0   # +0.865 mm

Y_FRAME_MIN = Y_PCB_CENTER - 18.63 / 2.0   # -4.78 mm
Y_FRAME_MAX = Y_PCB_CENTER + 18.63 / 2.0   # +13.85 mm
Y_VIS_MIN = Y_FRAME_MAX - 14.74            # -0.89 mm
Y_VIS_MAX = Y_FRAME_MAX                    # +13.85 mm
Y_OLED_WIN_CENTER = (Y_VIS_MIN + Y_VIS_MAX) / 2.0   # +6.48 mm

RIBBON_PROTRUSION_Y = 0.576
RIBBON_WIDTH_X = 14.40

OLED_WIN_W = 27.6
OLED_WIN_H = 14.8
OLED_POCKET_CLEAR = 0.65

# Onboard PRG and RST buttons (K = 3.33 mm, L = 4.34 mm)
X_PRG_RST = X_PCB_MIN + 3.33
Y_PRG = Y_PCB_MAX - 4.34
Y_RST = Y_PCB_MIN + 4.34

# Micro-USB cutout (-X wall)
Z_USB_CENTER = Z_PCB_TOP + 1.4
USB_OPEN_Y = 9.2
USB_OPEN_Z = 4.6
USB_RECESS_Y = 15.0
USB_RECESS_Z = 9.6
USB_RECESS_DEPTH = 1.3

# ----------------------------------------------------------------------
# 3. 3x 6x6mm Tactile Buttons (‹, ●, ›) in Thumb Zone
# ----------------------------------------------------------------------
TACT_BODY = 6.0
TACT_POCKET = 6.30
TACT_BODY_H = 2.9
TACT_STEM_H = 1.5
TACT_STEM_D = 3.5
TACT_TOTAL_H = TACT_BODY_H + TACT_STEM_H   # 4.40 mm

Y_BTN = -23.5
BTN_XS = (-15.0, 0.0, 15.0)
Z_TACT_FLOOR = 13.0
Z_TACT_ACTUATOR = Z_TACT_FLOOR + TACT_TOTAL_H   # 17.40 mm

CAP_D = 8.4
CAP_HOLE_D = 8.9
CAP_FLANGE_D = 11.2
CAP_FLANGE_H = 1.4
Z_CAP_BOT = Z_TACT_ACTUATOR + 0.05   # 17.45 mm
Z_CAP_TOP = H_TOTAL + 1.6            # 24.80 mm

# ----------------------------------------------------------------------
# 4. SMA Bulkhead Antenna & Slide Switch on Top Wall (+Y = Y_MAX_OUT)
# ----------------------------------------------------------------------
X_SMA = 13.0
Z_SMA = 11.0
SMA_HOLE_D = 6.7      # Generous clearance for SMA thread
SMA_HEX_AF = 8.4      # Generous hex pocket
SMA_WALL_T = 2.0

X_SW = -13.0
Z_SW = 11.0
SW_SLOT_X = 6.0
SW_SLOT_Z = 3.2
SW_BODY_X = 9.4
SW_BODY_Z = 4.8
SW_WALL_T = 1.4

# ----------------------------------------------------------------------
# 5. Battery Compartment (LiPo up to 50 x 24 x 10 mm)
# ----------------------------------------------------------------------
BAT_L = 50.0
BAT_W = 22.0
BAT_H = 10.0
Y_BAT_CENTER = Y_PCB_CENTER

# ----------------------------------------------------------------------
# 6. Corner Screw Bosses (4x M3 Heat-Set Inserts, Ø 4.0 x 7.0 mm)
# ----------------------------------------------------------------------
BOSS_R = 4.0
INSERT_M3_D = 4.0
INSERT_M3_DEPTH = 7.0
SCREW_CLEAR_D = 3.4
SCREW_HEAD_D = 6.2
CORNER_XY = [
    (-W_OUT / 2 + R_CORNER, Y_MIN_OUT + R_CORNER),
    ( W_OUT / 2 - R_CORNER, Y_MIN_OUT + R_CORNER),
    (-W_OUT / 2 + R_CORNER, Y_MAX_OUT - R_CORNER),
    ( W_OUT / 2 - R_CORNER, Y_MAX_OUT - R_CORNER),
]


def rounded_rect_wire(w, l, r, z=0.0, cy=Y_BOX_CENTER):
    hw, hl = w / 2.0, l / 2.0
    y0, y1 = cy - hl, cy + hl
    r = min(r, hw - 0.05, hl - 0.05)
    if r <= 0.05:
        pts = [V(-hw, y0, z), V(hw, y0, z), V(hw, y1, z), V(-hw, y1, z), V(-hw, y0, z)]
        return Part.makePolygon(pts)

    c = math.cos(math.pi / 4.0)
    edges = []
    p1 = V(-hw + r, y0, z)
    p2 = V( hw - r, y0, z)
    p3 = V( hw, y0 + r, z)
    p4 = V( hw, y1 - r, z)
    p5 = V( hw - r, y1, z)
    p6 = V(-hw + r, y1, z)
    p7 = V(-hw, y1 - r, z)
    p8 = V(-hw, y0 + r, z)

    edges.append(Part.LineSegment(p1, p2).toShape())
    edges.append(Part.Arc(p2, V(hw - r + r * c, y0 + r - r * c, z), p3).toShape())
    edges.append(Part.LineSegment(p3, p4).toShape())
    edges.append(Part.Arc(p4, V(hw - r + r * c, y1 - r + r * c, z), p5).toShape())
    edges.append(Part.LineSegment(p5, p6).toShape())
    edges.append(Part.Arc(p6, V(-hw + r - r * c, y1 - r + r * c, z), p7).toShape())
    edges.append(Part.LineSegment(p7, p8).toShape())
    edges.append(Part.Arc(p8, V(-hw + r - r * c, y0 + r - r * c, z), p1).toShape())
    return Part.Wire(edges)


def rounded_prism(w, l, h, r, z0=0.0, cy=Y_BOX_CENTER):
    face = Part.Face(rounded_rect_wire(w, l, r, z0, cy))
    return face.extrude(V(0, 0, h))


def beveled_outer_blank():
    c = CHAMFER_OUT
    w0 = rounded_rect_wire(W_OUT - 2 * c, L_OUT - 2 * c, R_CORNER - c, 0.0)
    w1 = rounded_rect_wire(W_OUT, L_OUT, R_CORNER, c)
    w2 = rounded_rect_wire(W_OUT, L_OUT, R_CORNER, H_TOTAL - c)
    w3 = rounded_rect_wire(W_OUT - 2 * c, L_OUT - 2 * c, R_CORNER - c, H_TOTAL)

    bot = Part.makeLoft([w0, w1], True, True)
    mid = rounded_prism(W_OUT, L_OUT, H_TOTAL - 2 * c, R_CORNER, c)
    top = Part.makeLoft([w2, w3], True, True)
    return bot.fuse(mid).fuse(top)


def hex_prism_y(cx, cz, y0, length, across_flats):
    r_circ = across_flats / math.sqrt(3.0)
    pts = []
    for i in range(6):
        ang = math.radians(i * 60.0 + 30.0)
        pts.append(V(cx + r_circ * math.cos(ang), y0, cz + r_circ * math.sin(ang)))
    pts.append(pts[0])
    face = Part.Face(Part.makePolygon(pts))
    return face.extrude(V(0, length, 0))


def pill_2d(p1, p2, r, z0, h):
    dx, dy = p2.x - p1.x, p2.y - p1.y
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = -uy * r, ux * r
    box_pts = [
        V(p1.x + nx, p1.y + ny, z0),
        V(p2.x + nx, p2.y + ny, z0),
        V(p2.x - nx, p2.y - ny, z0),
        V(p1.x - nx, p1.y - ny, z0),
        V(p1.x + nx, p1.y + ny, z0),
    ]
    bar = Part.Face(Part.makePolygon(box_pts)).extrude(V(0, 0, h))
    c1 = Part.makeCylinder(r, h, V(p1.x, p1.y, z0))
    c2 = Part.makeCylinder(r, h, V(p2.x, p2.y, z0))
    return bar.fuse(c1).fuse(c2)


def build_button_symbols(z_top, depth=INLAY_DEPTH):
    """Create sleek hardware markers (‹  •  ›) above the 3 buttons."""
    y_sym = Y_BTN + 8.2   # -15.3 mm
    z0 = z_top - depth
    h = depth
    r_stroke = 0.60

    cx1 = BTN_XS[0]
    chev_l1 = pill_2d(V(cx1 - 1.3, y_sym), V(cx1 + 1.3, y_sym + 2.1), r_stroke, z0, h)
    chev_l2 = pill_2d(V(cx1 - 1.3, y_sym), V(cx1 + 1.3, y_sym - 2.1), r_stroke, z0, h)
    left_sym = chev_l1.fuse(chev_l2)

    cx2 = BTN_XS[1]
    mid_sym = Part.makeCylinder(1.7, h, V(cx2, y_sym, z0))

    cx3 = BTN_XS[2]
    chev_r1 = pill_2d(V(cx3 + 1.3, y_sym), V(cx3 - 1.3, y_sym + 2.1), r_stroke, z0, h)
    chev_r2 = pill_2d(V(cx3 + 1.3, y_sym), V(cx3 - 1.3, y_sym - 2.1), r_stroke, z0, h)
    right_sym = chev_r1.fuse(chev_r2)

    return left_sym.fuse(mid_sym).fuse(right_sym).removeSplitter()


def build_iotueli_logo_3d(cx=0.0, cy=28.0, target_w=42.0, z_top=H_TOTAL, depth=INLAY_DEPTH):
    """Vectorize assets/iotueli-logo.png into a crisp 3D inlay solid on TopCover above the display."""
    raw = Image.open(LOGO_PNG_PATH)
    alpha = raw.split()[3]
    w, h = 290, 96
    im = alpha.resize((w, h), Image.Resampling.BILINEAR)
    px = im.load()

    edges = {}
    for y in range(h):
        for x in range(w):
            if px[x, y] > 128:
                for p1, p2 in [
                    ((x, y), (x + 1, y)),
                    ((x + 1, y), (x + 1, y + 1)),
                    ((x + 1, y + 1), (x, y + 1)),
                    ((x, y + 1), (x, y)),
                ]:
                    rev = (p2, p1)
                    if rev in edges:
                        del edges[rev]
                    else:
                        edges[(p1, p2)] = True

    adj = {}
    for p1, p2 in edges:
        adj.setdefault(p1, []).append(p2)

    loops = []
    while adj:
        start = next(iter(adj))
        loop = [start]
        curr = start
        while True:
            nxts = adj.get(curr, [])
            if not nxts:
                break
            nxt = nxts.pop()
            if not nxts:
                del adj[curr]
            if nxt == start:
                break
            loop.append(nxt)
            curr = nxt
        if len(loop) >= 6:
            loops.append(loop)

    scale = target_w / float(w)
    z0 = z_top - depth

    solids_pos = []
    solids_neg = []
    for loop in loops:
        simp = []
        n = len(loop)
        for i in range(n):
            p_prev = loop[(i - 1) % n]
            p_curr = loop[i]
            p_next = loop[(i + 1) % n]
            if (p_curr[0] - p_prev[0]) * (p_next[1] - p_curr[1]) != (p_curr[1] - p_prev[1]) * (p_next[0] - p_curr[0]):
                simp.append(p_curr)
        area2 = 0.0
        m = len(simp)
        for i in range(m):
            x1, y1 = simp[i]
            x2, y2 = simp[(i + 1) % m]
            area2 += x1 * y2 - x2 * y1
        pts_3d = [V(cx + (x - w / 2.0) * scale, cy + (h / 2.0 - y) * scale, z0) for (x, y) in simp]
        pts_3d.append(pts_3d[0])
        wire = Part.makePolygon(pts_3d)
        prism = Part.Face(wire).extrude(V(0, 0, depth))
        if area2 > 0:
            solids_pos.append((abs(area2), prism))
        else:
            solids_neg.append((abs(area2), prism))

    solids_pos.sort(key=lambda t: t[0], reverse=True)
    solids_neg.sort(key=lambda t: t[0], reverse=True)

    badge = solids_pos[0][1]
    for _, hole in solids_neg:
        badge = badge.cut(hole)
    for _, island in solids_pos[1:]:
        badge = badge.fuse(island)
    return badge


def make_heltec_pcb_shape(clr=0.0, z0=Z_PCB_BOT, h=PCB_T):
    """Exact 10-vertex polygon of the Heltec WiFi LoRa 32 V2 PCB from user photo & measurements A..N."""
    x0 = X_PCB_MIN - clr
    x_chamf_l = X_PCB_MIN + 1.80 - clr * 0.4
    x_j = X_PCB_MIN + PCB_STRAIGHT_J + clr
    x1 = X_PCB_MAX + clr
    y0 = Y_PCB_MIN - clr
    y1 = Y_PCB_MAX + clr
    yf0 = Y_FRAME_MIN - clr
    yf1 = Y_FRAME_MAX + clr
    chamf_r = 4.20

    pts = [
        V(x0, y0 + 1.80, z0),
        V(x_chamf_l, y0, z0),
        V(x_j, y0, z0),
        V(x_j, yf0, z0),
        V(x1, yf0 + chamf_r, z0),
        V(x1, yf1 - chamf_r, z0),
        V(x_j, yf1, z0),
        V(x_j, y1, z0),
        V(x_chamf_l, y1, z0),
        V(x0, y1 - 1.80, z0),
        V(x0, y0 + 1.80, z0),
    ]
    return Part.Face(Part.makePolygon(pts)).extrude(V(0, 0, h))


def build_bottom_shell(outer_blank):
    """Build BottomShell with wide wire pass-through channels (Durchgang) and spacious +Y antenna bay."""
    box_bot = Part.makeBox(W_OUT + 10, L_OUT + 10, Z_SPLIT, V(-W_OUT / 2 - 5, Y_MIN_OUT - 5, 0))
    shell = outer_blank.common(box_bot)

    lip_outer = rounded_prism(
        W_OUT - 2 * (WALL - LIP_W),
        L_OUT - 2 * (WALL - LIP_W),
        LIP_H,
        R_CORNER - (WALL - LIP_W),
        Z_SPLIT,
    )
    lip_inner = rounded_prism(
        W_OUT - 2 * WALL,
        L_OUT - 2 * WALL,
        LIP_H + 0.2,
        R_CORNER - WALL,
        Z_SPLIT - 0.1,
    )
    shell = shell.fuse(lip_outer.cut(lip_inner))

    cavity = rounded_prism(
        W_OUT - 2 * WALL,
        L_OUT - 2 * WALL,
        Z_SPLIT + LIP_H + 1.0,
        R_CORNER - WALL,
        FLOOR,
    )
    shell = shell.cut(cavity)

    # 2. Add 4 corner screw bosses (from FLOOR up to Z_SPLIT)
    for cx, cy in CORNER_XY:
        boss = Part.makeCylinder(BOSS_R, Z_SPLIT - FLOOR, V(cx, cy, FLOOR))
        shell = shell.fuse(boss)
    shell = shell.common(
        outer_blank.fuse(
            Part.makeBox(W_OUT, L_OUT, LIP_H + 1, V(-W_OUT / 2, Y_MIN_OUT, Z_SPLIT))
        )
    )

    # 3. Heltec V2 PCB Cradle with WIDE WIRE PASS-THROUGH CHANNELS ("Durchgang"):
    #    - Solid support at left end (X = X_PCB_MIN .. X_PCB_MIN + 8.5 mm)
    #    - Solid continuous support at right end ("o": X = X_PCB_MIN + 41.0 .. 52.0 mm,
    #      including the 90° step at J = 47.80 mm and 45° angled V2 tab!)
    #    - Wide 26.0 mm open wire pass-through (X = -18.0 .. +8.0 mm) through both the
    #      lower rail (-Y towards buttons) and upper rail (+Y towards switch/antenna)
    #      so wires can be routed cleanly underneath the ESP32!
    wall_h = PCB_T + 1.0

    base_support = make_heltec_pcb_shape(clr=PCB_CLEAR_X + 2.0, z0=FLOOR, h=Z_PCB_BOT - FLOOR)
    inner_cav_main = Part.makeBox(
        39.3,
        PCB_W - 2 * 1.65,
        Z_PCB_BOT - FLOOR + 1.0,
        V(X_PCB_MIN + 5.2, Y_PCB_MIN + 1.65, FLOOR - 0.5),
    )
    inner_cav_usb = Part.makeBox(
        7.0,
        14.0,
        Z_PCB_BOT - FLOOR + 1.0,
        V(X_PCB_MIN - 1.0, Y_PCB_CENTER - 7.0, FLOOR - 0.5),
    )
    # Wide 26.0 mm open wire pass-through channel ("Durchgang") under both -Y and +Y PCB rails!
    wire_pass_through = Part.makeBox(
        26.0,
        PCB_W + 10.0,
        Z_PCB_BOT - FLOOR + 1.0,
        V(-18.0, Y_PCB_MIN - 5.0, FLOOR - 0.5),
    )
    # Additional lower antenna coax clearance tunnel in front of SMA (X = +6..+20, Y = Y_FRAME_MAX..Y_PCB_MAX+4, Z = FLOOR..Z_PCB_BOT-2.0)
    # Leaves a 2.0 mm thick upper PCB support shelf at Z = 12.8..14.8 mm while clearing Z_SMA = 11.0 mm completely!
    sma_coax_tunnel = Part.makeBox(
        14.0,
        10.0,
        (Z_PCB_BOT - 2.0) - FLOOR + 0.5,
        V(6.0, Y_FRAME_MAX - 1.0, FLOOR - 0.5),
    )
    base_support = base_support.cut(inner_cav_main).cut(inner_cav_usb).cut(wire_pass_through).cut(sma_coax_tunnel)

    # Upper perimeter retaining wall from Z_PCB_BOT (14.80) to Z_PCB_TOP + 1.0 (17.40)
    rim_outer = make_heltec_pcb_shape(clr=PCB_CLEAR_X + 2.0, z0=Z_PCB_BOT, h=wall_h)
    rim_inner = make_heltec_pcb_shape(clr=PCB_CLEAR_X, z0=Z_PCB_BOT - 0.1, h=wall_h + 0.5)
    rim_wall = rim_outer.cut(rim_inner)

    usb_rim_open = Part.makeBox(
        4.0,
        14.0,
        wall_h + 1.0,
        V(X_PCB_MIN - 3.0, Y_PCB_CENTER - 7.0, Z_PCB_BOT - 0.2),
    )
    # Wide wire pass-through opening in rim_wall matching the lower tunnel (X = -18.0 .. +8.0 mm)
    wire_rim_open = Part.makeBox(
        26.0,
        PCB_W + 10.0,
        wall_h + 1.0,
        V(-18.0, Y_PCB_MIN - 5.0, Z_PCB_BOT - 0.2),
    )
    # Spacious U.FL antenna pigtail exit on the right V2 tip & upper-right corner towards SMA
    ufl_rim_open = Part.makeBox(
        8.0,
        14.0,
        wall_h + 1.0,
        V(X_J - 1.0, Y_PCB_CENTER - 2.0, Z_PCB_BOT - 0.2),
    )
    rim_wall = rim_wall.cut(usb_rim_open).cut(wire_rim_open).cut(ufl_rim_open)

    shell = shell.fuse(base_support).fuse(rim_wall)
    shell = shell.common(
        outer_blank.fuse(
            Part.makeBox(W_OUT, L_OUT, LIP_H + 1, V(-W_OUT / 2, Y_MIN_OUT, Z_SPLIT))
        )
    )

    # 4. Build the 3x 6x6mm Tactile Switch Cradle Deck in the thumb zone (Y_BTN = -23.5)
    cradle_w = 45.0
    cradle_l = 10.4
    z_cradle_bot = Z_TACT_FLOOR - 1.8   # 11.2 mm
    z_cradle_top = Z_TACT_FLOOR + TACT_BODY_H - 0.1   # 15.8 mm
    cradle = Part.makeBox(
        cradle_w,
        cradle_l,
        z_cradle_top - z_cradle_bot,
        V(-cradle_w / 2.0, Y_BTN - cradle_l / 2.0, z_cradle_bot),
    )
    for sx in (-21.0, -7.5, 7.5, 18.0):
        leg = Part.makeBox(3.0, cradle_l, z_cradle_bot - FLOOR, V(sx, Y_BTN - cradle_l / 2.0, FLOOR))
        cradle = cradle.fuse(leg)

    for bx in BTN_XS:
        pkt = Part.makeBox(
            TACT_POCKET,
            TACT_POCKET,
            10.0,
            V(bx - TACT_POCKET / 2.0, Y_BTN - TACT_POCKET / 2.0, Z_TACT_FLOOR),
        )
        pin_slot_l = Part.makeBox(
            2.0,
            TACT_POCKET + 1.0,
            Z_TACT_FLOOR - z_cradle_bot + 1.0,
            V(bx - TACT_POCKET / 2.0 - 0.2, Y_BTN - (TACT_POCKET + 1.0) / 2.0, z_cradle_bot - 0.5),
        )
        pin_slot_r = Part.makeBox(
            2.0,
            TACT_POCKET + 1.0,
            Z_TACT_FLOOR - z_cradle_bot + 1.0,
            V(bx + TACT_POCKET / 2.0 - 1.8, Y_BTN - (TACT_POCKET + 1.0) / 2.0, z_cradle_bot - 0.5),
        )
        cradle = cradle.cut(pkt).cut(pin_slot_l).cut(pin_slot_r)

    shell = shell.fuse(cradle)

    # 5. Cutouts in BottomShell:
    for cx, cy in CORNER_XY:
        hole = Part.makeCylinder(
            INSERT_M3_D / 2.0,
            INSERT_M3_DEPTH,
            V(cx, cy, Z_SPLIT - INSERT_M3_DEPTH + 0.01),
        )
        lead_in = Part.makeCone(
            INSERT_M3_D / 2.0,
            INSERT_M3_D / 2.0 + 0.4,
            0.4,
            V(cx, cy, Z_SPLIT - 0.39),
        )
        shell = shell.cut(hole).cut(lead_in)

    # 5b. SMA Bulkhead Connector on +Y Top Wall (Y = Y_MAX_OUT = +47.0 mm)
    sma_cyl = Part.makeCylinder(
        SMA_HOLE_D / 2.0,
        12.0,
        V(X_SMA, Y_MAX_OUT - 8.0, Z_SMA),
        V(0, 1, 0),
    )
    sma_hex = hex_prism_y(X_SMA, Z_SMA, Y_MAX_OUT - 10.0, 10.0 - SMA_WALL_T, SMA_HEX_AF)
    sma_outer_flat = Part.makeCylinder(
        5.8,
        4.0,
        V(X_SMA, Y_MAX_OUT - 0.1, Z_SMA),
        V(0, 1, 0),
    )
    shell = shell.cut(sma_cyl).cut(sma_hex).cut(sma_outer_flat)

    # 5c. Slide Switch cutout on +Y Top Wall (Y = Y_MAX_OUT = +47.0 mm)
    sw_slot = Part.makeBox(
        SW_SLOT_X,
        10.0,
        SW_SLOT_Z,
        V(X_SW - SW_SLOT_X / 2.0, Y_MAX_OUT - 5.0, Z_SW - SW_SLOT_Z / 2.0),
    )
    sw_inner_recess = Part.makeBox(
        SW_BODY_X,
        WALL - SW_WALL_T + 2.0,
        SW_BODY_Z,
        V(X_SW - SW_BODY_X / 2.0, Y_MAX_OUT - WALL - 1.0, Z_SW - SW_BODY_Z / 2.0),
    )
    shell = shell.cut(sw_slot).cut(sw_inner_recess)

    # 5d. Micro-USB port opening & cable overmold recess on -X Wall
    usb_hole = Part.makeBox(
        10.0,
        USB_OPEN_Y,
        USB_OPEN_Z,
        V(-W_OUT / 2.0 - 2.0, Y_PCB_CENTER - USB_OPEN_Y / 2.0, Z_USB_CENTER - USB_OPEN_Z / 2.0),
    )
    usb_recess = Part.makeBox(
        USB_RECESS_DEPTH + 1.0,
        USB_RECESS_Y,
        USB_RECESS_Z,
        V(-W_OUT / 2.0 - 1.0, Y_PCB_CENTER - USB_RECESS_Y / 2.0, Z_USB_CENTER - USB_RECESS_Z / 2.0),
    )
    shell = shell.cut(usb_hole).cut(usb_recess)

    return shell


def build_top_cover_and_inlay(outer_blank):
    """Build TopCover (Color 1) + flush 0.60 mm Inlay for IoTUeli Logo & Button Labels (Color 2)."""
    box_top = Part.makeBox(
        W_OUT + 10,
        L_OUT + 10,
        H_TOTAL - Z_SPLIT + 2.0,
        V(-W_OUT / 2 - 5, Y_MIN_OUT - 5, Z_SPLIT),
    )
    cover = outer_blank.common(box_top)

    cavity = rounded_prism(
        W_OUT - 2 * WALL,
        L_OUT - 2 * WALL,
        H_TOTAL - ROOF - Z_SPLIT + 0.5,
        R_CORNER - WALL,
        Z_SPLIT - 0.5,
    )
    cover = cover.cut(cavity)

    lip_groove = rounded_prism(
        W_OUT - 2 * (WALL - LIP_W - LIP_CLEAR),
        L_OUT - 2 * (WALL - LIP_W - LIP_CLEAR),
        LIP_H + 0.3,
        R_CORNER - (WALL - LIP_W - LIP_CLEAR),
        Z_SPLIT - 0.1,
    )
    cover = cover.cut(lip_groove)

    for cx, cy in CORNER_XY:
        boss = Part.makeCylinder(
            BOSS_R,
            H_TOTAL - ROOF - (Z_SPLIT + 0.2),
            V(cx, cy, Z_SPLIT + 0.2),
        )
        cover = cover.fuse(boss)
    lip_outer_clear = rounded_prism(
        W_OUT - 2 * (WALL - LIP_W - LIP_CLEAR),
        L_OUT - 2 * (WALL - LIP_W - LIP_CLEAR),
        LIP_H + 0.3,
        R_CORNER - (WALL - LIP_W - LIP_CLEAR),
        Z_SPLIT - 0.1,
    )
    lip_inner_clear = rounded_prism(
        W_OUT - 2 * (WALL + LIP_CLEAR),
        L_OUT - 2 * (WALL + LIP_CLEAR),
        LIP_H + 0.5,
        R_CORNER - (WALL + LIP_CLEAR),
        Z_SPLIT - 0.2,
    )
    cover = cover.cut(lip_outer_clear.cut(lip_inner_clear))

    # NOTE: Removed hold_rib_top and hold_rib_bot_l completely!
    # The user soldered GPIO wires on top of the ESP32 pin header rows, so the underside
    # of TopCover above the PCB pin rows stays 100% open with > 5.4 mm vertical clearance!

    # 4. Precision Stepped Display & Ribbon Pocket in the underside of TopCover
    clr = OLED_POCKET_CLEAR
    z_pocket_top = H_TOTAL - 0.65
    oled_module_pocket = Part.makeBox(
        33.07 + 2 * clr,
        18.63 + 2 * clr,
        z_pocket_top - (H_TOTAL - ROOF - 1.0),
        V(X_FRAME_MIN - clr, Y_FRAME_MIN - clr, H_TOTAL - ROOF - 1.0),
    )
    ribbon_pocket_w = RIBBON_WIDTH_X + 3.0
    ribbon_pocket_y0 = Y_FRAME_MIN - RIBBON_PROTRUSION_Y - 1.2
    ribbon_pocket = Part.makeBox(
        ribbon_pocket_w,
        (Y_VIS_MIN + 1.0) - ribbon_pocket_y0,
        (H_TOTAL - 0.60) - (H_TOTAL - ROOF - 1.0),
        V(X_OLED_CENTER - ribbon_pocket_w / 2.0, ribbon_pocket_y0, H_TOTAL - ROOF - 1.0),
    )

    # 5. Guide sleeves around the 3 tactile button holes
    z_sleeve_bot = Z_CAP_BOT + CAP_FLANGE_H + 0.5   # 18.40 mm
    for bx in BTN_XS:
        sleeve = Part.makeCylinder(
            CAP_HOLE_D / 2.0 + 1.8,
            H_TOTAL - ROOF - z_sleeve_bot,
            V(bx, Y_BTN, z_sleeve_bot),
        )
        cover = cover.fuse(sleeve)

    # 6. OLED Viewing Window
    oled_cut = Part.makeBox(
        OLED_WIN_W,
        OLED_WIN_H,
        10.0,
        V(X_OLED_CENTER - OLED_WIN_W / 2.0, Y_OLED_WIN_CENTER - OLED_WIN_H / 2.0, H_TOTAL - ROOF - 1.0),
    )
    bezel_z0 = H_TOTAL - 0.70
    bezel_z1 = H_TOTAL + 0.1
    bw0 = Part.makePolygon([
        V(X_OLED_CENTER - OLED_WIN_W / 2.0, Y_OLED_WIN_CENTER - OLED_WIN_H / 2.0, bezel_z0),
        V(X_OLED_CENTER + OLED_WIN_W / 2.0, Y_OLED_WIN_CENTER - OLED_WIN_H / 2.0, bezel_z0),
        V(X_OLED_CENTER + OLED_WIN_W / 2.0, Y_OLED_WIN_CENTER + OLED_WIN_H / 2.0, bezel_z0),
        V(X_OLED_CENTER - OLED_WIN_W / 2.0, Y_OLED_WIN_CENTER + OLED_WIN_H / 2.0, bezel_z0),
        V(X_OLED_CENTER - OLED_WIN_W / 2.0, Y_OLED_WIN_CENTER - OLED_WIN_H / 2.0, bezel_z0),
    ])
    bw1 = Part.makePolygon([
        V(X_OLED_CENTER - OLED_WIN_W / 2.0 - 0.9, Y_OLED_WIN_CENTER - OLED_WIN_H / 2.0 - 0.9, bezel_z1),
        V(X_OLED_CENTER + OLED_WIN_W / 2.0 + 0.9, Y_OLED_WIN_CENTER - OLED_WIN_H / 2.0 - 0.9, bezel_z1),
        V(X_OLED_CENTER + OLED_WIN_W / 2.0 + 0.9, Y_OLED_WIN_CENTER + OLED_WIN_H / 2.0 + 0.9, bezel_z1),
        V(X_OLED_CENTER - OLED_WIN_W / 2.0 - 0.9, Y_OLED_WIN_CENTER + OLED_WIN_H / 2.0 + 0.9, bezel_z1),
        V(X_OLED_CENTER - OLED_WIN_W / 2.0 - 0.9, Y_OLED_WIN_CENTER - OLED_WIN_H / 2.0 - 0.9, bezel_z1),
    ])
    bezel_loft = Part.makeLoft([bw0, bw1], True, True)
    cover = cover.cut(oled_module_pocket).cut(ribbon_pocket).cut(oled_cut).cut(bezel_loft)

    # 7. 3x Button Cap through-holes (Ø 8.9 mm)
    for bx in BTN_XS:
        b_hole = Part.makeCylinder(CAP_HOLE_D / 2.0, 10.0, V(bx, Y_BTN, z_sleeve_bot - 1.0))
        cover = cover.cut(b_hole)

    # 8. Pinhole access for onboard PRG and RST buttons
    for py in (Y_PRG, Y_RST):
        ph = Part.makeCylinder(1.3, 10.0, V(X_PRG_RST, py, H_TOTAL - ROOF - 2.0))
        cone = Part.makeCone(1.3, 2.2, 1.0, V(X_PRG_RST, py, H_TOTAL - 1.0))
        cover = cover.cut(ph).cut(cone)

    # 9. 4x Corner screw clearance holes + countersinks for M3 screws
    for cx, cy in CORNER_XY:
        sh = Part.makeCylinder(SCREW_CLEAR_D / 2.0, 15.0, V(cx, cy, Z_SPLIT - 1.0))
        cs = Part.makeCone(SCREW_CLEAR_D / 2.0, SCREW_HEAD_D / 2.0, 1.8, V(cx, cy, H_TOTAL - 1.8))
        cb = Part.makeCylinder(SCREW_HEAD_D / 2.0, 2.0, V(cx, cy, H_TOTAL - 0.5))
        cover = cover.cut(sh).cut(cs).cut(cb)

    # 10. Micro-USB top clearance notch & cable recess on -X Wall
    usb_hole = Part.makeBox(
        10.0,
        USB_OPEN_Y,
        USB_OPEN_Z,
        V(-W_OUT / 2.0 - 2.0, Y_PCB_CENTER - USB_OPEN_Y / 2.0, Z_USB_CENTER - USB_OPEN_Z / 2.0),
    )
    usb_recess = Part.makeBox(
        USB_RECESS_DEPTH + 1.0,
        USB_RECESS_Y,
        USB_RECESS_Z,
        V(-W_OUT / 2.0 - 1.0, Y_PCB_CENTER - USB_RECESS_Y / 2.0, Z_USB_CENTER - USB_RECESS_Z / 2.0),
    )
    cover = cover.cut(usb_hole).cut(usb_recess)

    # 11. Build 2-Color Flush Inlay (IoTUeli Logo at Y = +28.5 mm above Display + Button Symbols ‹ • ›)
    logo_3d = build_iotueli_logo_3d(cx=0.0, cy=28.5, target_w=42.0, z_top=H_TOTAL, depth=INLAY_DEPTH)
    btn_sym_3d = build_button_symbols(H_TOTAL, depth=INLAY_DEPTH)
    inlay_raw = logo_3d.fuse(btn_sym_3d)

    # Intersect inlay with the solid top cover so it conforms 100% to the top surface
    inlay_shape = cover.common(inlay_raw)
    cover_cut = cover.cut(inlay_shape)

    return cover_cut.removeSplitter(), inlay_shape


def build_button_cap(bx, by):
    """Build a captive 3D-printable button cap with a 100% flat underside."""
    flange = Part.makeCylinder(CAP_FLANGE_D / 2.0, CAP_FLANGE_H, V(bx, by, Z_CAP_BOT))
    shaft_h = Z_CAP_TOP - Z_CAP_BOT - 0.8
    shaft = Part.makeCylinder(CAP_D / 2.0, shaft_h, V(bx, by, Z_CAP_BOT))
    top_cone = Part.makeCone(
        CAP_D / 2.0,
        CAP_D / 2.0 - 0.8,
        0.8,
        V(bx, by, Z_CAP_BOT + shaft_h),
    )
    return flange.fuse(shaft).fuse(top_cone).removeSplitter()


def build_hardware_dummies():
    """Build exact reference 3D shapes from A..N measurements."""
    dummies = {}

    pcb = make_heltec_pcb_shape(clr=0.0, z0=Z_PCB_BOT, h=PCB_T)
    oled_frame = Part.makeBox(
        33.07, 18.63, 7.00 - PCB_T,
        V(X_FRAME_MIN, Y_FRAME_MIN, Z_PCB_TOP),
    )
    ribbon_dummy = Part.makeBox(
        13.00, RIBBON_PROTRUSION_Y, 4.5,
        V(X_OLED_CENTER - 6.50, Y_FRAME_MIN - RIBBON_PROTRUSION_Y, Z_PCB_TOP + 0.5),
    )
    usb_port = Part.makeBox(
        5.5, 8.0, 2.8,
        V(X_PCB_MIN, Y_PCB_CENTER - 4.0, Z_PCB_TOP),
    )
    jst_bot = Part.makeBox(
        5.0, 8.0, 5.72 - PCB_T,
        V(X_PCB_MIN + 2.0, Y_PCB_CENTER - 4.0, Z_PCB_BOT - (5.72 - PCB_T)),
    )
    dummies["Heltec_V2_Ref"] = pcb.fuse(oled_frame).fuse(ribbon_dummy).fuse(usb_port).fuse(jst_bot)

    sw_shapes = []
    for bx in BTN_XS:
        body = Part.makeBox(6.0, 6.0, TACT_BODY_H, V(bx - 3.0, Y_BTN - 3.0, Z_TACT_FLOOR))
        stem = Part.makeCylinder(1.75, TACT_TOTAL_H, V(bx, Y_BTN, Z_TACT_FLOOR))
        sw_shapes.append(body.fuse(stem))
    dummies["TactileSwitches_Ref"] = sw_shapes[0].fuse(sw_shapes[1]).fuse(sw_shapes[2])

    # SMA Bulkhead + 18.0 mm internal protrusion (I = 18.0 mm) at Y_MAX_OUT = +47.0 mm
    sma_inner = Part.makeCylinder(3.15, 18.0, V(X_SMA, Y_MAX_OUT - WALL - 18.0, Z_SMA), V(0, 1, 0))
    sma_nut = hex_prism_y(X_SMA, Z_SMA, Y_MAX_OUT, 4.0, 8.0)
    ant_base = Part.makeCylinder(5.0, 12.0, V(X_SMA, Y_MAX_OUT + 4.0, Z_SMA), V(0, 1, 0))
    ant_radome = Part.makeCone(4.8, 3.8, 38.0, V(X_SMA, Y_MAX_OUT + 16.0, Z_SMA), V(0, 1, 0))
    dummies["SMA_Antenna_Ref"] = sma_inner.fuse(sma_nut).fuse(ant_base).fuse(ant_radome)

    bat = Part.makeBox(
        38.0, 16.0, 9.0,
        V(-24.0, Y_BAT_CENTER - 8.0, FLOOR + 0.3),
    )
    dummies["LiPo_Battery_Ref"] = bat

    return dummies


def shape_to_mesh_xml(obj_id, name, shp, extruder_num=1):
    m = Mesh.Mesh(MeshPart.meshFromShape(Shape=shp, LinearDeflection=0.02, AngularDeflection=0.15, Relative=False))
    topo = m.Topology
    verts = topo[0]
    facets = topo[1]
    v_lines = [f'          <vertex x="{v.x:.4f}" y="{v.y:.4f}" z="{v.z:.4f}" />' for v in verts]
    t_lines = [f'          <triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}" />' for f in facets]
    return (
        f'    <object id="{obj_id}" name="{name}" type="model">\n'
        f'      <mesh>\n'
        f'        <vertices>\n' + "\n".join(v_lines) + '\n        </vertices>\n'
        f'        <triangles>\n' + "\n".join(t_lines) + '\n        </triangles>\n'
        f'      </mesh>\n'
        f'    </object>'
    )


def export_bambu_plate_3mf(bottom_shape, top_shape, inlay_shape, cap_shape, out_3mf_path):
    """Export a ready-to-print Multi-Color Bambu Studio .3mf plate:
       - Gehaeuse_Unten (Extruder 1)
       - Gehaeuse_Oben (Composite Multi-Color Object:
           Sub-part 1 = Deckel_Hauptkoerper [Extruder 1],
           Sub-part 2 = IoTUeli_Logo_und_Tasten [Extruder 2], both rotated together face-down on Z=0!)
       - 3x Taster_Kappe (Extruder 2 accent color)
    """
    s_bot = bottom_shape.copy()
    bb = s_bot.BoundBox
    s_bot.translate(V(84.0 - bb.Center.x, 140.0 - bb.Center.y, -bb.ZMin))

    # Rotate BOTH top_shape and inlay_shape around the exact same center & translate by the exact same vector
    # so the 0.60 mm Logo & Button inlays sit 100% flush on the build plate (Z = 0.00 mm)!
    s_top = top_shape.copy()
    s_inl = inlay_shape.copy()
    rot_center = s_top.BoundBox.Center
    s_top.rotate(rot_center, V(1, 0, 0), 180.0)
    s_inl.rotate(rot_center, V(1, 0, 0), 180.0)
    bb_top = s_top.BoundBox
    dx = 172.0 - bb_top.Center.x
    dy = 140.0 - bb_top.Center.y
    dz = -bb_top.ZMin
    s_top.translate(V(dx, dy, dz))
    s_inl.translate(V(dx, dy, dz))

    caps_oriented = []
    for idx, cx in enumerate((108.0, 128.0, 148.0), start=1):
        sc = cap_shape.copy()
        bb = sc.BoundBox
        sc.translate(V(cx - bb.Center.x, 74.0 - bb.Center.y, -bb.ZMin))
        caps_oriented.append((f"Taster_Kappe_{idx}", sc))

    # Object IDs:
    # 1: Gehaeuse_Unten (mesh, extruder 1)
    # 2: Deckel_Hauptkoerper (mesh, extruder 1)
    # 3: IoTUeli_Logo_und_Tasten (mesh, extruder 2)
    # 4: Gehaeuse_Oben (composite assembly of 2 + 3)
    # 5, 6, 7: Taster_Kappe_1..3 (mesh, extruder 2)
    obj_xml_list = [
        shape_to_mesh_xml(1, "Gehaeuse_Unten", s_bot, 1),
        shape_to_mesh_xml(2, "Deckel_Hauptkoerper", s_top, 1),
        shape_to_mesh_xml(3, "IoTUeli_Logo_und_Tasten", s_inl, 2),
        (
            '    <object id="4" name="Gehaeuse_Oben" type="model">\n'
            '      <components>\n'
            '        <component objectid="2" />\n'
            '        <component objectid="3" />\n'
            '      </components>\n'
            '    </object>'
        ),
    ]
    for idx, (cname, cshp) in enumerate(caps_oriented, start=5):
        obj_xml_list.append(shape_to_mesh_xml(idx, cname, cshp, 2))

    build_xml_list = [
        '    <item objectid="1" />',
        '    <item objectid="4" />',
        '    <item objectid="5" />',
        '    <item objectid="6" />',
        '    <item objectid="7" />',
    ]

    model_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<model unit="millimeter" xml:lang="en-US" '
        'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
        '  <metadata name="Application">BambuStudio</metadata>\n'
        '  <resources>\n'
        + "\n".join(obj_xml_list)
        + '\n  </resources>\n'
        '  <build>\n'
        + "\n".join(build_xml_list)
        + '\n  </build>\n'
        '</model>\n'
    )

    # Bambu Studio / PrusaSlicer model_settings.config for automatic multi-color extruder assignment
    model_settings_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<config>\n'
        '  <object id="1">\n'
        '    <metadata key="name" value="Gehaeuse_Unten"/>\n'
        '    <metadata key="extruder" value="1"/>\n'
        '  </object>\n'
        '  <object id="4">\n'
        '    <metadata key="name" value="Gehaeuse_Oben"/>\n'
        '    <part id="2" subtype="normal_part">\n'
        '      <metadata key="name" value="Deckel_Hauptkoerper"/>\n'
        '      <metadata key="extruder" value="1"/>\n'
        '    </part>\n'
        '    <part id="3" subtype="normal_part">\n'
        '      <metadata key="name" value="IoTUeli_Logo_und_Tasten"/>\n'
        '      <metadata key="extruder" value="2"/>\n'
        '    </part>\n'
        '  </object>\n'
        '  <object id="5">\n'
        '    <metadata key="name" value="Taster_Kappe_1"/>\n'
        '    <metadata key="extruder" value="2"/>\n'
        '  </object>\n'
        '  <object id="6">\n'
        '    <metadata key="name" value="Taster_Kappe_2"/>\n'
        '    <metadata key="extruder" value="2"/>\n'
        '  </object>\n'
        '  <object id="7">\n'
        '    <metadata key="name" value="Taster_Kappe_3"/>\n'
        '    <metadata key="extruder" value="2"/>\n'
        '  </object>\n'
        '</config>\n'
    )

    content_types_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        '  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />\n'
        '  <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml" />\n'
        '  <Default Extension="config" ContentType="text/xml" />\n'
        '</Types>\n'
    )

    rels_xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        '  <Relationship Target="/3D/3dmodel.model" Id="rel0" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" />\n'
        '</Relationships>\n'
    )

    with zipfile.ZipFile(out_3mf_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", rels_xml)
        zf.writestr("3D/3dmodel.model", model_xml)
        zf.writestr("Metadata/model_settings.config", model_settings_xml)


def set_color(obj, rgb, transparency=0):
    if getattr(App, "GuiUp", False) and obj.ViewObject is not None:
        obj.ViewObject.ShapeColor = rgb
        obj.ViewObject.Transparency = transparency


def build():
    os.makedirs(EXPORT_DIR, exist_ok=True)

    doc_name = "LoraWanFinder"
    if doc_name in App.listDocuments():
        doc = App.getDocument(doc_name)
        for o in list(doc.Objects):
            doc.removeObject(o.Name)
    else:
        doc = App.newDocument(doc_name)
    App.setActiveDocument(doc.Name)

    outer_blank = beveled_outer_blank()
    bottom_shape = build_bottom_shell(outer_blank)
    top_shape, inlay_shape = build_top_cover_and_inlay(outer_blank)

    o_bot = doc.addObject("Part::Feature", "BottomShell")
    o_bot.Label = "Gehaeuse_Unten"
    o_bot.Shape = bottom_shape
    set_color(o_bot, (0.20, 0.24, 0.28), 0)

    o_top = doc.addObject("Part::Feature", "TopCover")
    o_top.Label = "Gehaeuse_Oben"
    o_top.Shape = top_shape
    set_color(o_top, (0.24, 0.29, 0.35), 15)

    o_inl = doc.addObject("Part::Feature", "TopInlayColor2")
    o_inl.Label = "IoTUeli_Logo_und_Tasten_Farbe2"
    o_inl.Shape = inlay_shape
    set_color(o_inl, (0.00, 0.78, 0.95), 0)

    cap_labels = ("Taster_Links", "Taster_OK", "Taster_Rechts")
    cap_colors = ((0.00, 0.78, 0.95), (0.25, 0.82, 0.40), (0.00, 0.78, 0.95))
    cap_shapes = []
    for i, (bx, label, col) in enumerate(zip(BTN_XS, cap_labels, cap_colors), start=1):
        c_shape = build_button_cap(bx, Y_BTN)
        cap_shapes.append(c_shape)
        o_cap = doc.addObject("Part::Feature", f"ButtonCap_{i}")
        o_cap.Label = label
        o_cap.Shape = c_shape
        set_color(o_cap, col, 0)

    dummies = build_hardware_dummies()
    ref_colors = {
        "Heltec_V2_Ref": (0.92, 0.92, 0.92),
        "TactileSwitches_Ref": (0.75, 0.75, 0.78),
        "SMA_Antenna_Ref": (0.85, 0.68, 0.20),
        "LiPo_Battery_Ref": (0.25, 0.50, 0.85),
    }
    for name, shp in dummies.items():
        obj = doc.addObject("Part::Feature", name)
        obj.Shape = shp
        set_color(obj, ref_colors.get(name, (0.7, 0.7, 0.7)), 20)

    doc.recompute()
    doc.saveAs(FCSTD_PATH)

    Mesh.export([o_bot], os.path.join(EXPORT_DIR, "Gehaeuse_Unten.stl"))
    Mesh.export([o_top], os.path.join(EXPORT_DIR, "Gehaeuse_Oben.stl"))
    Mesh.export([o_inl], os.path.join(EXPORT_DIR, "Logo_und_Tasten_Farbe2.stl"))
    Mesh.export([doc.getObject("ButtonCap_1")], os.path.join(EXPORT_DIR, "Taster_Kappe.stl"))

    plate_3mf = os.path.join(EXPORT_DIR, "LoraWanFinder_BambuLab_Platte.3mf")
    export_bambu_plate_3mf(bottom_shape, top_shape, inlay_shape, cap_shapes[0], plate_3mf)

    report_data = {
        "outer_dimensions_mm": [W_OUT, L_OUT, H_TOTAL],
        "bottom_shell_valid": bottom_shape.isValid(),
        "top_cover_valid": top_shape.isValid(),
        "inlay_solids": len(inlay_shape.Solids),
        "collisions_mm3": {
            "bottom_vs_heltec": round(bottom_shape.common(dummies["Heltec_V2_Ref"]).Volume, 3),
            "top_vs_heltec": round(top_shape.common(dummies["Heltec_V2_Ref"]).Volume, 3),
            "heltec_vs_sma_18mm": round(dummies["Heltec_V2_Ref"].common(dummies["SMA_Antenna_Ref"]).Volume, 3),
            "bottom_vs_switches": round(bottom_shape.common(dummies["TactileSwitches_Ref"]).Volume, 3),
            "top_vs_switches": round(top_shape.common(dummies["TactileSwitches_Ref"]).Volume, 3),
            "bottom_vs_battery": round(bottom_shape.common(dummies["LiPo_Battery_Ref"]).Volume, 3),
            "bottom_vs_sma": round(bottom_shape.common(dummies["SMA_Antenna_Ref"]).Volume, 3),
            "top_vs_caps": round(sum(top_shape.common(c).Volume for c in cap_shapes), 3),
        },
        "exports": [
            plate_3mf,
            os.path.join(EXPORT_DIR, "Gehaeuse_Unten.stl"),
            os.path.join(EXPORT_DIR, "Gehaeuse_Oben.stl"),
            os.path.join(EXPORT_DIR, "Logo_und_Tasten_Farbe2.stl"),
            os.path.join(EXPORT_DIR, "Taster_Kappe.stl"),
            FCSTD_PATH,
        ],
    }
    return report_data


result = build()
print(json.dumps(result, indent=2))
