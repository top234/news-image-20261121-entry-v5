#!/usr/bin/env python3
"""news-image-20261121 v5 -- "The Saturday Ledger", clean-base revision.

Draws entry.png (1024x1024): 35 verified stories from Saturday 21 November
2026 on one newspaper front page. Iterates on v3's clean layout (same
masthead size, white stat chips, region row, 3 heroes + 10 small cards +
map + numbered list + DATE CHECK + footer) with v4's corrected numbers,
illustrated scene strips on the small cards, and Kryvyi Rih in the top 13.

Deterministic: seeded RNG, no network, no external assets, DejaVu fonts
from the system only. Re-running produces a byte-identical entry.png.
"""

import hashlib
import math
import random

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
SEED = 20261121
OUT = "entry.png"

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = f"{FONT_DIR}/DejaVuSerif.ttf"
SERIF_B = f"{FONT_DIR}/DejaVuSerif-Bold.ttf"
SANS = f"{FONT_DIR}/DejaVuSans.ttf"
SANS_B = f"{FONT_DIR}/DejaVuSans-Bold.ttf"

# ---- palette -----------------------------------------------------------
PAPER = (246, 241, 226)      # warm newsprint cream
CARD = (255, 253, 246)       # card paper
INK = (28, 43, 58)           # deep navy ink
RED = (179, 35, 27)          # headline red
MUTED = (112, 108, 96)       # grey caption ink
BORDER = (198, 190, 168)     # card border
CHIP_LINE = (214, 207, 186)  # stat-chip border
DATE_BG = (253, 236, 234)    # date-check wash
DATE_LINE = (179, 35, 27)

# tag colours per story topic
TAG = {
    "climate": (31, 111, 107),
    "defence": (179, 35, 27),
    "quake": (198, 93, 18),
    "war": (43, 74, 122),
    "aviation": (31, 111, 107),
    "markets": (43, 74, 122),
    "motorsport": (198, 93, 18),
    "cricket": (43, 74, 122),
    "diplomacy": (122, 63, 143),
    "transport": (150, 60, 40),
    "tennis": (31, 111, 107),
}

_font_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def text_w(draw, s, f):
    return draw.textlength(s, font=f)


