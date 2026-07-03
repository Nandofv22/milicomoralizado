import argparse
import datetime
import json
import os

from PIL import Image, ImageDraw

import state
from text_utils import draw_centered_multiline, fit_text, load_font

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
DATA_PATH = os.path.join(ROOT, "data", "questoes.json")
TEMPLATE_PATH = os.path.join(ROOT, "assets", "template_questao.png")
OUTPUT_DIR = os.path.join(ROOT, "output")

WHITE = (245, 245, 245)
DIM = (185, 185, 190)

W, H = 1080, 1350

HASHTAGS_BASE = "#concurseiro #concursopolicial #pmba #policiamilitar #vempraPM #foco #estudos"
HASHTAGS_BY_MATERIA = {
    "Direito Penal": "#direitopenal",
    "Direito Constitucional": "#direitoconstitucional",
    "Processo Penal": "#processopenal",
    "Legislacao PMBA": "#legislacaopmba",
}


def load_bank():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)["questoes"]


def render(item):
    img = Image.open(TEMPLATE_PATH).convert("RGB")
    draw = ImageDraw.Draw(img)

    handle_font = load_font("semibold", 34)
    draw_centered_multiline(draw, ["@milicomoralizado"], handle_font, W / 2, 55, 0, WHITE)

    kicker_font = load_font("title", 42)
    draw_centered_multiline(draw, ["QUESTAO DO DIA"], kicker_font, W / 2, 290, 0, WHITE)

    tag_font = load_font("semibold", 26)
    draw_centered_multiline(draw, [item["materia"].upper()], tag_font, W / 2, 340, 0, DIM)

    zone_top, zone_bottom = 410, 790
    font, lines, line_h = fit_text(
        draw, item["afirmacao"], "bold", W - 200, zone_bottom - zone_top, 52, 30
    )
    block_h = line_h * len(lines)
    start_y = zone_top + (zone_bottom - zone_top - block_h) / 2
    draw_centered_multiline(draw, lines, font, W / 2, start_y, line_h, WHITE)

    vf_font = load_font("title", 40)
    draw_centered_multiline(draw, ["VERDADEIRO OU FALSO?"], vf_font, W / 2, 878, 0, WHITE)

    cta_font = load_font("bold", 30)
    draw_centered_multiline(draw, ["COMENTA AQUI: V OU F"], cta_font, W / 2, H - 110, 0, WHITE)

    return img


def build_caption(item):
    tag = HASHTAGS_BY_MATERIA.get(item["materia"], "")
    return (
        f"\U0001F480 QUESTAO DO DIA — {item['materia']}\n\n"
        "Comenta aqui embaixo: VERDADEIRO ou FALSO?\n"
        "O gabarito comentado sai logo nos comentarios!\n\n"
        f"{HASHTAGS_BASE} {tag}"
    )


def build_comment(item):
    veredito = "VERDADEIRO" if item["correta"] else "FALSO"
    return (
        f"✅ Gabarito: {veredito}\n"
        f"\U0001F4D6 Base legal: {item['base_legal']}\n"
        f"{item['explicacao']}"
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None, help="YYYY-MM-DD, default today")
    parser.add_argument("--index", type=int, default=None, help="override bank index")
    args = parser.parse_args()

    date_str = args.date or datetime.date.today().isoformat()
    bank = load_bank()
    idx = args.index if args.index is not None else state.current_index("questao_index", len(bank))
    item = bank[idx]

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    img = render(item)
    img_path = os.path.join(OUTPUT_DIR, f"questao_{date_str}.png")
    img.save(img_path)

    meta = {
        "id": item["id"],
        "materia": item["materia"],
        "caption": build_caption(item),
        "comment": build_comment(item),
        "image_filename": os.path.basename(img_path),
    }
    meta_path = os.path.join(OUTPUT_DIR, f"questao_{date_str}.meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    print(f"OK: {img_path}")
    print(f"OK: {meta_path}")


if __name__ == "__main__":
    main()
