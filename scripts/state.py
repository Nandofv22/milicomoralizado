import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
STATE_PATH = os.path.join(HERE, "..", "data", "state.json")

DEFAULT_STATE = {"questao_index": 0, "frase_index": 0}


def load_state():
    if not os.path.exists(STATE_PATH):
        return dict(DEFAULT_STATE)
    with open(STATE_PATH, encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
        f.write("\n")


def current_index(key, bank_len):
    state = load_state()
    return state.get(key, 0) % bank_len


def advance_index(key, bank_len):
    state = load_state()
    idx = state.get(key, 0) % bank_len
    state[key] = (idx + 1) % bank_len
    save_state(state)
    return state[key]