def wrap(draw, text, f, max_w):
    """Greedy word wrap; returns a list of lines that each fit max_w."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if text_w(draw, trial, f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def vgrad(draw, x, y, w, h, top, bottom):
    """Vertical gradient sky inside (x, y, w, h)."""
    for i in range(h):
        draw.line([(x, y + i), (x + w - 1, y + i)],
                  fill=lerp(top, bottom, i / max(1, h - 1)))


def stars(draw, rng, x, y, w, h, n, colour=(255, 244, 200)):
    for _ in range(n):
        sx = x + rng.randint(2, w - 3)
        sy = y + rng.randint(2, h - 3)
        r = rng.choice([1, 1, 1, 2])
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=colour)


def burst(draw, cx, cy, r, colour, rays=10):
    """Starburst: radiating lines plus a bright core."""
    for k in range(rays):
        ang = 2 * math.pi * k / rays
        x2 = cx + r * math.cos(ang)
        y2 = cy + r * math.sin(ang)
        draw.line([(cx, cy), (x2, y2)], fill=colour, width=2)
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 240, 180))
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=(255, 255, 255))


def dotted_arc(draw, pts, colour, step=5):
    """Dotted trail through a list of points."""
    for i in range(0, len(pts), step):
        px, py = pts[i]
        draw.ellipse([px - 1, py - 1, px + 1, py + 1], fill=colour)


def quad(points, steps=24):
    """Quadratic bezier sample points for a dotted arc."""
    (x0, y0), (x1, y1), (x2, y2) = points[0], points[1], points[2]
    out = []
    for i in range(steps + 1):
        t = i / steps
        out.append((int((1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t * t * x2),
                    int((1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t * t * y2)))
    return out


# ---- illustrated scenes (pure pictures, no text) -----------------------
# Every scene paints inside (x, y, w, h). rng is a seeded Random.

def scene_cop31(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (44, 84, 96), (126, 178, 168))
    stars(draw, rng, x, y, w, h // 2, 14)
    # rising sun behind the globe
    draw.ellipse([x + w - 66, y + 8, x + w - 18, y + 56], fill=(255, 205, 110))
    draw.ellipse([x + w - 58, y + 16, x + w - 26, y + 48], fill=(255, 226, 150))
    # globe
    gx, gy, gr = x + 52, y + h // 2 + 2, 30
    draw.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 180),
                 outline=(20, 60, 90), width=2)
    draw.ellipse([gx - 18, gy - 16, gx + 2, gy + 2], fill=(96, 170, 90))
    draw.ellipse([gx - 4, gy + 8, gx + 20, gy + 24], fill=(96, 170, 90))
    draw.ellipse([gx + 6, gy - 24, gx + 22, gy - 8], fill=(96, 170, 90))
    # thermometer, mercury high
    tx = x + w - 118
    draw.rounded_rectangle([tx, y + 10, tx + 14, y + h - 20], radius=7,
                           fill=(240, 240, 235), outline=(30, 30, 30), width=2)
    draw.rectangle([tx + 4, y + 18, tx + 10, y + h - 26], fill=(200, 40, 30))
    draw.ellipse([tx - 4, y + h - 30, tx + 18, y + h - 8], fill=(200, 40, 30),
                 outline=(30, 30, 30), width=2)
    # summit flags along the bottom
    for i in range(7):
        fx = x + 108 + i * 22
        draw.line([(fx, y + h - 22), (fx, y + h - 2)], fill=(240, 240, 235),
                  width=2)
        draw.polygon([(fx, y + h - 22), (fx + 14, y + h - 18),
                      (fx, y + h - 14)],
                     fill=[(200, 60, 50), (60, 120, 200), (240, 200, 60),
                           (70, 160, 90), (200, 120, 40), (140, 80, 180),
                           (240, 240, 235)][i])


def scene_riyadh(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (16, 24, 52), (48, 52, 92))
    stars(draw, rng, x, y, w, h, 26)
    # crescent moon
    draw.ellipse([x + w - 52, y + 6, x + w - 22, y + 36], fill=(245, 238, 200))
    draw.ellipse([x + w - 46, y + 2, x + w - 18, y + 32], fill=(24, 32, 62))
    # skyline with lit windows
    base = y + h
    towers = [(0, 46, 34), (30, 60, 26), (58, 40, 30), (90, 66, 24),
              (116, 48, 32), (150, 62, 26), (178, 44, 30), (210, 58, 26),
              (238, 50, 30), (270, 64, 24), (296, 46, 24)]
    for ox, th, tw in towers:
        draw.rectangle([x + ox, base - th, x + ox + tw, base],
                       fill=(10, 14, 30))
        for wy in range(base - th + 5, base - 6, 9):
            for wx in range(x + ox + 4, x + ox + tw - 4, 8):
                if rng.random() < 0.5:
                    draw.rectangle([wx, wy, wx + 3, wy + 4],
                                   fill=(255, 214, 120))
    # intercept bursts + dotted missile trails
    for bx, by in [(x + 78, y + 16), (x + 168, y + 10), (x + 252, y + 18)]:
        burst(draw, bx, by, 13, (255, 190, 90))
    dotted_arc(draw, quad([(x + 40, y + 62), (x + 60, y + 22),
                           (x + 78, y + 16)]), (255, 220, 150))
    dotted_arc(draw, quad([(x + 210, y + 64), (x + 235, y + 30),
                           (x + 252, y + 18)]), (255, 220, 150))


def scene_peru(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (214, 122, 40), (242, 196, 130))
    # mountain ridges
    draw.polygon([(x, y + h), (x + 60, y + 22), (x + 130, y + h)],
                 fill=(122, 74, 40))
    draw.polygon([(x + 90, y + h), (x + 180, y + 10), (x + 280, y + h)],
                 fill=(96, 56, 32))
    draw.polygon([(x + 230, y + h), (x + 300, y + 30), (x + w, y + h)],
                 fill=(122, 74, 40))
    # snow caps
    draw.polygon([(x + 168, y + 20), (x + 180, y + 10), (x + 192, y + 20),
                  (x + 186, y + 24), (x + 180, y + 19), (x + 174, y + 24)],
                 fill=(250, 248, 240))
    # shaking house
    hx, hy = x + w - 62, y + h - 34
    draw.rectangle([hx, hy + 10, hx + 34, hy + 32], fill=(250, 244, 230),
                   outline=(90, 60, 40), width=2)
    draw.polygon([(hx - 4, hy + 10), (hx + 17, hy - 4), (hx + 38, hy + 10)],
                 fill=(160, 50, 40))
    draw.line([(hx + 8, hy + 12), (hx + 12, hy + 18), (hx + 9, hy + 24)],
              fill=(120, 40, 30), width=2)
    # seismograph trace across the sky
    pts = []
    px = x + 8
    while px < x + w - 8:
        pts.append((px, y + 16 + rng.randint(-3, 3)))
        px += 6
    mid = len(pts) // 2
    for k, spike in enumerate([-16, 20, -24, 14, -8, 6]):
        pts[mid + k] = (pts[mid + k][0], pts[mid + k][1] + spike)
    draw.line(pts, fill=(170, 30, 25), width=2)


def scene_hormuz(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (150, 196, 222), (214, 232, 240))
    # sea
    draw.rectangle([x, y + h - 16, x + w, y + h], fill=(52, 110, 150))
    for i in range(5):
        wx = x + 12 + i * 36
        draw.arc([wx, y + h - 12, wx + 18, y + h - 4], 180, 360,
                 fill=(220, 240, 250), width=2)
    # tanker silhouette
    draw.rectangle([x + 18, y + h - 30, x + 86, y + h - 16],
                   fill=(40, 50, 66))
    draw.rectangle([x + 66, y + h - 40, x + 78, y + h - 30],
                   fill=(40, 50, 66))
    # drone overhead with rotor blur
    dx, dy = x + w - 46, y + 12
    draw.ellipse([dx - 8, dy - 3, dx + 8, dy + 3], fill=(30, 34, 40))
    draw.line([(dx - 16, dy - 6), (dx + 16, dy - 6)], fill=(90, 96, 104),
              width=2)
    draw.line([(dx - 5, dy + 3), (dx - 8, dy + 10)], fill=(30, 34, 40),
              width=2)
    draw.line([(dx + 5, dy + 3), (dx + 8, dy + 10)], fill=(30, 34, 40),
              width=2)
    draw.ellipse([dx - 2, dy - 2, dx + 2, dy + 2], fill=(220, 60, 50))


def scene_kryvyi(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (14, 20, 44), (44, 48, 80))
    stars(draw, rng, x, y, w, h // 2, 12)
    # explosion glow over the rooftops
    gx, gy = x + w // 2 + 18, y + h - 22
    for r, col in [(30, (120, 50, 30)), (22, (200, 90, 30)),
                   (14, (250, 150, 50)), (8, (255, 220, 120))]:
        draw.ellipse([gx - r, gy - r, gx + r, gy + r], fill=col)
    # building silhouettes
    for ox, th, tw in [(0, 20, 30), (28, 28, 24), (52, 18, 26),
                       (118, 26, 24), (142, 20, 26), (168, 30, 21)]:
        draw.rectangle([x + ox, y + h - th, x + ox + tw, y + h],
                       fill=(8, 10, 24))
        for wy in range(y + h - th + 4, y + h - 4, 8):
            for wx in range(x + ox + 4, x + ox + tw - 3, 8):
                if rng.random() < 0.4:
                    draw.rectangle([wx, wy, wx + 3, wy + 3],
                                   fill=(255, 200, 100))
    # smoke column
    for i, (sx, sy, sr) in enumerate([(gx - 14, gy - 26, 7),
                                      (gx - 6, gy - 34, 9),
                                      (gx + 4, gy - 40, 6)]):
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(70, 70, 84))
    # rescue light beams from below
    draw.polygon([(x + 12, y + h), (x + 30, y + h), (x + 44, y + 8),
                  (x + 34, y + 8)], fill=(150, 190, 230))
    draw.polygon([(x + w - 30, y + h), (x + w - 12, y + h),
                  (x + w - 34, y + 10), (x + w - 44, y + 10)],
                 fill=(150, 190, 230))


def scene_davao(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (250, 214, 150), (168, 208, 232))
    draw.ellipse([x + 12, y + 4, x + 34, y + 26], fill=(255, 236, 170))
    # runway
    draw.polygon([(x, y + h), (x + w, y + h - 6), (x + w, y + h),
                  (x, y + h)], fill=(70, 74, 80))
    draw.rectangle([x, y + h - 8, x + w, y + h], fill=(80, 84, 90))
    for i in range(8):
        lx = x + 8 + i * 23
        draw.ellipse([lx, y + h - 6, lx + 4, y + h - 2],
                     fill=(255, 220, 120))
    # airliner on final approach
    px, py = x + 58, y + 12
    draw.ellipse([px, py, px + 72, py + 12], fill=(245, 245, 240))
    draw.polygon([(px + 66, py + 2), (px + 78, py - 6), (px + 82, py - 6),
                  (px + 76, py + 6)], fill=(30, 90, 140))
    draw.polygon([(px + 30, py + 10), (px + 46, py + 22), (px + 54, py + 22),
                  (px + 44, py + 10)], fill=(200, 210, 220))
    draw.polygon([(px + 34, py + 2), (px + 52, py - 8), (px + 58, py - 8),
                  (px + 46, py + 2)], fill=(200, 210, 220))
    for wx in range(px + 8, px + 64, 9):
        draw.rectangle([wx, py + 4, wx + 4, py + 7], fill=(40, 80, 120))
    # slides deployed below the fuselage
    draw.polygon([(px + 20, py + 12), (px + 30, py + 12),
                  (px + 40, y + h - 8), (px + 32, y + h - 8)],
                 fill=(240, 200, 90))


def scene_bitcoin(draw, rng, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(18, 26, 48))
    for gy in range(y + 8, y + h, 10):
        draw.line([(x + 4, gy), (x + w - 4, gy)], fill=(34, 44, 74), width=1)
    # falling price line with candles
    pts = [(x + 10, y + 10), (x + 40, y + 14), (x + 66, y + 12),
           (x + 92, y + 22), (x + 118, y + 28), (x + 144, y + 34),
           (x + 172, y + 40)]
    draw.line(pts, fill=(230, 70, 60), width=2)
    for cx, cy in [(x + 26, y + 12), (x + 78, y + 18), (x + 130, y + 30)]:
        draw.rectangle([cx - 3, cy - 4, cx + 3, cy + 4],
                       fill=(230, 70, 60))
        draw.line([(cx, cy - 8), (cx, cy + 8)], fill=(230, 70, 60), width=1)
    # gold coin, lower left
    cx, cy, cr = x + 30, y + h - 16, 13
    draw.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(240, 180, 60),
                 outline=(180, 120, 20), width=2)
    bf = font(SERIF_B, 15)
    draw.text((cx - 5, cy - 9), "B", font=bf, fill=(120, 75, 10))
    draw.line([(cx - 2, cy - 8), (cx - 2, cy + 8)], fill=(120, 75, 10),
              width=1)
    draw.line([(cx + 2, cy - 8), (cx + 2, cy + 8)], fill=(120, 75, 10),
              width=1)


def scene_vegas(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (12, 12, 34), (52, 26, 74))
    stars(draw, rng, x, y, w, h // 2, 10)
    # neon strip towers
    for ox, th, tw, col in [(4, 20, 16, (255, 90, 120)),
                            (24, 28, 14, (90, 200, 255)),
                            (42, 18, 18, (255, 210, 90)),
                            (148, 26, 16, (140, 255, 160)),
                            (168, 20, 16, (255, 150, 80))]:
        draw.rectangle([x + ox, y + h - 18 - th, x + ox + tw, y + h - 18],
                       fill=(16, 16, 34))
        draw.rectangle([x + ox + 2, y + h - 18 - th + 3,
                        x + ox + tw - 2, y + h - 18 - th + 7], fill=col)
        for wy in range(y + h - 18 - th + 10, y + h - 20, 6):
            draw.rectangle([x + ox + 3, wy, x + ox + tw - 3, wy + 2],
                           fill=col)
    # track with dashes
    draw.rectangle([x, y + h - 18, x + w, y + h], fill=(36, 36, 44))
    for i in range(9):
        dx = x + 6 + i * 21
        draw.rectangle([dx, y + h - 10, dx + 11, y + h - 7],
                       fill=(240, 240, 240))
    # F1 car
    cx, cy = x + 88, y + h - 24
    draw.rectangle([cx, cy, cx + 56, cy + 7], fill=(200, 30, 30))
    draw.polygon([(cx + 44, cy), (cx + 56, cy - 6), (cx + 62, cy - 6),
                  (cx + 62, cy)], fill=(200, 30, 30))
    draw.polygon([(cx - 8, cy + 2), (cx, cy), (cx, cy + 7), (cx - 8, cy + 7)],
                 fill=(180, 20, 20))
    for wx in (cx + 8, cx + 44):
        draw.ellipse([wx - 6, cy + 4, wx + 6, cy + 16], fill=(20, 20, 20),
                     outline=(120, 120, 130), width=2)
    # chequered flag corner
    for r in range(2):
        for c in range(4):
            fill = (245, 245, 245) if (r + c) % 2 == 0 else (20, 20, 20)
            draw.rectangle([x + w - 26 + c * 5, y + 4 + r * 5,
                            x + w - 22 + c * 5, y + 8 + r * 5], fill=fill)


def scene_cricket(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (168, 214, 240), (214, 236, 248))
    draw.rectangle([x, y + h - 18, x + w, y + h], fill=(86, 158, 74))
    draw.rectangle([x, y + h - 10, x + w, y + h], fill=(70, 138, 60))
    # pitch
    draw.rectangle([x + 74, y + h - 26, x + 108, y + h - 8],
                   fill=(216, 190, 150))
    # stumps
    for sx in (x + 80, x + 85, x + 90):
        draw.line([(sx, y + h - 26), (sx, y + h - 16)], fill=(240, 200, 60),
                  width=2)
    # batsman mid-drive
    bx, by = x + 128, y + h - 34
    draw.ellipse([bx - 5, by - 6, bx + 5, by + 4], fill=(240, 220, 200))
    draw.line([(bx, by + 4), (bx - 2, by + 16)], fill=(30, 70, 140), width=4)
    draw.line([(bx - 2, by + 16), (bx - 8, by + 26)], fill=(245, 245, 245),
              width=3)
    draw.line([(bx - 2, by + 16), (bx + 5, by + 26)], fill=(245, 245, 245),
              width=3)
    draw.line([(bx - 1, by + 8), (bx - 16, by + 20)], fill=(240, 220, 200),
              width=3)
    draw.line([(bx - 16, by + 20), (bx - 26, by + 30)], fill=(210, 170, 120),
              width=4)
    # red ball flying
    draw.ellipse([x + 34, y + 8, x + 42, y + 16], fill=(180, 40, 35))
    draw.arc([x + 40, y + 2, x + 66, y + 22], 300, 60, fill=(180, 40, 35),
             width=2)


def scene_warsaw(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (170, 206, 236), (226, 238, 246))
    # government building with columns
    bx, by = x + 52, y + h - 30
    draw.rectangle([bx, by, bx + 84, y + h - 2], fill=(232, 226, 210),
                   outline=(120, 110, 90), width=1)
    draw.polygon([(bx - 6, by), (bx + 42, by - 14), (bx + 90, by)],
                 fill=(180, 60, 55))
    for i in range(5):
        cx = bx + 10 + i * 16
        draw.rectangle([cx, by + 5, cx + 6, y + h - 6],
                       fill=(250, 248, 240))
    # flag poles: Poland + NATO star
    draw.line([(x + 18, y + 6), (x + 18, y + h - 2)], fill=(90, 90, 90),
              width=2)
    draw.rectangle([x + 18, y + 8, x + 40, y + 14], fill=(245, 245, 245))
    draw.rectangle([x + 18, y + 14, x + 40, y + 20], fill=(220, 40, 50))
    draw.line([(x + w - 20, y + 6), (x + w - 20, y + h - 2)],
              fill=(90, 90, 90), width=2)
    sx, sy = x + w - 32, y + 14
    draw.polygon([(sx, sy - 7), (sx + 2, sy - 2), (sx + 7, sy),
                  (sx + 2, sy + 2), (sx, sy + 7), (sx - 2, sy + 2),
                  (sx - 7, sy), (sx - 2, sy - 2)], fill=(40, 90, 160))


def scene_sejong(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (196, 216, 228), (232, 236, 238))
    # hills
    draw.polygon([(x, y + h - 14), (x + 50, y + 12), (x + 110, y + h - 14)],
                 fill=(140, 170, 130))
    draw.polygon([(x + 90, y + h - 14), (x + 150, y + 18),
                  (x + w, y + h - 14)], fill=(120, 155, 115))
    # track
    draw.rectangle([x, y + h - 14, x + w, y + h - 10], fill=(110, 100, 90))
    draw.rectangle([x, y + h - 8, x + w, y + h - 5], fill=(110, 100, 90))
    for i in range(10):
        sx = x + 6 + i * 19
        draw.rectangle([sx, y + h - 14, sx + 8, y + h - 4],
                       fill=(90, 80, 70))
    # freight cars: three upright, two tipped off the rails
    for i, (cx, col) in enumerate([(x + 12, (60, 110, 160)),
                                   (x + 52, (200, 90, 40)),
                                   (x + 92, (60, 140, 90))]):
        draw.rectangle([cx, y + h - 34, cx + 34, y + h - 14], fill=col)
    draw.polygon([(x + 136, y + h - 30), (x + 168, y + h - 38),
                  (x + 172, y + h - 20), (x + 140, y + h - 12)],
                 fill=(160, 60, 60))
    draw.polygon([(x + 164, y + h - 16), (x + 188, y + h - 26),
                  (x + 190, y + h - 8), (x + 168, y + h - 2)],
                 fill=(120, 120, 130))
    # dust cloud over the tipped cars
    for dx, dy, dr in [(x + 150, y + h - 38, 8), (x + 164, y + h - 44, 10),
                       (x + 178, y + h - 36, 7)]:
        draw.ellipse([dx - dr, dy - dr, dx + dr, dy + dr],
                     fill=(200, 195, 180))


def scene_tennis(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (150, 190, 230), (200, 226, 240))
    # court in perspective
    draw.polygon([(x + 14, y + h - 4), (x + w - 14, y + h - 4),
                  (x + w - 40, y + 10), (x + 40, y + 10)],
                 fill=(70, 140, 200))
    draw.polygon([(x + 52, y + h - 4), (x + w - 52, y + h - 4),
                  (x + w - 52, y + 10), (x + 52, y + 10)],
                 fill=(90, 165, 220))
    draw.line([(x + 14, y + h - 4), (x + 40, y + 10)], fill=(245, 245, 245),
              width=2)
    draw.line([(x + w - 14, y + h - 4), (x + w - 40, y + 10)],
              fill=(245, 245, 245), width=2)
    # net
    draw.line([(x + 30, y + 24), (x + w - 30, y + 24)], fill=(245, 245, 245),
              width=3)
    draw.line([(x + 30, y + 24), (x + 30, y + 34)], fill=(60, 60, 60),
              width=2)
    draw.line([(x + w - 30, y + 24), (x + w - 30, y + 34)],
              fill=(60, 60, 60), width=2)
    # ball + motion arc
    draw.ellipse([x + w - 58, y + 4, x + w - 46, y + 16],
                 fill=(220, 230, 60), outline=(150, 160, 40), width=1)
    draw.arc([x + 40, y - 6, x + w - 50, y + 22], 300, 80,
             fill=(220, 230, 60), width=2)
    # racket silhouette, lower left
    draw.ellipse([x + 14, y + h - 28, x + 38, y + h - 8],
                 outline=(40, 40, 60), width=3)
    draw.line([(x + 26, y + h - 8), (x + 18, y + h - 1)], fill=(40, 40, 60),
              width=3)


def scene_delhi(draw, rng, x, y, w, h):
    vgrad(draw, x, y, w, h, (250, 196, 130), (250, 224, 180))
    draw.ellipse([x + w - 40, y + 4, x + w - 16, y + 28],
                 fill=(255, 240, 190))
    # memorial arch (India Gate silhouette)
    ax = x + w // 2
    draw.rectangle([ax - 34, y + 12, ax + 34, y + h - 4],
                   fill=(190, 130, 80))
    draw.rectangle([ax - 42, y + 8, ax + 42, y + 14], fill=(170, 110, 65))
    draw.rectangle([ax - 12, y + 24, ax + 12, y + h - 4],
                   fill=(250, 224, 180))
    draw.pieslice([ax - 12, y + 14, ax + 12, y + 34], 180, 360,
                  fill=(250, 224, 180))
    draw.rectangle([ax - 46, y + h - 8, ax + 46, y + h - 4],
                   fill=(170, 110, 65))
    # flanking flags
    for fx, cols in [(x + 16, [(255, 150, 50), (245, 245, 245),
                               (30, 140, 70)]),
                     (x + w - 34, [(255, 150, 50), (245, 245, 245),
                                   (30, 140, 70)])]:
        draw.line([(fx, y + 10), (fx, y + h - 4)], fill=(90, 90, 90),
                  width=2)
        for k, col in enumerate(cols):
            draw.rectangle([fx, y + 12 + k * 5, fx + 16, y + 17 + k * 5],
                           fill=col)
    # lawn
    draw.rectangle([x, y + h - 4, x + w, y + h], fill=(110, 160, 90))


# ---- story data --------------------------------------------------------
# All 35 happened, or were first reported, on Saturday 21 November 2026.
# (Verification sources in BUILD_NOTES-v5.md.)

STRAPLINE = ("COP31 talks run into overtime \u00b7 Three missiles down over "
             "Riyadh \u00b7 Peru shaken by a 6.7 quake \u00b7 "
             "Kryvyi Rih toll climbs to 47")

CHIPS = [
    ("DAY 13", "COP31 overtime"),
    ("3", "missiles down, Riyadh"),
    ("6.7", "Peru quake"),
    ("146", "safe in Davao"),
    ("$56,357", "Bitcoin, 05:19 UTC"),
    ("136", "Rahul, Wellington"),
]

REGIONS = [
    ("ASIA-PACIFIC", 8, (31, 111, 107)),
    ("OCEANIA", 7, (43, 74, 122)),
    ("EUROPE", 7, (122, 63, 143)),
    ("AMERICAS", 5, (198, 93, 18)),
    ("MIDDLE EAST", 3, (179, 35, 27)),
    ("AFRICA", 3, (70, 140, 70)),
    ("GLOBAL", 2, (90, 96, 104)),
]

HEROES = [
    dict(num=1, tag="CLIMATE", place="ANTALYA", kind="climate",
         scene=scene_cop31,
         head="COP31 runs into overtime with no deal in sight",
         deck=("Day 13: nearly 200 nations deadlocked; the draft drops "
               "fossil fuels and the $120bn target. A third text is due "
               "Saturday."),
         source="SOURCE: AP \u00b7 REUTERS"),
    dict(num=2, tag="DEFENCE", place="RIYADH", kind="defence",
         scene=scene_riyadh,
         head="Three missiles shot down over Riyadh in the small hours",
         deck=("The Saudi-led coalition intercepts three Houthi missiles "
               "over the capital at about 2am \u2014 the second attack on "
               "Riyadh in days."),
         source="SOURCE: REUTERS"),
    dict(num=3, tag="QUAKE", place="PERU", kind="quake",
         scene=scene_peru,
         head="Peru shaken by a magnitude 6.7 quake",
         deck=("Jun\u00edn, 00:09 UTC, 108 km deep; felt in Lima. No "
               "casualties or damage reported, and no tsunami risk."),
         source="SOURCE: USGS \u00b7 AP"),
]

CARDS = [
    dict(num=4, tag="HORMUZ", kind="defence", scene=scene_hormuz,
         head="Iran claims it downed a US MQ-9 drone",
         deck="IRGC claims its 58th MQ-9 fell over the strait; US silent.",
         source="PRESS TV \u00b7 AFP"),
    dict(num=5, tag="KRYVYI RIH", kind="war", scene=scene_kryvyi,
         head="Kryvyi Rih toll climbs to 47 injured",
         deck=("Friday evening\u2019s double-tap strike kills a boy, 7, "
               "and a paramedic."),
         source="KYIV INDEPENDENT"),
    dict(num=6, tag="AVIATION", kind="aviation", scene=scene_davao,
         head="Jet lands safely in Davao after engine alert",
         deck="PX19: 137 passengers, 9 crew \u2014 all safe by slide; none hurt.",
         source="AP"),
    dict(num=7, tag="MARKETS", kind="markets", scene=scene_bitcoin,
         head="Bitcoin slides to $56,357 on Saturday",
         deck="Down 8.5% on the day at 05:19 UTC; intraday low $55,556.",
         source="FINNHUB \u00b7 BINANCE"),
    dict(num=8, tag="MOTORSPORT", kind="motorsport", scene=scene_vegas,
         head="Antonelli fastest, Verstappen inherits pole",
         deck=("Antonelli tops Q3 in 1:33.893; his penalty hands pole "
               "to Verstappen."),
         source="FORMULA 1"),
    dict(num=9, tag="CRICKET", kind="cricket", scene=scene_cricket,
         head="Rahul\u2019s 136 puts India on top in Wellington",
         deck=("13th Test ton; first Indian opener with tons in all "
               "SENA nations."),
         source="AFP"),
    dict(num=10, tag="DIPLOMACY", kind="diplomacy", scene=scene_warsaw,
         head="NATO chief Rutte visits Warsaw",
         deck=("Follows Friday\u2019s missile incident; Poland wants more "
               "NATO support."),
         source="REUTERS"),
    dict(num=11, tag="TRANSPORT", kind="transport", scene=scene_sejong,
         head="Freight train derails in Sejong",
         deck="Five of 21 cars derailed at Sejong; line cut, no injuries.",
         source="YONHAP"),
    dict(num=12, tag="TENNIS", kind="tennis", scene=scene_tennis,
         head="Turin semi-finals day at the ATP Finals",
         deck="Alcaraz v Shelton, then Zverev v Medvedev under the lights.",
         source="ATP TOUR"),
    dict(num=13, tag="DIPLOMACY", kind="diplomacy", scene=scene_delhi,
         head="SCO dialogue forum opens in Delhi",
         deck="First forum at Purana Qila; Pakistan\u2019s Malik due to speak.",
         source="ANI"),
]

LIST_ITEMS = [
    (14, "Kim Jong-un inspects dual-equipment factories (KCNA via Yonhap)"),
    (15, "Bangkok: PM chairs emergency meeting on arsenic in Chiang Rai rivers (Chiang Rai Times)"),
    (16, "Akvan remnants: heavy-rain alerts for eastern India \u2014 Bengal, Bihar, Odisha (IMD)"),
    (17, "Cricket Australia backs Cummins to stay on as Test captain (AFP)"),
    (18, "Jurf al-Sakhar: Karbala road and security HQ due to reopen Saturday (ANF)"),
    (19, "England v Australia 1st T20I, MCG, Sat 19:15 local (ECB)"),
    (20, "Indonesia\u2019s PLN signs six renewable power deals at COP31 (Antara)"),
    (21, "Hazlewood backs Cummins \u2014 and hints he could quit if the captain goes (Fox Sports)"),
    (22, "Las Vegas GP qualifying: Antonelli fastest in Q3, Verstappen inherits pole; Russell topped FP3 (F1)"),
    (23, "BBC: $811m migrant-bail scam firm still operating under new name (BBC)"),
    (24, "Barnham village votes on symbolically leaving UK over asylum plan (BBC)"),
    (25, "NHS: emergency admissions for high blood pressure up 77% since 2019 (NHS England)"),
    (26, "NSW passes Mount Pleasant coalmine expansion law at 01:36 (The Guardian)"),
    (27, "Homebirth rallies in 25 Australian towns over insurance deadline (AAP)"),
    (28, "Premier League returns: seven Saturday games; Frank\u2019s first Palace match (PL)"),
    (29, "Northern Ireland resident doctors\u2019 24-hour strike ends 07:00 GMT (BBC)"),
    (30, "AFLW: North Melbourne beat Sydney 83\u201351 to reach a fourth straight GF (AAP)"),
    (31, "F1 Academy: Larsen charges from ninth to win Las Vegas reverse-grid race (F1 Academy)"),
    (32, "ANC scrambles for city coalition deals after worst result since 1994 (BBC)"),
    (33, "Springboks v Ireland, Dublin, Sat 16:40 GMT; Erasmus banned 6 matches (BBC Sport)"),
    (34, "Hong Kong Open semis Sat: Sen v Antonsen; Satwik-Chirag also in last four (BWF)"),
    (35, "Ghana MP demands account of GH\u00a2100m for One Million Coders (GhanaWeb)"),
]

DATE_CHECK_1 = ("Deliberately left out: these are FRIDAY 20 NOVEMBER news, "
                "not Saturday\u2019s \u2014 missiles landing in Poland \u00b7 "
                "Wall Street\u2019s correction (S&P 500 \u22123.7%) \u00b7 "
                "the Kyiv barrage \u00b7 Cyclone Akvan\u2019s landfall \u00b7 "
                "the Los Angeles earthquake \u00b7 the Loch Leven glider "
                "crash \u00b7 Harry Kane\u2019s ankle injury \u00b7 Trump\u2019s "
                "data-centre tax \u00b7 Denmark expels attach\u00e9.")
DATE_CHECK_2 = ("Not confirmed when drawn, so not shown: BepiColombo to "
                "Mercury orbit (burn due 19:24 CET tonight) \u00b7 a final "
                "COP31 text.")
DATE_CHECK_3 = ("A story counts here only if it happened, or was first "
                "reported, on Saturday 21 November 2026.")

# ---- world map ---------------------------------------------------------
# Stylised continents as (lon, lat) polygons, equirectangular projection.

CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 72), (-85, 70),
     (-80, 73), (-65, 62), (-60, 52), (-65, 44), (-75, 35), (-80, 26),
     (-90, 21), (-97, 16), (-94, 17), (-87, 13), (-83, 9), (-79, 9),
     (-85, 14), (-90, 14), (-97, 22), (-105, 23), (-110, 28), (-114, 32),
     (-120, 36), (-124, 42), (-124, 48), (-130, 55), (-145, 60),
     (-158, 58), (-165, 60)],
    # South America
    [(-79, 9), (-75, 10), (-70, 12), (-60, 8), (-52, 5), (-50, 0),
     (-44, -3), (-35, -8), (-38, -15), (-40, -22), (-48, -28), (-52, -33),
     (-58, -38), (-62, -41), (-65, -45), (-68, -50), (-68, -54),
     (-72, -54), (-73, -45), (-73, -37), (-71, -30), (-70, -20),
     (-75, -15), (-79, -8), (-81, -4), (-80, 2)],
    # Africa
    [(-6, 35), (10, 37), (20, 32), (30, 31), (35, 28), (43, 12), (51, 11),
     (48, 2), (42, -2), (40, -10), (35, -18), (32, -26), (28, -33),
     (20, -35), (17, -29), (14, -22), (12, -15), (13, -8), (9, 4), (4, 6),
     (-8, 5), (-13, 8), (-17, 15), (-16, 21), (-10, 31)],
    # Eurasia
    [(-10, 36), (-9, 43), (-2, 48), (-4, 49), (0, 50), (3, 52), (8, 54),
     (8, 58), (5, 60), (10, 64), (18, 69), (28, 71), (40, 68), (45, 68),
     (55, 69), (68, 73), (80, 73), (95, 76), (110, 74), (125, 72),
     (140, 72), (155, 70), (170, 67), (178, 65), (178, 62), (170, 60),
     (162, 56), (158, 52), (150, 59), (142, 55), (140, 40), (135, 35),
     (129, 33), (127, 39), (122, 38), (120, 32), (122, 25), (115, 23),
     (109, 20), (105, 10), (104, 9), (100, 8), (98, 12), (94, 17),
     (91, 22), (88, 22), (85, 20), (80, 15), (77, 8), (74, 20), (70, 22),
     (66, 25), (61, 25), (57, 26), (54, 26), (52, 25), (50, 29), (48, 30),
     (44, 29), (40, 31), (36, 36), (30, 36), (27, 37), (23, 36), (19, 40),
     (15, 44), (12, 44), (10, 44), (7, 44), (3, 43), (0, 39), (-2, 37),
     (-6, 36), (-9, 37)],
    # Australia
    [(113, -22), (114, -28), (115, -33), (118, -35), (124, -33),
     (129, -32), (132, -32), (135, -35), (138, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (151, -24),
     (146, -19), (142, -15), (142, -11), (140, -17), (136, -15),
     (132, -12), (129, -14), (126, -14), (122, -17), (117, -20)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (0, 53), (1, 51)],
    # Japan
    [(130, 31), (133, 34), (137, 35), (140, 36), (141, 40), (142, 44),
     (145, 44), (143, 40), (140, 38), (138, 35), (134, 33)],
    # Borneo
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (112, -3)],
    # Sumatra
    [(95, 5), (100, 0), (104, -4), (106, -6), (103, -3), (99, 2)],
    # New Guinea
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -10), (147, -9),
     (142, -8), (136, -7), (131, -3)],
    # New Zealand
    [(167, -45), (172, -41), (175, -38), (178, -38), (176, -41),
     (173, -44), (168, -47)],
]

# (number, label, lon, lat, leader-offset or None). Leader pins sit too
# close to a neighbour at true position, so the numbered circle is offset
# and joined by a thin line to a dot at the true spot.
PINS = [
    (1, "Antalya", 30.7, 36.9, None),
    (2, "Riyadh", 46.7, 24.6, None),
    (3, "Jun\u00edn", -75.2, -11.2, None),
    (4, "Hormuz", 56.3, 27.1, (10, -18)),
    (5, "Kryvyi Rih", 33.4, 47.9, (0, -20)),
    (6, "Davao", 125.6, 7.1, None),
    (8, "Las Vegas", -115.1, 36.2, None),
    (9, "Wellington", 174.8, -41.3, None),
    (10, "Warsaw", 21.0, 52.2, None),
    (11, "Sejong", 127.3, 36.5, None),
    (13, "Delhi", 77.2, 28.6, None),
    (24, "Barnham", 0.7, 52.4, None),
    (26, "Sydney", 151.2, -33.9, None),
    (32, "Johannesburg", 28.0, -26.2, None),
    (35, "Accra", -0.2, 5.6, None),
]

LEGEND_TEXT = ("Pins: " + " \u00b7 ".join(
    f"{n} {label}" for n, label, _lo, _la, _off in PINS))


# ---- layout ------------------------------------------------------------
MARGIN = 22
CW = 980                       # content width
CX = MARGIN

WARN = []


def warn(msg):
    WARN.append(msg)
    print("WARN:", msg)


def paint_strip(img, scene_fn, rng, x, y, w, h):
    """Render a scene onto its own tile, then paste it with rounded top
    corners (bottom corners square, so it meets the card body cleanly)."""
    tile = Image.new("RGB", (w, h), (255, 255, 255))
    td = ImageDraw.Draw(tile)
    scene_fn(td, rng, 0, 0, w, h)
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([0, 0, w - 1, h + 11], radius=6, fill=255)
    img.paste(tile, (x, y), mask)


def card_frame(draw, x, y, w, h):
    draw.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=6,
                           fill=CARD, outline=BORDER, width=1)


def draw_header(draw):
    eyebrow = font(SANS_B, 11)
    draw.text((CX, 14), "THE WORLD NEWS LEDGER", font=eyebrow, fill=INK)
    right = "ONE DAY \u00b7 ONE PAGE \u00b7 35 STORIES"
    draw.text((CX + CW - text_w(draw, right, eyebrow), 14), right,
              font=eyebrow, fill=RED)
    size = 54
    mast = font(SERIF_B, size)
    title = "Saturday 21 November 2026"
    while text_w(draw, title, mast) > 960 and size > 40:
        size -= 2
        mast = font(SERIF_B, size)
    draw.text(((W - text_w(draw, title, mast)) / 2, 28), title,
              font=mast, fill=INK)
    strap_size = 13
    strap = font(SERIF, strap_size)
    while text_w(draw, STRAPLINE, strap) > 960 and strap_size > 10:
        strap_size -= 1
        strap = font(SERIF, strap_size)
    draw.text(((W - text_w(draw, STRAPLINE, strap)) / 2, 90), STRAPLINE,
              font=strap, fill=INK)
    draw.line([(CX, 110), (CX + CW, 110)], fill=INK, width=2)
    draw.line([(CX, 114), (CX + CW, 114)], fill=INK, width=1)


def draw_chips(draw):
    chip_w, gap, y, h = 160, 4, 120, 32
    x0 = CX + (CW - (6 * chip_w + 5 * gap)) // 2
    num_f, lab_f = font(SANS_B, 14), font(SANS, 9)
    for i, (num, lab) in enumerate(CHIPS):
        x = x0 + i * (chip_w + gap)
        draw.rounded_rectangle([x, y, x + chip_w - 1, y + h - 1], radius=7,
                               fill=(255, 255, 255), outline=CHIP_LINE,
                               width=1)
        unit = (text_w(draw, num, num_f) + 5 + text_w(draw, lab, lab_f))
        sx = x + (chip_w - unit) / 2
        if unit > chip_w - 8:
            warn(f"chip {i + 1} too wide: {unit:.0f}px")
        draw.text((sx, y + 8), num, font=num_f, fill=RED)
        draw.text((sx + text_w(draw, num, num_f) + 5, y + 11), lab,
                  font=lab_f, fill=MUTED)


def draw_regions(draw):
    f = font(SANS_B, 10)
    sep = " \u00b7 "
    sep_w = text_w(draw, sep, f)
    parts = [(text_w(draw, f"{name} {n}", f), name, n, col)
             for name, n, col in REGIONS]
    total = sum(p[0] + 12 for p in parts) + sep_w * (len(parts) - 1)
    x = CX + (CW - total) / 2
    y = 160
    for i, (lw, name, n, col) in enumerate(parts):
        draw.ellipse([x, y + 3, x + 7, y + 10], fill=col)
        draw.text((x + 11, y), f"{name} {n}", font=f, fill=INK)
        x += lw + 12
        if i < len(parts) - 1:
            draw.text((x, y), sep, font=f, fill=MUTED)
            x += sep_w
    if sum(n for _, n, _ in REGIONS) != 35:
        warn("region counts do not sum to 35")


def draw_hero(img, draw, rng, hero, x, y):
    w, h, art_h = 320, 174, 78
    card_frame(draw, x, y, w, h)
    paint_strip(img, hero["scene"], rng, x + 1, y + 1, w - 2, art_h)
    colour = TAG[hero["kind"]]
    # number badge straddling the art / text boundary
    bx, by, br = x + 16, y + art_h, 9
    draw.ellipse([bx - br, by - br, bx + br, by + br], fill=RED,
                 outline=(255, 255, 255), width=1)
    num_f = font(SANS_B, 10)
    num = str(hero["num"])
    draw.text((bx - text_w(draw, num, num_f) / 2, by - 8), num,
              font=num_f, fill=(255, 255, 255))
    tag_f = font(SANS_B, 9)
    draw.text((x + 32, y + art_h + 6),
              f"{hero['tag']} \u00b7 {hero['place']}", font=tag_f,
              fill=colour)
    head_f = font(SERIF_B, 16)
    lines = wrap(draw, hero["head"], head_f, w - 20)
    if len(lines) > 2:
        warn(f"hero {hero['num']} headline wraps to {len(lines)} lines")
    hy = y + art_h + 22
    for ln in lines[:2]:
        draw.text((x + 10, hy), ln, font=head_f, fill=INK)
        hy += 18
    deck_f = font(SANS, 9)
    dlines = wrap(draw, hero["deck"], deck_f, w - 20)
    if len(dlines) > 2:
        warn(f"hero {hero['num']} deck wraps to {len(dlines)} lines")
    dy = hy + 3
    for ln in dlines[:2]:
        draw.text((x + 10, dy), ln, font=deck_f, fill=(60, 60, 60))
        dy += 11
    draw.text((x + 10, y + h - 13), hero["source"], font=font(SANS, 8),
              fill=MUTED)


def draw_small_card(img, draw, rng, card, x, y):
    w, h, strip_h = 189, 142, 46
    card_frame(draw, x, y, w, h)
    paint_strip(img, card["scene"], rng, x + 1, y + 1, w - 2, strip_h)
    colour = TAG[card["kind"]]
    num_f, tag_f = font(SANS_B, 13), font(SANS_B, 9)
    num = str(card["num"])
    draw.text((x + 8, y + strip_h + 4), num, font=num_f, fill=colour)
    draw.text((x + 8 + text_w(draw, num, num_f) + 5, y + strip_h + 7),
              card["tag"], font=tag_f, fill=colour)
    head_f = font(SERIF_B, 12)
    lines = wrap(draw, card["head"], head_f, w - 16)
    if len(lines) > 2:
        warn(f"card {card['num']} headline wraps to {len(lines)} lines")
    hy = y + strip_h + 22
    for ln in lines[:2]:
        draw.text((x + 8, hy), ln, font=head_f, fill=INK)
        hy += 15
    deck_f = font(SANS, 9)
    dlines = wrap(draw, card["deck"], deck_f, w - 16)
    if len(dlines) > 2:
        warn(f"card {card['num']} deck wraps to {len(dlines)} lines")
    dy = hy + 3
    for ln in dlines[:2]:
        draw.text((x + 8, dy), ln, font=deck_f, fill=(60, 60, 60))
        dy += 11
    draw.text((x + 8, y + h - 12), card["source"], font=font(SANS, 7),
              fill=MUTED)


def project(mx, my, mw, mh, lon, lat):
    px = mx + (lon + 180) / 360 * mw
    py = my + (75 - lat) / 135 * mh
    return px, py


def draw_map_panel(draw):
    x, y, w, h = CX, 658, 430, 224
    card_frame(draw, x, y, w, h)
    draw.text((x + 10, y + 8), "WHERE IT HAPPENED",
              font=font(SANS_B, 12), fill=INK)
    draw.text((x + 10, y + 25),
              "Numbered pins mark the dateline of each story.",
              font=font(SANS, 8), fill=MUTED)
    mx, my, mw = x + 8, y + 40, w - 16
    leg_f = font(SANS, 8)
    legend_lines = wrap(draw, LEGEND_TEXT, leg_f, mw)
    legend_h = len(legend_lines) * 11 + 4
    mh = h - 40 - legend_h - 6
    # ocean + graticule
    draw.rectangle([mx, my, mx + mw, my + mh], fill=(220, 234, 242))
    for lon in range(-150, 181, 30):
        gx = mx + (lon + 180) / 360 * mw
        draw.line([(gx, my), (gx, my + mh)], fill=(196, 216, 228), width=1)
    for lat in range(-60, 76, 30):
        gy = my + (75 - lat) / 135 * mh
        draw.line([(mx, gy), (mx + mw, gy)], fill=(196, 216, 228), width=1)
    # continents
    for poly in CONTINENTS:
        pts = [project(mx, my, mw, mh, lo, la) for lo, la in poly]
        draw.polygon(pts, fill=(216, 226, 196), outline=(178, 196, 160))
    # pins (leader pins get a dot at the true spot + a line to the circle)
    pin_f = font(SANS_B, 8)
    placed = []
    for num, label, lon, lat, off in PINS:
        tx, ty = project(mx, my, mw, mh, lon, lat)
        cx, cy = tx, ty
        if off:
            cx, cy = tx + off[0], ty + off[1]
            draw.line([(tx, ty), (cx, cy)], fill=RED, width=1)
            draw.ellipse([tx - 3, ty - 3, tx + 3, ty + 3], fill=RED)
        draw.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=RED,
                     outline=(255, 255, 255), width=1)
        s = str(num)
        draw.text((cx - text_w(draw, s, pin_f) / 2, cy - 6), s,
                  font=pin_f, fill=(255, 255, 255))
        placed.append((num, cx, cy))
    for i, (n1, x1, y1) in enumerate(placed):
        for n2, x2, y2 in placed[i + 1:]:
            d = math.hypot(x1 - x2, y1 - y2)
            if d < 15:
                warn(f"map pins {n1} and {n2} only {d:.0f}px apart")
    ly = my + mh + 5
    for ln in legend_lines:
        draw.text((mx, ly), ln, font=leg_f, fill=(70, 70, 70))
        ly += 11
    if ly > y + h - 2:
        warn("map legend overflows its panel")


def draw_list_panel(draw):
    x, y, w, h = CX + 440, 658, 540, 224
    card_frame(draw, x, y, w, h)
    draw.text((x + 10, y + 8), "ALSO ON SATURDAY 21 NOVEMBER 2026",
              font=font(SANS_B, 12), fill=INK)
    draw.text((x + 10, y + 25), "22 more stories, numbered 14\u201335.",
              font=font(SANS, 8), fill=MUTED)
    item_f, num_f = font(SANS, 8), font(SANS_B, 8)
    iy = y + 40
    for num, text in LIST_ITEMS:
        label = f"{num}. "
        lw = text_w(draw, label, num_f)
        total = lw + text_w(draw, text, item_f)
        if total > w - 20:
            warn(f"list #{num} overflows by {total - (w - 20):.0f}px")
        draw.text((x + 10, iy), label, font=num_f, fill=RED)
        draw.text((x + 10 + lw, iy), text, font=item_f, fill=(40, 40, 40))
        iy += 8
    if iy > y + h - 2:
        warn("story list overflows its panel")


def draw_date_check(draw):
    x, y, w, h = CX, 888, CW, 60
    draw.rounded_rectangle([x, y, x + w - 1, y + h - 1], radius=6,
                           fill=DATE_BG, outline=DATE_LINE, width=1)
    body_f = font(SANS, 9)
    lead_f = font(SANS_B, 9)
    lead = "DATE CHECK \u2014 "
    lead_w = text_w(draw, lead, lead_f)
    inner = w - 20
    # paragraph 1: first line starts after the bold lead-in
    words = DATE_CHECK_1.split(" ")
    lines, cur, first = [], "", True
    for word in words:
        limit = inner - lead_w if first else inner
        trial = f"{cur} {word}".strip()
        if text_w(draw, trial, body_f) <= limit or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur, first = word, False
    if cur:
        lines.append(cur)
    lines += wrap(draw, DATE_CHECK_2, body_f, inner)
    lines += wrap(draw, DATE_CHECK_3, body_f, inner)
    if len(lines) > 4:
        warn(f"DATE CHECK needs {len(lines)} lines, box fits 4")
    ly = y + 6
    draw.text((x + 10, ly), lead, font=lead_f, fill=RED)
    draw.text((x + 10 + lead_w, ly), lines[0], font=body_f,
              fill=(80, 30, 25))
    ly += 12
    for ln in lines[1:4]:
        draw.text((x + 10, ly), ln, font=body_f, fill=(80, 30, 25))
        ly += 12


def draw_footer(draw):
    f1 = font(SANS_B, 10)
    line1 = ("Every story here happened, or was first reported, on "
             "Saturday 21 November 2026. Sources are named beside each "
             "story.")
    draw.text(((W - text_w(draw, line1, f1)) / 2, 954), line1, font=f1,
              fill=INK)
    f2 = font(SANS, 9)
    line2 = ("Las Vegas motorsport sessions ran on Friday evening local "
             "time \u2014 Saturday in UTC. \u201cClaim\u201d stories are "
             "labelled as claims; scheduled events are labelled as due.")
    draw.text(((W - text_w(draw, line2, f2)) / 2, 968), line2, font=f2,
              fill=MUTED)
    f3 = font(SANS, 8)
    line3 = ("THE WORLD NEWS LEDGER \u00b7 35 STORIES \u00b7 7 REGIONS "
             "\u00b7 DRAWN 21 NOVEMBER 2026")
    draw.text(((W - text_w(draw, line3, f3)) / 2, 982), line3, font=f3,
              fill=MUTED)


def main():
    rng = random.Random(SEED)
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    draw_header(draw)
    draw_chips(draw)
    draw_regions(draw)
    hero_y = 182
    for i, hero in enumerate(HEROES):
        draw_hero(img, draw, rng, hero, CX + i * 330, hero_y)
    for row in range(2):
        for col in range(5):
            card = CARDS[row * 5 + col]
            draw_small_card(img, draw, rng, card, CX + col * 197,
                            362 + row * 148)
    draw_map_panel(draw)
    draw_list_panel(draw)
    draw_date_check(draw)
    draw_footer(draw)
    img.save(OUT, "PNG")
    data = open(OUT, "rb").read()
    print(f"saved {OUT}: {len(data)} bytes")
    print("sha256:", hashlib.sha256(data).hexdigest())
    if WARN:
        print(f"FIT: {len(WARN)} warning(s) \u2014 see above")
    else:
        print("FIT OK: no overflows, all counts check out")


if __name__ == "__main__":
    main()
