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

GOLD = (232, 184, 75)
NAVY_TEXT = (10, 17, 40)
LIGHT = (235, 235, 235)
DIM = (190, 190, 190)

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

    title_font = load_font("title", 50)
    draw_centered_multiline(draw, ["QUESTAO DO DIA"], title_font, W / 2, 145, 0, GOLD)

    tag_font = load_font("semibold", 26)
    materia_upper = item["materia"].upper()
    draw_centered_multiline(draw, [materia_upper], tag_font, W / 2, 205, 0, DIM)

    panel_left, panel_top, panel_right, panel_bottom = 120, 415, W - 120, 725
    font, lines, line_h = fit_text(
        draw,
        item["enunciado"],
        "semibold",
        panel_right - panel_left,
        panel_bottom - panel_top,
        44,
        24,
    )
    block_h = line_h * len(lines)
    start_y = panel_top + (panel_bottom - panel_top - block_h) / 2
    draw_centered_multiline(draw, lines, font, W / 2, start_y, line_h, LIGHT)

    slot_h, gap, top = 96, 22, 820
    letters = ["A", "B", "C", "D"]
    for i, letter in enumerate(letters):
        y0 = top + i * (slot_h + gap)
        cy = y0 + slot_h / 2
        bcx, br = 145, 27
        draw.ellipse([bcx - br, cy - br, bcx + br, cy + br], fill=GOLD)
        letter_font = load_font("title", 32)
        bbox = draw.textbbox((0, 0), letter, font=letter_font)
        lw, lh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text((bcx - lw / 2 - bbox[0], cy - lh / 2 - bbox[1]), letter, font=letter_font, fill=NAVY_TEXT)

        alt_text = item["alternativas"][letter]
        afont, alines, aline_h = fit_text(
            draw, alt_text, "semibold", W - 120 - 195, slot_h - 16, 30, 18, step=1
        )
        ablock_h = aline_h * len(alines)
        ay = cy - ablock_h / 2
        draw_centered_multiline(
            draw, alines, afont, 0, ay, aline_h, LIGHT, align="left", box_left=195
        )

    handle_font = load_font("semibold", 24)
    draw_centered_multiline(draw, ["@milicomoralizado"], handle_font, W / 2, H - 78, 0, GOLD)

    return img


def build_caption(item):
    tag = HASHTAGS_BY_MATERIA.get(item["materia"], "")
    return (
        f"\U0001F4DA QUESTAO DO DIA — {item['materia']}\n\n"
        "Responda nos comentarios com a letra da alternativa correta (A, B, C ou D).\n"
        "O gabarito comentado sai logo ali embaixo, nos comentarios!\n\n"
        f"{HASHTAGS_BASE} {tag}"
    )


def build_comment(item):
    return (
        f"✅ Gabarito: {item['gabarito']}) {item['alternativas'][item['gabarito']]}\n"
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
