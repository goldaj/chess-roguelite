
import os, sys, json, random, math, time
import pygame
from pygame.locals import *
try:
    from .core.board import Board, Piece
    from .core.ai import choose_move
    from .ui.assets_loader import Assets
    from .ui.buttons import Button
    from .meta.save import load_meta, save_meta
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    from core.board import Board, Piece
    from core.ai import choose_move
    from ui.assets_loader import Assets
    from ui.buttons import Button
    from meta.save import load_meta, save_meta

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Load content robustly
CONTENT_PATHS = [
    os.path.join(BASE_DIR, "content", "shop_items.json"),
    os.path.join(os.path.dirname(__file__), "content", "shop_items.json"),
]
CONTENT = None
for _p in CONTENT_PATHS:
    if os.path.exists(_p):
        with open(_p, "r", encoding="utf-8") as f:
            CONTENT = json.load(f)
        break
if CONTENT is None:
    raise FileNotFoundError(f"shop_items.json introuvable aux chemins: {CONTENT_PATHS}")

PIECE_VALUES = CONTENT["piece_values"]
TICK_COSTS = CONTENT["tick_costs"]
FILES = "abcdefgh"

def draw_text(surface, text, pos, size=22, color=(230,234,240), center=False):
    font = pygame.font.SysFont("arial", size, bold=True)
    s = font.render(text, True, color)
    r = s.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    surface.blit(s, r)

def rounded_rect(surface, rect, color, radius=12):
    pygame.draw.rect(surface, color, rect, border_radius=radius)

