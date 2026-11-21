"""Catalogue photo of an impossible gadget: WiToast.

A stainless-steel toaster that toasts the Wi-Fi password onto bread.
Draws one 1024x1024 catalogue photograph to /output/entry.png.
Pure stdlib + Pillow, deterministic (fixed seeds, no network).
"""

import math
import os
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
OUT = "/output/entry.png"

CENTRE = (251, 248, 240)   # warm off-white, centre of the backdrop
EDGE = (231, 223, 207)     # slightly darker toward the edges
BODY = (203, 207, 212)     # brushed silver
DARK = (42, 44, 46)        # slot / lever / feet
BROWN = (92, 58, 26)       # toasted text and wi-fi symbol
CRUST = (138, 90, 36)
CRUMB = (217, 164, 91)
GREY_TEXT = (58, 61, 66)
ORANGE = (255, 122, 26)


def load_font(size, bold=False):
    names = ["DejaVuSans-Bold.ttf", "DejaVuSans.ttf"] if bold else \
        ["DejaVuSans.ttf", "DejaVuSans-Bold.ttf"]
    bases = [
        "/usr/share/fonts/truetype/dejavu/",
        "/usr/share/fonts/TTF/",
        "/usr/share/fonts/",
    ]
    for base in bases:
        for name in names:
            try:
                return ImageFont.truetype(base + name, size)
            except Exception:
                continue
    return ImageFont.load_default()


def radial_background():
    # small radial falloff mask, upscaled for a smooth studio backdrop
    s = 256
    cx = cy = s / 2
    maxd = math.hypot(cx, cy)
    mask = Image.new("L", (s, s), 0)
    px = mask.load()
    for y in range(s):
        for x in range(s):
            d = math.hypot(x - cx, y - cy) / maxd
            px[x, y] = int(255 * max(0.0, 1.0 - d * d))
    mask = mask.resize((W, H), Image.BICUBIC)
    base = Image.new("RGB", (W, H), EDGE)
    centre = Image.new("RGB", (W, H), CENTRE)
    return Image.composite(centre, base, mask)


def draw_toast():
    # one slice on a transparent layer, 220x260; rotated by the caller
    tw, th = 220, 260
    layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # crust border, then golden crumb
    d.rounded_rectangle([4, 4, tw - 4, th - 4], radius=34,
                        fill=CRUST + (255,))
    d.rounded_rectangle([14, 14, tw - 14, th - 14], radius=28,
                        fill=CRUMB + (255,))
    # tiny toasted speckles (seeded)
    rng = random.Random(7)
    for _ in range(26):
        x = rng.randint(24, tw - 24)
        y = rng.randint(24, th - 24)
        r = rng.randint(2, 4)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(170, 110, 45, 90))
    # wi-fi symbol: three arcs above a dot, centred (110, 96)
    # arcs drawn bolder so the symbol reads at catalogue size
    cx, cy = 110, 96
    for r in (16, 28, 40):
        d.arc([cx - r, cy - r, cx + r, cy + r], start=225, end=315,
              fill=BROWN + (255,), width=6)
    d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=BROWN + (255,))
    # faint toasted edge along the top of the slice for depth
    d.arc([10, 10, tw - 10, th - 10], start=180, end=360,
          fill=(150, 100, 40, 70), width=3)
    # the password, toasted in dark brown
    f1 = load_font(34, bold=True)
    f2 = load_font(27, bold=True)
    d.text((cx, 128), "WiFi", font=f1, fill=BROWN + (255,), anchor="ma")
    d.text((cx, 166), "hunter2", font=f2, fill=BROWN + (255,), anchor="ma")
    return layer


def main():
    img = radial_background()
    d = ImageDraw.Draw(img, "RGBA")
    # thin horizontal surface line near the bottom
    d.line([(90, 778), (934, 778)], fill=(201, 192, 175, 255), width=2)
    # soft elliptical contact shadow beneath the toaster
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([300, 774, 724, 812], fill=(60, 50, 35, 70))
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img.convert("RGBA"), shadow)
    d = ImageDraw.Draw(img, "RGBA")
    # toaster body: brushed-silver rounded rectangle
    bx0, by0, bx1, by1 = 322, 460, 702, 760
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=42, fill=BODY + (255,))
    # vertical brushed-metal streaks (seeded, central safe area)
    rng = random.Random(1234)
    for _ in range(55):
        x = rng.randint(340, 684)
        light = rng.random() < 0.5
        col = (226, 230, 235, 34) if light else (168, 172, 180, 30)
        d.line([(x, 472), (x, 748)], fill=col, width=1)
    # soft highlight along the top edge
    d.rounded_rectangle([330, 464, 694, 480], radius=8,
                        fill=(237, 239, 242, 110))
    # two small black feet under the body
    d.rounded_rectangle([360, 760, 392, 774], radius=4, fill=DARK + (255,))
    d.rounded_rectangle([632, 760, 664, 774], radius=4, fill=DARK + (255,))
    # toast, tilted a few degrees, bottom edge at the slot
    toast = draw_toast()
    toast = toast.rotate(-7, expand=True, resample=Image.BICUBIC)
    px = 512 - toast.width // 2
    py = 490 - toast.height
    img.alpha_composite(toast, (px, py))
    d = ImageDraw.Draw(img, "RGBA")
    # dark slot across the top (drawn over the toast base so it reads as in)
    d.rounded_rectangle([360, 470, 664, 492], radius=9, fill=DARK + (255,))
    # black lever on the right side
    d.rounded_rectangle([700, 556, 730, 570], radius=7, fill=DARK + (255,))
    d.ellipse([726, 554, 742, 572], fill=DARK + (255,))
    # brand name above the dial
    fb = load_font(34, bold=True)
    d.text((512, 618), "WiToast", font=fb, fill=GREY_TEXT + (255,),
           anchor="ma")
    # small round dial, a clock face with a hand
    dcx, dcy, dr = 465, 695, 26
    d.ellipse([dcx - dr, dcy - dr, dcx + dr, dcy + dr],
              fill=(245, 240, 230, 255), outline=DARK + (255,), width=3)
    for ang in (0, 90, 180, 270):
        a = math.radians(ang)
        x0 = dcx + int((dr - 4) * math.sin(a))
        y0 = dcy - int((dr - 4) * math.cos(a))
        x1 = dcx + int((dr - 9) * math.sin(a))
        y1 = dcy - int((dr - 9) * math.cos(a))
        d.line([(x0, y0), (x1, y1)], fill=DARK + (255,), width=2)
    ha = math.radians(60)  # hand pointing to ~2 o'clock
    hx = dcx + int(17 * math.sin(ha))
    hy = dcy - int(17 * math.cos(ha))
    d.line([(dcx, dcy), (hx, hy)], fill=DARK + (255,), width=3)
    d.ellipse([dcx - 3, dcy - 3, dcx + 3, dcy + 3], fill=DARK + (255,))
    # small round orange indicator light to the dial's right
    lcx, lcy, lr = 548, 695, 11
    d.ellipse([lcx - lr, lcy - lr, lcx + lr, lcy + lr],
              fill=ORANGE + (255,), outline=DARK + (255,), width=2)
    d.ellipse([lcx - 5, lcy - 6, lcx + 1, lcy - 1],
              fill=(255, 220, 180, 255))
    # save
    os.makedirs("/output", exist_ok=True)
    img.convert("RGB").save(OUT, "PNG")


if __name__ == "__main__":
    main()
