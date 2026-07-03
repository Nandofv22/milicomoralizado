import argparse
import datetime
import json
import os

from PIL import Image, ImageDraw

import state
from text_utils import draw_centered_multiline, fit_text, load_font

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA_PATH = os.path.join(ROOT, "data", "frases.json")
TEMPLATE_PATH = os.path.join(ROOT, "assets", "template_frase.png")
OUTPUT_DIR = os.path.join(ROOT, "output")

GOLD = (232, 184, 75)
LIGHT = (245, 245, 245)
DIM = (190, 190, 190)

W, H = 1080, 1350

TEMA_LABELS = {
    "disciplina": "DISCIPLINA",
    "foco": "FOCO",
    "resiliencia": "RESILIENCIA",
    "rotina": "ROTINA DE ESTUDOS",
    "sacrificio": "SACRIFICIO",
    "objetivo": "A FARDA",
    "fe": "FE E PROPOSITO",
}

HASHTAGS = (
    "#concurseiro #motivacaopolicial #vempraPM #pmba #policiamilitar "
    "#foconoconcurso #disciplina #concursopolicial"
)


def load_bank():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)["frases"]


def render(item):
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    title_font = load_font("title", 50)
    draw_centered_multiline(draw, ["FRASE DO DIA"], title_font, W / 2, 145, 0, GOLD)

    tag_font = load_font("semibold", 26)
    tag = TEMA_LABELS.get(item.get("tema", ""), "MOTIVACAO")
    draw_centered_multiline(draw, [tag], tag_font, W / 2, 205, 0, DIM)

    zone_top, zone_bottom = 520, 1200
    font, lines, line_h = fit_text(
        draw,
        item["texto"],
        "extrabold",
        W - 260,
        zone_bottom - zone_top,
        62,
        30,
    )
    block_h = line_h * len(lines)
    start_y = zone_top + (zone_bottom - zone_top - block_h) / 2
    draw_centered_multiline(draw, lines, font, W / 2, start_y, line_h, LIGHT)

    handle_font = load_font("semibold", 24)
    draw_centered_multiline(draw, ["@milicomoralizado"], handle_font, W / 2, H - 78, 0, GOLD)

    return img


def build_caption(item):
    return f"{item['texto']}\n\n\U0001F6A8 Marca aquele concurseiro que precisa ler isso hoje.\n\n{HASHTAGS}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None, help="YYYY-MM-DD, default today")
    parser.add_argument("--index", type=int, default=None, help="override bank index")
    args = parser.parse_args()

    date_str = args.date or datetime.date.today().isoformat()
    bank = load_bank()
    idx = args.index if args.index is not None else state.current_index("frase_index", len(bank))
    item = bank[idx]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img = render(item)
    img_path = os.path.join(OUTPUT_DIR, f"frase_{date_str}.png")
    img.save(img_path)

    meta = {
        "id": item["id"],
        "tema": item.get("tema"),
        "caption": build_caption(item),
        "comment": None,
        "image_filename": os.path.basename(img_path),
    }
    meta_path = os.path.join(OUTPUT_DIR, f"frase_{date_str}.meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"OK: {img_path}")
    print(f"OK: {meta_path}")


if __name__ == "__main__":
    main()
