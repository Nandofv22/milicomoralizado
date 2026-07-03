import math
import os

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(HERE, "..", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

W, H = 1080, 1350

BG = (6, 6, 9)
BLUE = (40, 110, 235)
RED = (222, 32, 32)
WHITE = (245, 245, 245)


def add_grain(img_rgb, amount=7):
    arr = np.array(img_rgb).astype(np.int16)
    noise = np.random.randint(-amount, amount + 1, arr.shape[:2] + (1,))
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, "RGB")


def add_corner_glow(base_rgba, color, cx, cy, radius, alpha, blur):
    glow = Image.new("RGBA", base_rgba.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color + (alpha,))
    glow = glow.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(base_rgba, glow)


def base_canvas():
    img = Image.new("RGB", (W, H), BG)
    img = add_grain(img, amount=6)
    rgba = img.convert("RGBA")

    # siren-light glows: blue bleeding from top-right, red bleeding from bottom-left
    rgba = add_corner_glow(rgba, BLUE, W * 1.02, -H * 0.05, radius=W * 0.62, alpha=150, blur=170)
    rgba = add_corner_glow(rgba, RED, -W * 0.05, H * 1.05, radius=W * 0.62, alpha=140, blur=170)
    # secondary tighter, brighter cores for a bit of realism
    rgba = add_corner_glow(rgba, BLUE, W * 0.98, H * 0.02, radius=W * 0.22, alpha=110, blur=90)
    rgba = add_corner_glow(rgba, RED, W * 0.02, H * 0.98, radius=W * 0.22, alpha=100, blur=90)

    return rgba


def skull_mask(size):
    """Returns an RGBA image of a flat white skull silhouette, size x size."""
    S = size
    mask = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(mask)

    def pt(nx, ny):
        return (nx * S, ny * S)

    outline = [
        pt(0.50, 0.00), pt(0.72, 0.03), pt(0.87, 0.14), pt(0.97, 0.34),
        pt(0.94, 0.52), pt(0.83, 0.60), pt(0.81, 0.70), pt(0.71, 0.79),
        pt(0.60, 0.85), pt(0.50, 0.80), pt(0.40, 0.85), pt(0.29, 0.79),
        pt(0.19, 0.70), pt(0.17, 0.60), pt(0.06, 0.52), pt(0.03, 0.34),
        pt(0.13, 0.14), pt(0.28, 0.03),
    ]
    d.polygon(outline, fill=255)

    d.ellipse([pt(0.20, 0.32)[0], pt(0.20, 0.32)[1], pt(0.44, 0.56)[0], pt(0.44, 0.56)[1]], fill=0)
    d.ellipse([pt(0.56, 0.32)[0], pt(0.56, 0.32)[1], pt(0.80, 0.56)[0], pt(0.80, 0.56)[1]], fill=0)
    d.polygon([pt(0.50, 0.56), pt(0.46, 0.66), pt(0.54, 0.66)], fill=0)
    for tx in (0.37, 0.46, 0.55, 0.64):
        d.rectangle([pt(tx, 0.74)[0], pt(tx, 0.74)[1], pt(tx + 0.02, 0.83)[0], pt(tx + 0.02, 0.83)[1]], fill=0)

    rgba = Image.new("RGBA", (S, S), WHITE + (255,))
    rgba.putalpha(mask)
    return rgba


def draw_skull(base_rgba, cx, cy, height):
    S = int(height / 0.85)
    skull = skull_mask(S).resize((S, S), Image.LANCZOS)
    x = int(cx - S / 2)
    y = int(cy - S / 2)
    base_rgba.paste(skull, (x, y), skull)


def rounded_panel(base_rgba, box, radius, fill_alpha=30, outline_alpha=70):
    layer = Image.new("RGBA", base_rgba.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    ld.rounded_rectangle(box, radius=radius, fill=(255, 255, 255, fill_alpha), outline=(255, 255, 255, outline_alpha), width=2)
    return Image.alpha_composite(base_rgba, layer)


def make_questao_template():
    img = base_canvas()
    draw_skull(img, W / 2, 200, 150)

    # panel behind the "Verdadeiro ou Falso?" callout
    img = rounded_panel(img, [230, 840, W - 230, 960], radius=24)

    img.convert("RGB").save(os.path.join(ASSETS_DIR, "template_questao.png"))


def make_frase_template():
    img = base_canvas()
    draw_skull(img, W / 2, 200, 150)

    img.convert("RGB").save(os.path.join(ASSETS_DIR, "template_frase.png"))


if __name__ == "__main__":
    make_questao_template()
    make_frase_template()
    print("OK: template_questao.png + template_frase.png gerados em", ASSETS_DIR)
