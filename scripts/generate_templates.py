import math
import os

from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(HERE, "..", "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

W, H = 1080, 1350

NAVY_TOP = (10, 17, 40)
NAVY_BOTTOM = (4, 6, 14)
GOLD = (232, 184, 75)
GOLD_DIM = (120, 96, 45)


def vertical_gradient(w, h, top, bottom):
    img = Image.new("RGB", (w, h), top)
    px = img.load()
    for y in range(h):
        t = y / (h - 1)
        r = int(top[0] + (bottom[0] - top[0]) * t)
        g = int(top[1] + (bottom[1] - top[1]) * t)
        b = int(top[2] + (bottom[2] - top[2]) * t)
        for x in range(w):
            px[x, y] = (r, g, b)
    return img


def add_vignette(img, strength=110):
    w, h = img.size
    vig = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vig)
    cx, cy = w / 2, h / 2
    max_r = math.hypot(cx, cy)
    steps = 60
    for i in range(steps):
        t = i / steps
        r = max_r * (1 - t)
        alpha = int(strength * t)
        vd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=alpha)
    vig = vig.filter(ImageFilter.GaussianBlur(80))
    dark = Image.new("RGB", (w, h), (0, 0, 0))
    return Image.composite(dark, img, Image.eval(vig, lambda p: 255 - p))


def draw_star(draw, cx, cy, r_outer, r_inner, fill=None, outline=None, width=2):
    points = []
    for i in range(10):
        angle = math.pi / 2 + i * math.pi / 5
        r = r_outer if i % 2 == 0 else r_inner
        points.append((cx + r * math.cos(angle), cy - r * math.sin(angle)))
    draw.polygon(points, fill=fill, outline=outline, width=width)


def rounded_rect(draw, box, radius, outline, width, fill=None):
    draw.rounded_rectangle(box, radius=radius, outline=outline, width=width, fill=fill)


def gold_rgba(alpha):
    return (GOLD[0], GOLD[1], GOLD[2], alpha)


def base_canvas():
    base = vertical_gradient(W, H, NAVY_TOP, NAVY_BOTTOM)
    base = add_vignette(base, strength=130)
    img = base.convert("RGBA")

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)

    # outer thin gold frame
    margin = 42
    od.rectangle(
        [margin, margin, W - margin, H - margin],
        outline=gold_rgba(150),
        width=2,
    )
    # corner ticks
    tick = 26
    for cx0, cy0, dx, dy in [
        (margin, margin, 1, 1),
        (W - margin, margin, -1, 1),
        (margin, H - margin, 1, -1),
        (W - margin, H - margin, -1, -1),
    ]:
        od.line([(cx0, cy0), (cx0 + dx * tick, cy0)], fill=gold_rgba(220), width=3)
        od.line([(cx0, cy0), (cx0, cy0 + dy * tick)], fill=gold_rgba(220), width=3)

    # faded watermark star, upper area, large and subtle
    star_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(star_layer)
    draw_star(sd, W / 2, 250, 230, 95, fill=gold_rgba(16))
    star_layer = star_layer.filter(ImageFilter.GaussianBlur(2))
    overlay = Image.alpha_composite(overlay, star_layer)
    od = ImageDraw.Draw(overlay)

    # small solid accent star, top center, above header text zone
    draw_star(od, W / 2, 118, 26, 11, fill=gold_rgba(255))

    img = Image.alpha_composite(img, overlay)
    return img


def make_questao_template():
    img = base_canvas()
    od = ImageDraw.Draw(img)

    # header divider
    od.line([(140, 190), (W - 140, 190)], fill=gold_rgba(150), width=2)

    # question panel outline (text drawn later by render script)
    panel_box = [90, 380, W - 90, 760]
    rounded_rect(od, panel_box, radius=22, outline=gold_rgba(210), width=3)

    # 4 alternative slots
    slot_h = 96
    gap = 22
    top = 820
    for i in range(4):
        y0 = top + i * (slot_h + gap)
        y1 = y0 + slot_h
        rounded_rect(od, [90, y0, W - 90, y1], radius=16, outline=gold_rgba(150), width=2)

    # footer divider + watermark zone marker
    od.line([(140, H - 90), (W - 140, H - 90)], fill=gold_rgba(120), width=2)

    img.convert("RGB").save(os.path.join(ASSETS_DIR, "template_questao.png"))


def make_frase_template():
    img = base_canvas()
    od = ImageDraw.Draw(img)

    od.line([(140, 190), (W - 140, 190)], fill=gold_rgba(150), width=2)

    # soft radial glow behind quote area
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([W / 2 - 420, 560 - 260, W / 2 + 420, 560 + 260], fill=gold_rgba(22))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img = Image.alpha_composite(img, glow)
    od = ImageDraw.Draw(img)

    # stylized quote-mark accent (two comma-like blobs, drawn as shapes)
    for dx in (-46, 6):
        cx = W / 2 + dx
        od.ellipse([cx, 300, cx + 26, 326], fill=gold_rgba(200))
        od.polygon(
            [(cx, 313), (cx + 26, 300), (cx + 10, 350)],
            fill=gold_rgba(200),
        )

    # divider line above the quote text zone
    od.line([(220, 470), (W - 220, 470)], fill=gold_rgba(160), width=2)

    od.line([(140, H - 90), (W - 140, H - 90)], fill=gold_rgba(120), width=2)

    img.convert("RGB").save(os.path.join(ASSETS_DIR, "template_frase.png"))


if __name__ == "__main__":
    make_questao_template()
    make_frase_template()
    print("OK: template_questao.png + template_frase.png gerados em", ASSETS_DIR)
