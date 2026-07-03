import os

from PIL import ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS_DIR = os.path.join(HERE, "..", "assets", "fonts")

FONTS = {
    "title": os.path.join(FONTS_DIR, "Anton-Regular.ttf"),
    "extrabold": os.path.join(FONTS_DIR, "Barlow-ExtraBold.ttf"),
    "bold": os.path.join(FONTS_DIR, "Barlow-Bold.ttf"),
    "semibold": os.path.join(FONTS_DIR, "Barlow-SemiBold.ttf"),
    "regular": os.path.join(FONTS_DIR, "Barlow-Regular.ttf"),
}


def load_font(kind, size):
    return ImageFont.truetype(FONTS[kind], size)


def wrap_text(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        w = draw.textbbox((0, 0), candidate, font=font)[2]
        if w <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_text(draw, text, kind, max_width, max_height, max_size, min_size, line_spacing=1.18, step=2):
    best_font, best_lines = None, None
    for size in range(max_size, min_size - 1, -step):
        font = load_font(kind, size)
        lines = wrap_text(draw, text, font, max_width)
        line_h = draw.textbbox((0, 0), "Ag", font=font)[3] * line_spacing
        total_h = line_h * len(lines)
        best_font, best_lines = font, lines
        if total_h <= max_height:
            return font, lines, line_h
    font = load_font(kind, min_size)
    lines = wrap_text(draw, text, font, max_width)
    line_h = draw.textbbox((0, 0), "Ag", font=font)[3] * line_spacing
    return font, lines, line_h


def draw_centered_multiline(draw, lines, font, center_x, top_y, line_h, fill, align="center", box_left=None, box_right=None):
    y = top_y
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        if align == "center":
            x = center_x - w / 2
        elif align == "left":
            x = box_left
        else:
            x = box_right - w
        draw.text((x, y), line, font=font, fill=fill)
        y += line_h
    return y