class App:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.fullscreen=False
        w,h = int(info.current_w*0.9), int(info.current_h*0.9)
        self.screen = pygame.display.set_mode((w,h), pygame.RESIZABLE)
        pygame.display.set_caption("ChessRoguelite")
        self.clock = pygame.time.Clock()
        self.assets = Assets(BASE_DIR)
        self.tile=96
        self.assets.load(self.tile)
        self.meta = load_meta()
        self.buttons=[]
        self.state="menu"
        self.phase="menu"
        self.message=""
        self.stage_index=0
        self.animations=[]
        self.hover_tooltip=None
        self.reset_run()
        self.build_menu_buttons()
    
    def recompute_tile(self):
        # Ensure board fits screen; keep pieces crisp
        W, H = self.screen.get_size()
        side_panel = max(360, W//4)
        max_tile_w = max(40, int((W - side_panel - 40) / max(1, self.board_w)))
        max_tile_h = max(40, int((H - 60) / max(1, self.board_h)))
        new_tile = max(56, min(128, min(max_tile_w, max_tile_h)))
        if new_tile != self.tile:
            self.tile = new_tile
            self.assets.load(self.tile)

    def reset_run(self):
        self.phase = "manche"
        self.btns_play = []
        self.stage_index=0
        self.manches_won = 0
        self.gold=0
        self.double_start=False
        self.double_start_always=False
        self.freeze_random_next=False
        self.freeze_target_stock=0
        self.bias_white=self.meta["permanent"]["bias_white"]
        self.bias_black=self.meta["permanent"]["bias_black"]
        self.zero_cost_probs=dict(self.meta["permanent"]["zero_cost_probs"])
        self.enemy_tick_factor=1.0
        self.player_color = 'w' if random.random() < (0.5 + self.bias_white - self.bias_black) else 'b'
        self.enemy_color = 'b' if self.player_color=='w' else 'w'
        sd = CONTENT["stages"][0]
        self.board_w,self.board_h = sd["board"]
        self.player_ticks = 100 + self.meta["permanent"]["start_ticks_bonus"]
        self.enemy_ticks = 100
        self.player_army = dict(self.meta["starting_deck"])
        self.enemy_army = dict(sd["enemy_start"])
        self.selection=None; self.legal_moves=[]
        self.place_armies_initial_layout()
        self.frozen_coords=set()
        self.pre_moves_left=0
        self.turn='w'  # white moves first rules; start powers may give 2 moves
        self.build_ingame_buttons()
    
    
    
    def place_armies_initial_layout(self):
        # Player pieces always at bottom; enemy at top. Colors preserved.
        self.board = Board(self.board_w, self.board_h)

        def center_cols(count, width):
            if count >= width: return list(range(width))
            mid = width // 2
            cols=[mid]; L=mid-1; R=mid+1
            while len(cols)<count and (L>=0 or R<width):
                if L>=0: cols.append(L); L-=1
                if len(cols)>=count: break
                if R<width: cols.append(R); R+=1
            cols.sort(); return cols[:count]

        def place_bottom(army, color):
            pawn_row = self.board_h - 2
            back_row = self.board_h - 1
            cols3 = center_cols(3, self.board_w)
            p_count = min(army.get('P',0), len(cols3))
            for i in range(p_count):
                self.board.set(cols3[i], pawn_row, Piece('P', color))
            back_kinds = ['R','K','N'][:len(cols3)]
            for kind, fx in zip(back_kinds, cols3):
                if army.get(kind,0)>0:
                    self.board.set(fx, back_row, Piece(kind, color))
            for kind in ('B','Q','A','R','N','P'):
                base_count = 1 if kind in ('R','K','N') else 0
                base_p = 1 if (kind=='P' and p_count>0) else 0
                extra = max(0, army.get(kind,0) - base_count - base_p)
                for _ in range(extra):
                    placed=False
                    for y in [back_row, pawn_row]:
                        for x in range(self.board_w):
                            if self.board.get(x,y) is None:
                                self.board.set(x,y, Piece(kind, color)); placed=True; break
                        if placed: break

        def place_top(army, color):
            pawn_row = 1
            back_row = 0
            cols3 = center_cols(3, self.board_w)
            p_count = min(army.get('P',0), len(cols3))
            for i in range(p_count):
                self.board.set(cols3[i], pawn_row, Piece('P', color))
            back_kinds = ['R','K','N'][:len(cols3)]
            for kind, fx in zip(back_kinds, cols3):
                if army.get(kind,0)>0:
                    self.board.set(fx, back_row, Piece(kind, color))
            for kind in ('B','Q','A','R','N','P'):
                base_count = 1 if kind in ('R','K','N') else 0
                base_p = 1 if (kind=='P' and p_count>0) else 0
                extra = max(0, army.get(kind,0) - base_count - base_p)
                for _ in range(extra):
                    placed=False
                    for y in [back_row, pawn_row]:
                        for x in range(self.board_w):
                            if self.board.get(x,y) is None:
                                self.board.set(x,y, Piece(kind, color)); placed=True; break
                        if placed: break

        if self.player_color == 'w':
            place_bottom(self.player_army, 'w')
            place_top(self.enemy_army, 'b')
        else:
            place_bottom(self.player_army, 'b')
            place_top(self.enemy_army, 'w')

    def build_menu_buttons(self):
        self.buttons = []
        sw, sh = self.screen.get_size()
        def add(y, text, cb):
            rect = pygame.Rect(sw//2 - 180, y, 360, 52)
            self.buttons.append(Button(rect, text, cb))
        add(int(sh*0.55), "JOUER", self.start_game)
        add(int(sh*0.55)+70, "OPTIONS", self.open_options)
        add(int(sh*0.55)+140, "QUITTER", self.quit_game)

        sw,sh=self.screen.get_size()
        side_panel = max(360, sw//4)
        x = sw - side_panel + 20
        # place buttons below info area to avoid overlap
        y = 200
        self.btns_play.append(Button(pygame.Rect(x,y, side_panel-40, 44), "Options", self.open_options)); y+=58
        self.btns_play.append(Button(pygame.Rect(x,y, side_panel-40, 44), "Aller au menu (sauver le deck)", self.back_to_menu)); y+=58
        if self.freeze_target_stock>0:
            self.btns_play.append(Button(pygame.Rect(x,y, side_panel-40, 44), "Utiliser Freeze ciblé", self.enter_freeze_mode)); y+=58
    
    def quit_game(self):
        # Sauvegarde et fermeture propre
        try:
            self.meta["starting_deck"] = getattr(self, "player_army", self.meta.get("starting_deck", {}))
            save_meta(self.meta)
        except Exception:
            pass
        pygame.quit()
        sys.exit(0)


    def build_ingame_buttons(self):
        # Buttons placed below the info block in right panel
        self.btns_play = []
        sw, sh = self.screen.get_size()
        side_panel = max(360, sw // 4)
        x = sw - side_panel + 20
        y = 200  # below gold/ticks/manche info
        self.btns_play.append(Button(pygame.Rect(x, y, side_panel - 40, 44), "Options", self.open_options)); y += 58
        self.btns_play.append(Button(pygame.Rect(x, y, side_panel - 40, 44), "Aller au menu (sauver le deck)", self.back_to_menu)); y += 58
        if self.freeze_target_stock > 0:
            self.btns_play.append(Button(pygame.Rect(x, y, side_panel - 40, 44), "Utiliser Freeze ciblé", self.enter_freeze_mode)); y += 58


    def build_shop_buttons(self):
        if self.phase != "inter":
            return  # guard: only between manches
        # build 3 random offers + 'Continuer' button
        self.shop_offers = random.sample(CONTENT["shop_pool"], 3)
        self.shop_btns=[]
        sw,sh=self.screen.get_size()
        y=140
        for it in self.shop_offers:
            def make_cb(item=it):
                def cb():
                    self.purchase(item)
                return cb
            btn=Button(pygame.Rect(60,y, 760, 48), f"{it['name']}  (coût {it.get('cost',0)})", make_cb())
            self.shop_btns.append(btn)
            y+=70
        self.shop_continue=Button(pygame.Rect(60,y+10, 300, 48), "Continuer", self.shop_continue_next)
    
    def start_game(self):
        self.reset_run()
        self.state="play"
        # apply start powers per stage
        self.start_stage()
    
    def open_options(self):
        self._state_before_options = self.state
        self.state="options"
        self.build_options_buttons()
    
    def build_options_buttons(self):
        self.opt_btns=[]
        sw,sh=self.screen.get_size()
        def add(y,text,cb):
            self.opt_btns.append(Button(pygame.Rect(sw//2-220, y, 440, 52), text, cb))
        add(int(sh*0.45), "Basculer plein écran / fenêtré", self.toggle_fullscreen)
        add(int(sh*0.45)+70, "Retour", self.back_to_prev_from_options)
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        else:
            info = pygame.display.Info()
            w,h = int(info.current_w*0.9), int(info.current_h*0.9)
            self.screen = pygame.display.set_mode((w,h), pygame.RESIZABLE)
        self.assets.load(self.tile)
        if self.state=="play":
            self.build_ingame_buttons()
        elif self.state=="menu":
            self.build_menu_buttons()
        elif self.state=="options":
            self.build_options_buttons()
        elif self.state=="shop":
            self.build_shop_buttons()
    
    def back_to_prev_from_options(self):
        self.state = getattr(self, "_state_before_options", "menu")
    
    def back_to_menu(self):
        self.meta["starting_deck"]=self.player_army
        save_meta(self.meta)
        self.state="menu"
        self.build_menu_buttons()
    
    def enter_freeze_mode(self):
        self.state="freeze_target"
        self.message="Cliquez une pièce ennemie à geler (1 tour)."
    
    def start_stage(self):
        self.recompute_tile()
        if self.double_start or self.double_start_always:
            self.pre_moves_left=2
        else:
            self.pre_moves_left=0
        if self.freeze_random_next:
            self.apply_freeze_random_enemy(); self.freeze_random_next=False
        self.build_ingame_buttons()
    
    def end_stage(self, win:bool):
        bonus = int(self.player_ticks * CONTENT["tick_reward_factor"])
        if win:
            self.gold += bonus + 5
        if win:
            self.manches_won += 1
            self.stage_index += 1
            if self.stage_index >= len(CONTENT["stages"]):
                # unlock amazon
                if not self.meta["amazon_unlocked"]:
                    self.meta["amazon_unlocked"]=True
                self.meta["stats"]["runs"]+=1
                self.meta["stats"]["wins"]+=1
                save_meta(self.meta)
                self.state="meta"
            else:
                sd = CONTENT["stages"][self.stage_index]
                self.board_w, self.board_h = sd["board"]
                boost=sd.get("enemy_boost",0)
                for _ in range(boost):
                    kind = random.choice(['P','N','B','R'])
                    self.enemy_army[kind]=self.enemy_army.get(kind,0)+1
                # ticks fixed by stage
                self.player_ticks = sd.get("player_ticks", self.player_ticks)
                self.enemy_ticks = sd.get("enemy_ticks", self.enemy_ticks)
                # carry surviving pieces to next manche
                self.player_army = self.count_army(self.player_color)
                self.enemy_army = self.count_army(self.enemy_color)
                self.place_armies_initial_layout()
                self.selection=None; self.legal_moves=[]
                self.phase = "inter"; self.state="shop"
                self.build_shop_buttons()
        else:
            self.meta["stats"]["runs"]+=1
            save_meta(self.meta)
            self.state="meta"
    
    def apply_freeze_random_enemy(self):
        coords=[]
        for x in range(self.board_w):
            for y in range(self.board_h):
                p=self.board.get(x,y)
                if p and p.color==self.enemy_color and p.kind!='K':
                    coords.append((x,y))
        if coords:
            self.frozen_coords.add(random.choice(coords))
    
    # Helpers
    def cost_for_piece(self, kind):
        prob = self.zero_cost_probs.get(kind, 0.0)
        return 0 if random.random() < prob else 1
    def piece_value(self, kind):
        return PIECE_VALUES.get(kind,0)
    
    def count_army(self, color):
        counts = {}
        for x in range(self.board_w):
            for y in range(self.board_h):
                p = self.board.get(x,y)
                if p and p.color==color:
                    counts[p.kind] = counts.get(p.kind,0)+1
        return counts


    def world_layout(self):
        W,H=self.screen.get_size()
        side_panel=max(360, W//4)
        ox = (W-side_panel - self.tile*self.board_w)//2
        oy = (H - self.tile*self.board_h)//2
        return ox,oy,side_panel
    
    def to_cell(self, mx,my, ox,oy):
        x=(mx-ox)//self.tile; y=(my-oy)//self.tile
        if 0<=x<self.board_w and 0<=y<self.board_h: return int(x),int(y)
        return None
    
    def animate_move(self, x1,y1,x2,y2):
        # simple 0.18s tween
        duration=180
        start=pygame.time.get_ticks()
        W,H=self.screen.get_size()
        ox,oy,sp = self.world_layout()
        start_px=(ox+x1*self.tile+self.tile//2, oy+y1*self.tile+self.tile//2)
        end_px=(ox+x2*self.tile+self.tile//2, oy+y2*self.tile+self.tile//2)
        p=self.board.get(x1,y1)
        key=f"{p.color}_{'pawn' if p.kind=='P' else 'knight' if p.kind=='N' else 'bishop' if p.kind=='B' else 'rook' if p.kind=='R' else 'queen' if p.kind=='Q' else 'king' if p.kind=='K' else 'amazon'}"
        sprite=self.assets.pieces[key]
        while pygame.time.get_ticks()-start < duration:
            t=(pygame.time.get_ticks()-start)/duration
            cx=int(start_px[0]*(1-t)+end_px[0]*t)
            cy=int(start_px[1]*(1-t)+end_px[1]*t)
            self.draw_play()
            sr=sprite.get_rect(center=(cx,cy))
            self.screen.blit(sprite, sr)
            pygame.display.flip()
            self.clock.tick(60)
    
    def do_player_move(self, x1,y1,x2,y2):
        p=self.board.get(x1,y1); t=self.board.get(x2,y2)
        self.animate_move(x1,y1,x2,y2)
        self.board.move_and_promote(x1,y1,x2,y2)
        if t:
            self.gold += self.piece_value(t.kind)
        cost=self.cost_for_piece(p.kind)
        self.player_ticks -= cost
        if self.player_ticks <= 0:
            self.message="Vous manquez de temps !"; self.end_stage(False); return
        ek=self.board.locate_king(self.enemy_color)
        no_enemy = all((self.board.get(x,y) is None or self.board.get(x,y).color!=self.enemy_color) for x in range(self.board_w) for y in range(self.board_h))
        if ek is None or no_enemy:
            self.message="Roi ennemi capturé !"; self.end_stage(True); return
        if self.pre_moves_left>0:
            self.pre_moves_left-=1
            if self.pre_moves_left==0: self.turn=self.enemy_color
        else:
            self.turn=self.enemy_color
    
    def do_enemy_turn(self):
        move=choose_move(self.board, self.enemy_color)
        if move is None:
            # No legal move (pat) -> skip enemy turn (no end-of-manche)
            self.turn=self.player_color; return
        (x1,y1),(x2,y2)=move
        if (x1,y1) in self.frozen_coords:
            self.frozen_coords.discard((x1,y1))
            self.turn=self.player_color; return
        p=self.board.get(x1,y1); t=self.board.get(x2,y2)
        # animate enemy
        self.animate_move(x1,y1,x2,y2)
        self.board.move_and_promote(x1,y1,x2,y2)
        cost=1 * self.enemy_tick_factor
        self.enemy_ticks -= cost
        if self.enemy_ticks <= 0:
            self.message="L'ennemi manque de temps !"; self.end_stage(True); return
        pk=self.board.locate_king(self.player_color)
        no_player = all((self.board.get(x,y) is None or self.board.get(x,y).color!=self.player_color) for x in range(self.board_w) for y in range(self.board_h))
        if pk is None or no_player:
            self.message="Votre roi est capturé..."; self.end_stage(False); return
        self.turn=self.player_color
    
    # SHOP
    def purchase(self, item):
        cost=item.get('cost',0)
        if self.gold < cost:
            self.message="Pas assez d'or."; return
        t=item['type']
        if t=='tick':
            self.player_ticks += item['amount']
        elif t=='tick_enemy':
            self.enemy_tick_factor = max(0.5, 1.0 + item['amount'])
        elif t=='economy' and item.get('effect')=='double':
            self.gold *= 2
        elif t=='consumable':
            if item['effect']=='freeze_random':
                self.freeze_random_next=True
            elif item['effect']=='freeze_target':
                self.freeze_target_stock += 1
        elif t=='start_power':
            if item['effect']=='double_once': self.double_start=True
            else: self.double_start_always=True
        elif t=='bias':
            if item['side']=='white': self.bias_white += item['amount']
            else: self.bias_black += item['amount']
        elif t=='zero_cost':
            k=item['piece']; self.zero_cost_probs[k]=min(0.95, self.zero_cost_probs.get(k,0)+item['chance'])
        elif t=='convert':
            self.convert_piece_dialog()
        elif t=='buy':
            self.buy_piece_dialog()
        self.gold -= cost
        self.message=f"Achat : {item['name']}"
    
    def shop_continue_next(self):
        # proceed to next manche
        self.phase = "manche"
        self.start_stage()
        self.state="play"
    
    def convert_piece_dialog(self):
        options=[]
        for k,v in CONTENT["convert_costs"].items():
            src,dst=k.split("->")
            if self.player_army.get(src,0)>0:
                options.append((src,dst,v))
        if not options:
            self.message="Aucune conversion possible."; return
        options.sort(key=lambda x:x[2])
        src,dst,cost=options[0]
        if self.gold < cost:
            self.message=f"Conversion {src}->{dst} coûte {cost} or."; return
        self.player_army[src]-=1
        self.player_army[dst]=self.player_army.get(dst,0)+1
        self.gold -= cost
        self.message=f"Converti {src} en {dst}."
    
    def buy_piece_dialog(self):
        pool=['P','N','B','R','Q']
        if self.meta["amazon_unlocked"]: pool.append('A')
        kind=random.choice(pool); cost=CONTENT["buy_costs"][kind]
        if self.gold < cost:
            self.message=f"Acheter {kind} coûte {cost} or."; return
        self.player_army[kind]=self.player_army.get(kind,0)+1
        self.gold -= cost
        self.message=f"Acheté {kind}."
    
    # Drawing
    
    def open_meta(self):
        self.state = "meta_menu"
        self.build_meta_buttons()

    def build_meta_buttons(self):
        self.meta_menu_btns = []
        sw, sh = self.screen.get_size()
        self.meta_menu_btns.append(Button(pygame.Rect(sw//2-180, int(sh*0.80), 360, 52), "Retour", self.back_to_menu))

    def draw_meta_menu(self):
        self.screen.fill((20,22,28))
        draw_text(self.screen, "Méta — Déblocages & deck de départ", (self.screen.get_width()//2, 70), 28, center=True)
        y = 120
        draw_text(self.screen, f"Amazon débloquée : {'Oui' if self.meta.get('amazon_unlocked') else 'Non'}", (60, y), 22); y += 30
        # permanent bonuses
        perm = self.meta.get('permanent', {})
        draw_text(self.screen, f"Biais Blanc: {int(perm.get('bias_white',0)*100)}%  |  Biais Noir: {int(perm.get('bias_black',0)*100)}%", (60, y), 20); y += 26
        zcp = perm.get('zero_cost_probs', {})
        draw_text(self.screen, f"Chances de coup gratuit (par pièce): {zcp}", (60, y), 18); y += 26
        # starting deck
        sd = self.meta.get('starting_deck', {})
        deck_str = ", ".join([f"{k}x{sd[k]}" for k in sorted(sd.keys())]) if sd else "(défaut)"
        draw_text(self.screen, f"Deck de départ: {deck_str}", (60, y), 22); y += 30
        for b in self.meta_menu_btns: b.draw(self.screen)

    def draw_menu(self):
        self.screen.fill((24,26,32))
        if self.assets.logo:
            lr=self.assets.logo.get_rect()
            sr=self.screen.get_rect()
            s=0.6
            logo=pygame.transform.smoothscale(self.assets.logo,(int(lr.w*s),int(lr.h*s)))
            self.screen.blit(logo, logo.get_rect(center=(sr.w//2, sr.h//3)))
        for b in self.buttons: b.draw(self.screen)
    
    def draw_options(self):
        self.screen.fill((22,24,30))
        draw_text(self.screen, "OPTIONS", (self.screen.get_width()//2, 80), 32, center=True)
        for b in self.opt_btns: b.draw(self.screen)
    
    def draw_coords(self, ox, oy):
        # files a..h at bottom/top; ranks 1..H on left/right from white perspective
        # bottom = white side (y = h-1)
        for x in range(self.board_w):
            letter=FILES[x]
            draw_text(self.screen, letter, (ox + x*self.tile + self.tile//2, oy + self.board_h*self.tile + 6), size=18, color=(210,215,225), center=True)
            draw_text(self.screen, letter, (ox + x*self.tile + self.tile//2, oy - 24), size=18, color=(210,215,225), center=True)
        for y in range(self.board_h):
            rank=str(self.board_h - y)
            draw_text(self.screen, rank, (ox - 20, oy + y*self.tile + self.tile//2), size=18, color=(210,215,225), center=True)
            draw_text(self.screen, rank, (ox + self.board_w*self.tile + 20, oy + y*self.tile + self.tile//2), size=18, color=(210,215,225), center=True)
    
    def piece_name_fr(self, kind):
        return {'K':'Roi','Q':'Dame','R':'Tour','B':'Fou','N':'Cavalier','P':'Pion','A':'Amazone'}.get(kind,kind)
    
    def draw_tooltip(self, text, mx,my):
        font=pygame.font.SysFont("arial", 18, bold=True)
        s=font.render(text, True, (20,22,28))
        pad=8
        r=pygame.Rect(mx+16, my+16, s.get_width()+pad*2, s.get_height()+pad*2)
        rounded_rect(self.screen, r, (235,238,245), radius=8)
        self.screen.blit(s, (r.x+pad, r.y+pad))
    
    def draw_play(self):
        self.screen.fill((16,18,24))
        W,H=self.screen.get_size()
        ox,oy,side_panel = self.world_layout()
        # board
        col_a=(210,215,222); col_b=(110,120,135)
        for x in range(self.board_w):
            for y in range(self.board_h):
                r=pygame.Rect(ox+x*self.tile, oy+y*self.tile, self.tile, self.tile)
                c=col_a if (x+y)%2==0 else col_b
                pygame.draw.rect(self.screen, c, r)
        # pieces
        self.hover_tooltip=None
        mx,my=pygame.mouse.get_pos()
        for x in range(self.board_w):
            for y in range(self.board_h):
                r=pygame.Rect(ox+x*self.tile, oy+y*self.tile, self.tile, self.tile)
                p=self.board.get(x,y)
                if p:
                    key=f"{p.color}_{'pawn' if p.kind=='P' else 'knight' if p.kind=='N' else 'bishop' if p.kind=='B' else 'rook' if p.kind=='R' else 'queen' if p.kind=='Q' else 'king' if p.kind=='K' else 'amazon'}"
                    img=self.assets.pieces[key]
                    ir=img.get_rect(center=r.center)
                    self.screen.blit(img, ir)
                    if r.collidepoint((mx,my)):
                        self.hover_tooltip=self.piece_name_fr(p.kind)
                if self.selection and (x,y) in self.legal_moves:
                    pygame.draw.rect(self.screen, (255,210,70), r, 4)
                if (x,y) in self.frozen_coords:
                    fr=pygame.Rect(r.x+6, r.y+6, self.tile-12, self.tile-12)
                    s=pygame.Surface((fr.w, fr.h), pygame.SRCALPHA)
                    s.fill((120,180,255,90))
                    self.screen.blit(s, fr)
        # coords
        self.draw_coords(ox,oy)
        # side panel
        panel=pygame.Rect(W-side_panel,0,side_panel,H)
        pygame.draw.rect(self.screen, (28,30,38), panel)
        # info
        self.screen.blit(self.assets.icons["coin"], (panel.x+16, 20))
        draw_text(self.screen, f"Or : {self.gold}", (panel.x+54, 22), 24)
        self.screen.blit(self.assets.icons["tick"], (panel.x+16, 60))
        draw_text(self.screen, f"Vos ticks : {int(self.player_ticks)}", (panel.x+54, 62), 22)
        draw_text(self.screen, f"Ticks ennemi : {int(self.enemy_ticks)}", (panel.x+54, 90), 22, (180,200,220))
        draw_text(self.screen, f"Manche : {self.stage_index+1}", (panel.x+16, 126), 24)
        if self.double_start or self.double_start_always:
            draw_text(self.screen, f"Double coup initial", (panel.x+16, 158), 20, (255,230,130))
        if self.message:
            draw_text(self.screen, self.message, (panel.x+16, H-48), 20, (220,220,255))
        # buttons
        for b in self.btns_play: b.draw(self.screen)
        # tooltip
        if self.hover_tooltip:
            self.draw_tooltip(self.hover_tooltip, mx,my)
    
    def draw_shop(self):
        self.screen.fill((22,24,30))
        draw_text(self.screen, "Boutique — 3 améliorations au choix", (60,60), 28)
        draw_text(self.screen, f"Or : {self.gold}", (60, 96), 24)
        for b in self.shop_btns: b.draw(self.screen)
        self.shop_continue.draw(self.screen)
    
    def draw_meta(self):
        self.screen.fill((20,22,28))
        draw_text(self.screen, "Fin de run — Progression méta", (60,60), 28)
        draw_text(self.screen, f"Amazon débloquée : {'Oui' if self.meta['amazon_unlocked'] else 'Non'}", (60, 100), 22)
        # back to menu button
        self.meta_btn = Button(pygame.Rect(60, 150, 300, 48), "Retour menu", self.back_to_menu)
        self.meta_btn.draw(self.screen)
    
    def handle_play_click(self, pos):
        mx,my=pos
        ox,oy,sp = self.world_layout()
        cell=self.to_cell(mx,my,ox,oy)
        if cell:
            x,y=cell
            if self.selection is None:
                p=self.board.get(x,y)
                if p and p.color==self.player_color and self.turn==self.player_color:
                    self.selection=(x,y)
                    self.legal_moves=self.board.legal_moves_for(x,y)
                else:
                    self.message="Sélectionnez une de vos pièces."
            else:
                if (x,y) in self.legal_moves:
                    x1,y1=self.selection
                    self.do_player_move(x1,y1,x,y)
                    self.selection=None; self.legal_moves=[]
                else:
                    self.selection=None; self.legal_moves=[]
        # pass: handled by buttons
    
    def run(self):
        running=True
        while running:
            dt = self.clock.tick(60)
            for ev in pygame.event.get():
                if ev.type==QUIT: running=False
                elif ev.type==VIDEORESIZE:
                    self.recompute_tile()
                    if self.state=="menu": self.build_menu_buttons()
                    if self.state=="play": self.build_ingame_buttons()
                    if self.state=="shop": self.build_shop_buttons()
                    if self.state=="options": self.build_options_buttons()
                elif ev.type in (MOUSEMOTION,MOUSEBUTTONDOWN):
                    if self.state=="menu":
                        for b in self.buttons: b.handle_event(ev)
                    elif self.state=="options":
                        for b in self.opt_btns: b.handle_event(ev)
                    elif self.state=="play":
                        for b in self.btns_play: b.handle_event(ev)
                        if ev.type==MOUSEBUTTONDOWN and ev.button==1:
                            self.handle_play_click(ev.pos)
                    elif self.state=="freeze_target":
                        if ev.type==MOUSEBUTTONDOWN and ev.button==1:
                            ox,oy,sp=self.world_layout()
                            cell=self.to_cell(ev.pos[0], ev.pos[1], ox,oy)
                            if cell:
                                x,y=cell; p=self.board.get(x,y)
                                if p and p.color==self.enemy_color:
                                    self.frozen_coords.add((x,y))
                                    self.freeze_target_stock-=1
                                    self.message="Pièce ennemie gelée (1 tour)."
                                    self.state="play"
                    elif self.state=="shop":
                        for b in self.shop_btns: b.handle_event(ev)
                        self.shop_continue.handle_event(ev)
                    elif self.state=="meta":
                        if hasattr(self, 'meta_btn'):
                            self.meta_btn.handle_event(ev)
                    elif self.state=="meta_menu":
                        for b in getattr(self, 'meta_menu_btns', []): b.handle_event(ev)
                # no keyboard shortcuts; buttons only
            
            # game tick
            if self.state=="play":
                if self.turn==self.enemy_color:
                    self.do_enemy_turn()
            
            # draw
            if self.state=="menu": self.draw_menu()
            elif self.state=="options": self.draw_options()
            elif self.state in ("play","freeze_target"): self.draw_play()
            elif self.state=="shop": self.draw_shop()
            elif self.state=="meta": self.draw_meta()
            elif self.state=="meta_menu": self.draw_meta_menu()
            
            pygame.display.flip()
        # on quit
        self.meta["starting_deck"]=self.player_army
        save_meta(self.meta)
        pygame.quit()

def main():
    App().run()

if __name__ == "__main__":
    main()