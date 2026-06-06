#!/usr/bin/env python3
"""Generate annotated robot image with labels baked in."""

from PIL import Image, ImageDraw, ImageFont

SRC = "images/final_car.png"
OUT = "images/final_car_annotated.png"

img = Image.open(SRC).convert("RGBA")

# Arrow endpoints — where the dot lands on the photo (3024 x 4032)
TARGETS = {
    "esp32": (1460, 1680),       # ESP32 board (below wire bundle)
    "pot": (980, 1850),          # rear face of white chassis
    "motor": (1630, 2480),       # red L298N board center
    "battery": (1760, 3080),     # black-taped battery pack
    "photo": (940, 2620),        # front photoresistor / light shield
}

# Label box positions (text only — separate from arrow endpoints)
LABELS = [
    ("ESP32", (1280, 480), "esp32", False),
    ("Potentiometer Circuit\n(On Back)", (80, 1050), "pot", True),
    ("Motor Driver", (2150, 1880), "motor", False),
    ("Photoresistor Circuit\n+ Light Shield", (2150, 2780), "battery", True),
    ("Motors + Battery\nPack", (80, 2480), "photo", True),
]

overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
draw = ImageDraw.Draw(overlay)

font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 52)
font_sm = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 44)

PINK = (228, 76, 101, 255)
WHITE = (255, 255, 255, 235)
BLACK = (26, 26, 26, 255)


def anchor_point(box, target):
    x0, y0, x1, y1 = box
    tx, ty = target
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = tx - cx, ty - cy
    if abs(dx) > abs(dy):
        return (x1 if dx > 0 else x0, max(y0, min(y1, ty)))
    return (max(x0, min(x1, tx)), y1 if dy > 0 else y0)


def draw_label(text, label_pos, target_key, multiline=False):
    tx, ty = TARGETS[target_key]
    lx, ly = label_pos
    f = font_sm if multiline else font
    lines = text.split("\n")
    line_heights = []
    max_w = 0
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=f)
        max_w = max(max_w, bbox[2] - bbox[0])
        line_heights.append(bbox[3] - bbox[1])
    pad_x, pad_y = 28, 20
    box_h = sum(line_heights) + pad_y * 2 + (len(lines) - 1) * 8
    box_w = max_w + pad_x * 2
    box = [lx, ly, lx + box_w, ly + box_h]
    draw.rounded_rectangle(box, radius=18, fill=WHITE, outline=PINK, width=4)
    cy = ly + pad_y
    for i, line in enumerate(lines):
        draw.text((lx + pad_x, cy), line, fill=BLACK, font=f)
        cy += line_heights[i] + 8
    sx, sy = anchor_point(box, (tx, ty))
    draw.line([sx, sy, tx, ty], fill=PINK, width=6)
    draw.ellipse([tx - 16, ty - 16, tx + 16, ty + 16], fill=PINK)


for item in LABELS:
    draw_label(*item)

out = Image.alpha_composite(img, overlay).convert("RGB")
out.save(OUT, quality=95)
print("Targets:", TARGETS)
print(f"Wrote {OUT}")
