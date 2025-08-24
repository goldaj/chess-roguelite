
import os, json
SAVE_PATH = os.path.join(os.path.dirname(__file__),'save.json')
def load_meta():
    if not os.path.exists(SAVE_PATH):
        return {
            "amazon_unlocked": False,
            "starting_deck": {"K":1,"R":1,"N":1,"P":3},
            "permanent": {"bias_white":0.0,"bias_black":0.0,"start_ticks_bonus":0,"zero_cost_probs":{"P":0.0,"N":0.0,"B":0.0,"R":0.0,"Q":0.0,"A":0.0}},
            "stats":{"runs":0,"wins":0}
        }
    return json.load(open(SAVE_PATH,'r',encoding='utf-8'))
def save_meta(data):
    json.dump(data, open(SAVE_PATH,'w',encoding='utf-8'), indent=2)
