import argparse
import datetime
import json
import os
import sys

import instagram_api
import state

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUTPUT_DIR = os.path.join(ROOT, "output")
DATA_PATHS = {
    "questao": os.path.join(ROOT, "data", "questoes.json"),
    "frase": os.path.join(ROOT, "data", "frases.json"),
}
BANK_KEYS = {"questao": "questoes", "frase": "frases"}
STATE_KEYS = {"questao": "questao_index", "frase": "frase_index"}


def bank_len(post_type):
    with open(DATA_PATHS[post_type], encoding="utf-8") as f:
        data = json.load(f)
    return len(data[BANK_KEYS[post_type]])


def build_raw_url(image_filename):
    repo = os.environ.get("GITHUB_REPOSITORY")
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    if not repo:
        raise RuntimeError("GITHUB_REPOSITORY env var not set (run this inside the GitHub Actions workflow)")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/output/{image_filename}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True, choices=["questao", "frase"])
    parser.add_argument("--date", default=None)
    args = parser.parse_args()

    date_str = args.date or datetime.date.today().isoformat()
    meta_path = os.path.join(OUTPUT_DIR, f"{args.type}_{date_str}.meta.json")
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    ig_user_id = os.environ["IG_USER_ID"]
    access_token = os.environ["IG_ACCESS_TOKEN"]

    image_url = build_raw_url(meta["image_filename"])
    print(f"Waiting for {image_url} to be publicly reachable...")
    instagram_api.wait_for_public_url(image_url)

    print("Publishing to Instagram...")
    media_id = instagram_api.publish_image(ig_user_id, access_token, image_url, meta["caption"])
    print(f"Published. media_id={media_id}")

    if meta.get("comment"):
        comment_id = instagram_api.comment_on_media(media_id, access_token, meta["comment"])
        print(f"Gabarito commented. comment_id={comment_id}")

    key = STATE_KEYS[args.type]
    new_idx = state.advance_index(key, bank_len(args.type))
    print(f"State advanced: {key} -> {new_idx}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)
