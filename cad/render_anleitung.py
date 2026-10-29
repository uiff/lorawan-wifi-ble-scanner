import os
import shutil
import FreeCAD as App
import FreeCADGui as Gui

IMG_DIR = r"c:\Users\uiff\Documents\coding\ESP_LoraWan_Finder\docs\anleitung\img"
ART_DIR = r"C:\Users\uiff\.gemini\antigravity\brain\4b72dc1a-fb07-4ae4-b9ba-bce37b21af7b"
os.makedirs(IMG_DIR, exist_ok=True)

doc = App.getDocument("LoraWanFinder")
App.setActiveDocument("LoraWanFinder")
Gui.setActiveDocument("LoraWanFinder")
view = Gui.getDocument("LoraWanFinder").ActiveView

ALL_OBJS = [
    "BottomShell",
    "TopCover",
    "TopInlayColor2",
    "ButtonCap_1",
    "ButtonCap_2",
    "ButtonCap_3",
    "Heltec_V2_Ref",
    "TactileSwitches_Ref",
    "SMA_Antenna_Ref",
    "LiPo_Battery_Ref",
]


def set_vis(visible_names, transparencies=None):
    transparencies = transparencies or {}
    for name in ALL_OBJS:
        obj = doc.getObject(name)
        if obj and obj.ViewObject:
            vis = name in visible_names
            obj.ViewObject.Visibility = vis
            if vis:
                obj.ViewObject.Transparency = transparencies.get(name, 0)
                obj.ViewObject.DisplayMode = "Flat Lines"
                obj.ViewObject.LineWidth = 1.5


def reset_placements():
    for name in ALL_OBJS:
        obj = doc.getObject(name)
        if obj:
            obj.Placement.Base = App.Vector(0, 0, 0)
    doc.recompute()


def save_shot(filename, cam_type="iso", w=1400, h=950):
    if cam_type == "iso":
        view.viewIsometric()
    elif cam_type == "front":
        view.viewFront()
    elif cam_type == "top":
        view.viewTop()
    elif cam_type == "bottom":
        view.viewBottom()
    elif cam_type == "right":
        view.viewRight()
    view.fitAll()
    Gui.updateGui()
    out_path = os.path.join(IMG_DIR, filename)
    view.saveImage(out_path, w, h, "White")
    try:
        from PIL import Image, ImageChops
        im = Image.open(out_path).convert("RGB")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bbox = ImageChops.difference(im, bg).getbbox()
        if bbox:
            pad = 40
            crop_box = (
                max(0, bbox[0] - pad),
                max(0, bbox[1] - pad),
                min(im.width, bbox[2] + pad),
                min(im.height, bbox[3] + pad),
            )
            im.crop(crop_box).save(out_path)
    except Exception as e:
        print("Crop warning:", e)
    try:
        shutil.copy2(out_path, os.path.join(ART_DIR, filename))
    except Exception:
        pass
    print("Saved:", out_path)


reset_placements()

# 1. Assembled overall view
set_vis(
    ALL_OBJS,
    {"TopCover": 10, "Heltec_V2_Ref": 0},
)
save_shot("01_gesamt.png", "iso", 1400, 950)
save_shot("top_check_v5.png", "top", 1400, 1100)

# 2. Exploded view
offsets = {
    "BottomShell": (0, 0, 0),
    "LiPo_Battery_Ref": (0, 0, 18),
    "TactileSwitches_Ref": (0, 0, 32),
    "SMA_Antenna_Ref": (0, 18, 34),
    "Heltec_V2_Ref": (0, 0, 52),
    "ButtonCap_1": (0, 0, 72),
    "ButtonCap_2": (0, 0, 72),
    "ButtonCap_3": (0, 0, 72),
    "TopCover": (0, 0, 92),
    "TopInlayColor2": (0, 0, 92),
}
for name, (dx, dy, dz) in offsets.items():
    obj = doc.getObject(name)
    if obj:
        obj.Placement.Base = App.Vector(dx, dy, dz)
doc.recompute()
set_vis(ALL_OBJS, {"TopCover": 8})
save_shot("02_explosion.png", "iso", 1400, 1100)
reset_placements()

# 3. Bottom shell alone (with wide wire pass-through & spacious antenna bay)
set_vis(["BottomShell"])
save_shot("03_gehaeuse_unten.png", "iso", 1400, 950)

# 4. Bottom shell + Switches + LiPo + SMA Antenna
set_vis(["BottomShell", "TactileSwitches_Ref", "LiPo_Battery_Ref", "SMA_Antenna_Ref"])
save_shot("04_taster_akku_sma.png", "iso", 1400, 950)

# 5. Heltec V2 installed
set_vis(
    ["BottomShell", "TactileSwitches_Ref", "LiPo_Battery_Ref", "SMA_Antenna_Ref", "Heltec_V2_Ref"],
)
save_shot("05_heltec_einbau.png", "iso", 1400, 950)

# 6. Top cover + 2-color Inlay + 3 button caps
set_vis(["TopCover", "TopInlayColor2", "ButtonCap_1", "ButtonCap_2", "ButtonCap_3"], {"TopCover": 5})
save_shot("06_deckel_kappen.png", "iso", 1400, 950)

# Restore full view
set_vis(ALL_OBJS, {"TopCover": 10})
view.viewIsometric()
view.fitAll()
