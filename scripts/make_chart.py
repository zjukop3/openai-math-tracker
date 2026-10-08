#!/usr/bin/env python3
"""Render the discipline-distribution chart (article/学科分布图.png) from data/stats.json."""
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
stats = json.loads((ROOT / "data" / "stats.json").read_text())

items = sorted(stats["disciplines"].items(), key=lambda kv: -kv[1])
total = stats["families"]

FONT_CANDIDATES = [
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]
def font(size):
    for c in FONT_CANDIDATES:
        if Path(c).exists():
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()

BAR_H, GAP, PAD_L, PAD_R, PAD_T = 34, 10, 340, 90, 70
LABEL_W = 300
W = 1200
H = PAD_T + len(items) * (BAR_H + GAP) + 40
maxv = max(v for _, v in items)

img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
f_title, f_label, f_val = font(30), font(22), font(22)

d.text((PAD_L - LABEL_W + 10, 20),
       f"openai/math: {stats['families']} result families by discipline", font=f_title, fill="#111")

bar_max_w = W - PAD_L - PAD_R
for i, (name, v) in enumerate(items):
    y = PAD_T + i * (BAR_H + GAP)
    bw = int(bar_max_w * v / maxv)
    d.text((10, y + 4), name, font=f_label, fill="#222")
    d.rectangle([PAD_L, y, PAD_L + bw, y + BAR_H], fill="#3b82f6")
    d.text((PAD_L + bw + 10, y + 4), f"{v}  ({v / total:.0%})", font=f_val, fill="#333")

out = ROOT / "article" / "discipline-distribution.png"
img.save(out)
print("wrote", out)
