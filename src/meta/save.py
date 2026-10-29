
import os, json, tempfile
SAVE_PATH = os.path.join(os.path.dirname(__file__),'save.json')
def load_meta():
    if not os.path.exists(SAVE_PATH):
        return {
            "amazon_unlocked": False,
            "starting_deck": {"K":1,"R":1,"B":1,"P":3},
            "permanent": {"bias_white":0.0,"bias_black":0.0,"start_ticks_bonus":0,"zero_cost_probs":{"P":0.0,"N":0.0,"B":0.0,"R":0.0,"Q":0.0,"A":0.0}},
            "stats":{"runs":0,"wins":0}
        }
    with open(SAVE_PATH, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def save_meta(data):
    """Replace the save atomically to preserve the previous version on failure."""
    directory = os.path.dirname(SAVE_PATH)
    os.makedirs(directory, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.meta_', suffix='.tmp', dir=directory)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, indent=2)
            handle.write('\n')
        os.replace(temporary, SAVE_PATH)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
