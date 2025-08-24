
import os, sys, json, random, math
import pygame
from pygame.locals import *
try:
    from .core.board import Board, Piece
    from .core.ai import choose_move
    from .ui.assets_loader import Assets
    from .meta.save import load_meta, save_meta
except ImportError:
    # Support running as a plain script (e.g., PyCharm 'Run main.py')
    import os, sys
    sys.path.append(os.path.dirname(__file__))  # add 'src' to path
    from core.board import Board, Piece
    from core.ai import choose_move
    from ui.assets_loader import Assets
    from meta.save import load_meta, save_meta


BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Load content
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
# original open removed
    CONTENT = json.load(f)

PIECE_VALUES = CONTENT["piece_values"]
TICK_COSTS = CONTENT["tick_costs"]

def draw_text(surface, text, pos, size=22, color=(230,234,240), center=False):
    font = pygame.font.SysFont("arial", size, bold=True)
    s = font.render(text, True, color)
    r = s.get_rect()
    if center:
        r.center = pos
    else:
        r.topleft = pos
    surface.blit(s, r)

class ChessRogueliteApp:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.fullscreen = False
        w, h = int(info.current_w*0.9), int(info.current_h*0.9)
        self.screen = pygame.display.set_mode((w,h), pygame.RESIZABLE)
        pygame.display.set_caption("ChessRoguelite")
        self.clock = pygame.time.Clock()
        self.assets = Assets(BASE_DIR)
        self.tile = 96
        self.assets.load(self.tile)
        self.meta = load_meta()
        self.state = "menu"
        self.message = ""
        self.stage_index = 0
        self.reset_run()
    
    def reset_run(self):
        self.stage_index = 0
        self.gold = 0
        self.double_start = False
        self.double_start_always = False
        self.freeze_random_next = False
        self.freeze_target_stock = 0
        self.bias_white = self.meta["permanent"]["bias_white"]
        self.bias_black = self.meta["permanent"]["bias_black"]
        self.zero_cost_probs = dict(self.meta["permanent"]["zero_cost_probs"])
        self.board = None
        self.player_color = 'w' if random.random() < (0.5 + self.bias_white - self.bias_black) else 'b'
        self.enemy_color = 'b' if self.player_color=='w' else 'w'
        self.stage_data = CONTENT["stages"][0]
        self.board_w, self.board_h = self.stage_data["board"]
        self.player_ticks = 100 + self.meta["permanent"]["start_ticks_bonus"]
        self.enemy_ticks = 100
        self.player_army = dict(self.meta["starting_deck"])  # e.g., {"K":1,"R":1,"N":1,"P":3}
        self.enemy_army = dict(self.stage_data["enemy_start"])
        self.selection = None
        self.legal_moves = []
        self.turn = 'w'  # chess turn order for moves; ticks are budgets
        self.place_armies()
        self.frozen_coords = set()
        if self.freeze_random_next:
            self.apply_freeze_random_enemy()
    
    def place_armies(self):
        # Initialize board
        self.board = Board(self.board_w, self.board_h)
        # Place player's pieces on bottom 2 ranks, enemy on top 2 ranks
        def place(army, color, rows):
            # simple placement left to right by kind priority
            order = ["K","Q","R","B","N","A","P"]
            x = 0
            for kind in order:
                count = army.get(kind,0)
                for _ in range(count):
                    # find next spot
                    placed = False
                    for ry in rows:
                        for xx in range(self.board_w):
                            if self.board.get(xx,ry) is None:
                                self.board.set(xx,ry,Piece(kind, color))
                                placed = True
                                break
                        if placed: break
            # ensure at least a King
        if self.player_color == 'w':
            place(self.player_army,'w', [self.board_h-1, self.board_h-2, self.board_h-3])
            place(self.enemy_army,'b', [0,1,2])
            self.turn = 'w'
        else:
            place(self.player_army,'b', [0,1,2])
            place(self.enemy_army,'w', [self.board_h-1, self.board_h-2, self.board_h-3])
            self.turn = 'w'  # white still moves first; bias handled by start powers
    
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        else:
            info = pygame.display.Info()
            w,h = int(info.current_w*0.9), int(info.current_h*0.9)
            self.screen = pygame.display.set_mode((w,h), pygame.RESIZABLE)
        self.refresh_layout()
    
    def refresh_layout(self):
        # recompute tile based on window
        W,H = self.screen.get_size()
        side_panel = max(320, W//4)
        self.tile = min((W-side_panel)//self.board_w, H//self.board_h)
        self.assets.load(self.tile)
    
    def draw_board(self):
        W,H = self.screen.get_size()
        side_panel = max(320, W//4)
        ox = (W-side_panel - self.tile*self.board_w)//2
        oy = (H - self.tile*self.board_h)//2
        # board
        col_a = (210,215,222)
        col_b = (110,120,135)
        for x in range(self.board_w):
            for y in range(self.board_h):
                r = pygame.Rect(ox+x*self.tile, oy+y*self.tile, self.tile, self.tile)
                c = col_a if (x+y)%2==0 else col_b
                pygame.draw.rect(self.screen, c, r)
                # highlight legal
                if self.selection and (x,y) in self.legal_moves:
                    pygame.draw.rect(self.screen, (255, 210, 70), r, 4)
                p = self.board.get(x,y)
                if p:
                    key = f"{p.color}_{('pawn' if p.kind=='P' else 'knight' if p.kind=='N' else 'bishop' if p.kind=='B' else 'rook' if p.kind=='R' else 'queen' if p.kind=='Q' else 'king' if p.kind=='K' else 'amazon')}"
                    img = self.assets.pieces.get(key)
                    if img:
                        ir = img.get_rect()
                        ir.center = r.center
                        self.screen.blit(img, ir)
                    if (x,y) in self.frozen_coords:
                        # overlay freeze
                        fr = pygame.Rect(r.x+6,r.y+6, self.tile-12, self.tile-12)
                        s = pygame.Surface((fr.w, fr.h), pygame.SRCALPHA)
                        s.fill((120,180,255,90))
                        self.screen.blit(s, fr)
        # side panel
        panel = pygame.Rect(W - side_panel, 0, side_panel, H)
        pygame.draw.rect(self.screen, (28,30,38), panel)
        # info
        self.screen.blit(self.assets.icons["coin"], (panel.x+16, 20))
        draw_text(self.screen, f"Or : {self.gold}", (panel.x+58, 22), size=26)
        self.screen.blit(self.assets.icons["tick"], (panel.x+16, 64))
        draw_text(self.screen, f"Vos ticks : {int(self.player_ticks)}", (panel.x+58, 66), size=22)
        draw_text(self.screen, f"Ticks ennemi : {int(self.enemy_ticks)}", (panel.x+58, 94), size=22, color=(180,200,220))
        draw_text(self.screen, f"Manche : {self.stage_index+1}", (panel.x+16, 130), size=24)
        if self.freeze_target_stock > 0:
            self.screen.blit(self.assets.icons["freeze"], (panel.x+16, 170))
            draw_text(self.screen, f"Freeze ciblé : {self.freeze_target_stock}", (panel.x+58, 174), size=22)
        if self.double_start or self.double_start_always:
            draw_text(self.screen, f"Double coup initial actif", (panel.x+16, 210), size=20, color=(255,230,130))
        if self.message:
            draw_text(self.screen, self.message, (panel.x+16, H-48), size=20, color=(220,220,255))
        draw_text(self.screen, "O : Options | Échap : Menu", (panel.x+16, H-28), size=18, color=(180,190,200))
        return ox, oy, side_panel
    
    def cost_for_piece(self, kind):
        base = TICK_COSTS.get(kind,100)
        # zero-cost proc?
        if random.random() < self.zero_cost_probs.get(kind,0.0):
            return 0
        return base
    
    def piece_value(self, kind):
        return PIECE_VALUES.get(kind,0)
    
    def to_cell(self, mx,my, ox,oy):
        x = (mx - ox) // self.tile
        y = (my - oy) // self.tile
        if 0 <= x < self.board_w and 0 <= y < self.board_h:
            return int(x), int(y)
        return None
    
    def apply_freeze_random_enemy(self):
        # mark a random enemy piece (not king) as frozen for 1 move
        coords = []
        for x in range(self.board_w):
            for y in range(self.board_h):
                p = self.board.get(x,y)
                if p and p.color == self.enemy_color and p.kind != 'K':
                    coords.append((x,y))
        if coords:
            self.frozen_coords.add(random.choice(coords))
    
    def start_stage(self):
        # apply start powers
        if self.double_start or self.double_start_always:
            # allow two player moves before enemy moves
            self.turn = self.player_color
            self.pre_moves_left = 2
        else:
            self.pre_moves_left = 0
        if self.freeze_random_next:
            self.apply_freeze_random_enemy()
            self.freeze_random_next = False
    
    def end_stage(self, win:bool):
        # reward ticks remaining
        bonus = int(self.player_ticks * CONTENT["tick_reward_factor"])
        if win:
            self.gold += bonus + 5  # small prime for winning
        # progress or finish
        if win:
            self.stage_index += 1
            if self.stage_index >= len(CONTENT["stages"]):
                # unlock amazon meta
                if not self.meta["amazon_unlocked"]:
                    self.meta["amazon_unlocked"] = True
                self.meta["stats"]["runs"] += 1
                self.meta["stats"]["wins"] += 1
                save_meta(self.meta)
                self.state = "meta"  # meta screen
            else:
                # prepare next stage
                sd = CONTENT["stages"][self.stage_index]
                self.board_w, self.board_h = sd["board"]
                # enemy boost: add random piece(s)
                boost = sd.get("enemy_boost",0)
                for _ in range(boost):
                    kind = random.choice(['P','N','B','R'])
                    self.enemy_army[kind] = self.enemy_army.get(kind,0)+1
                self.player_ticks += CONTENT["tick_bonus_per_stage"]
                self.enemy_ticks += CONTENT["tick_bonus_per_stage"]
                # re-place armies with current deck (lost pieces are lost)
                self.place_armies()
                self.selection=None; self.legal_moves=[]
                self.state = "shop"
        else:
            # lose run
            self.meta["stats"]["runs"] += 1
            save_meta(self.meta)
            self.state = "meta"
    
    def do_player_move(self, x1,y1,x2,y2):
        p = self.board.get(x1,y1)
        t = self.board.get(x2,y2)
        self.board.move_and_promote(x1,y1,x2,y2)
        if t:
            val = self.piece_value(t.kind)
            self.gold += val
        cost = self.cost_for_piece(p.kind)
        self.player_ticks -= cost
        # check end conditions
        if self.player_ticks <= 0:
            self.message = "Vous manquez de temps !"
            self.end_stage(False)
            return
        # enemy king captured?
        ek = self.board.locate_king(self.enemy_color)
        if ek is None:
            self.message = "Roi ennemi capturé !"
            self.end_stage(True)
            return
        # turn switch logic
        if self.pre_moves_left > 0:
            self.pre_moves_left -= 1
            if self.pre_moves_left == 0:
                self.turn = self.enemy_color
        else:
            self.turn = self.enemy_color
    
    def do_enemy_turn(self):
        # unfreeze if freezing marker
        # enemy tries to move; skip if selected piece is frozen
        move = choose_move(self.board, self.enemy_color)
        if move is None:
            # no legal moves -> you win
            self.message = "L'ennemi est bloqué !"
            self.end_stage(True); return
        (x1,y1),(x2,y2) = move
        if (x1,y1) in self.frozen_coords:
            # consume freeze and skip move
            self.frozen_coords.discard((x1,y1))
            self.turn = self.player_color
            return
        p = self.board.get(x1,y1)
        t = self.board.get(x2,y2)
        self.board.move_and_promote(x1,y1,x2,y2)
        if t:
            # enemy capturing your piece -> no gold change
            pass
        cost = TICK_COSTS.get(p.kind,100)
        # apply -ticks enemy effects via multiplicative factor if set (tracked via enemy_tick_factor)
        cost *= getattr(self, "enemy_tick_factor", 1.0)
        self.enemy_ticks -= cost
        if self.enemy_ticks <= 0:
            self.message = "L'ennemi manque de temps !"
            self.end_stage(True); return
        # your king captured?
        pk = self.board.locate_king(self.player_color)
        if pk is None:
            self.message = "Votre roi est capturé..."
            self.end_stage(False); return
        self.turn = self.player_color
    
    def open_options(self):
        # simple toggle fullscreen
        self.toggle_fullscreen()
    
    def draw_menu(self):
        self.screen.fill((24,26,32))
        if self.assets.logo:
            lr = self.assets.logo.get_rect()
            sr = self.screen.get_rect()
            s = 0.6
            logo = pygame.transform.smoothscale(self.assets.logo, (int(lr.w*s), int(lr.h*s)))
            lr2 = logo.get_rect(center=(sr.w//2, sr.h//3))
            self.screen.blit(logo, lr2)
        draw_text(self.screen, "Entrée : Jouer   |   O : Options   |   Échap : Quitter", (self.screen.get_width()//2, int(self.screen.get_height()*0.7)), size=26, center=True)
    
    def draw_shop(self):
        self.screen.fill((22,24,30))
        draw_text(self.screen, "Boutique inter-manche — dépensez votre or", (40,30), size=28)
        draw_text(self.screen, f"Or : {self.gold}", (40,70), size=24)
        # List items
        y = 120
        self.shop_rects = []
        for item in CONTENT["shop_pool"]:
            name = item["name"]
            cost = item.get("cost",0)
            rect = pygame.Rect(40,y, 820, 36)
            pygame.draw.rect(self.screen, (35,38,48), rect, border_radius=6)
            draw_text(self.screen, f"{name}   (coût {cost})", (rect.x+10, rect.y+6), size=22)
            self.shop_rects.append((rect,item))
            y += 44
        draw_text(self.screen, "C : Continuer sans achat", (40, y+20), size=20, color=(180,190,200))
    
    def handle_shop_click(self, mx,my):
        for rect,item in self.shop_rects:
            if rect.collidepoint(mx,my):
                cost = item.get("cost",0)
                if self.gold < cost:
                    self.message = "Pas assez d'or."
                    return
                # handle purchase
                t = item["type"]
                if t == "tick":
                    self.player_ticks += item["amount"]
                elif t == "tick_enemy":
                    self.enemy_tick_factor = max(0.5, 1.0 + item["amount"])  # reduce up to 50%
                elif t == "economy" and item["effect"]=="double":
                    self.gold *= 2
                elif t == "consumable":
                    if item["effect"]=="freeze_random":
                        self.freeze_random_next = True
                    elif item["effect"]=="freeze_target":
                        self.freeze_target_stock += 1
                elif t == "start_power":
                    if item["effect"]=="double_once":
                        self.double_start = True
                    else:
                        self.double_start_always = True
                elif t == "bias":
                    if item["side"]=="white": self.bias_white += item["amount"]
                    else: self.bias_black += item["amount"]
                elif t == "zero_cost":
                    self.zero_cost_probs[item["piece"]] = min(0.95, self.zero_cost_probs.get(item["piece"],0)+item["chance"])
                elif t == "convert":
                    self.convert_piece_dialog()
                elif t == "buy":
                    self.buy_piece_dialog()
                self.gold -= cost
                self.message = f"Achat : {item['name']}"
                return
    
    def convert_piece_dialog(self):
        # Simplified: convert a P->N, P->B, N->R, R->Q etc based on available conversion costs
        # Find any convertible owned piece according to CONTENT["convert_costs"]
        options = []
        for k,v in CONTENT["convert_costs"].items():
            src, dst = k.split("->")
            if self.player_army.get(src,0) > 0:
                options.append((src,dst,v))
        if not options:
            self.message = "Aucune conversion possible."
            return
        # pick the cheapest by default
        options.sort(key=lambda x:x[2])
        src,dst,cost = options[0]
        if self.gold < cost:
            self.message = f"Conversion {src}->{dst} coûte {cost} or."
            return
        self.player_army[src] -= 1
        self.player_army[dst] = self.player_army.get(dst,0)+1
        self.gold -= cost
        self.message = f"Converti {src} en {dst}."
    
    def buy_piece_dialog(self):
        # Offer a random piece available, include Amazon if unlocked
        pool = ['P','N','B','R','Q']
        if self.meta["amazon_unlocked"]:
            pool.append('A')
        kind = random.choice(pool)
        cost = CONTENT["buy_costs"][kind]
        if self.gold < cost:
            self.message = f"Acheter {kind} coûte {cost} or."
            return
        self.player_army[kind] = self.player_army.get(kind,0)+1
        self.gold -= cost
        self.message = f"Acheté {kind}."
    
    def draw_meta(self):
        self.screen.fill((20,22,28))
        draw_text(self.screen, "Fin de run — Progression méta", (40,40), size=28)
        draw_text(self.screen, f"Amazon débloquée : {'Oui' if self.meta['amazon_unlocked'] else 'Non'}", (40,90), size=22)
        draw_text(self.screen, "Entrée : Retour menu (deck sauvegardé)", (40, 140), size=22)
    
    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)
            for ev in pygame.event.get():
                if ev.type == QUIT:
                    running = False
                elif ev.type == KEYDOWN:
                    if self.state == "menu":
                        if ev.key == K_RETURN:
                            self.state = "play"
                            self.reset_run()
                            self.start_stage()
                        elif ev.key == K_o:
                            self.open_options()
                        elif ev.key == K_ESCAPE:
                            running = False
                    elif self.state == "play":
                        if ev.key == K_ESCAPE:
                            # save current deck
                            self.meta["starting_deck"] = self.player_army
                            save_meta(self.meta)
                            self.state = "menu"
                        elif ev.key == K_o:
                            self.open_options()
                        elif ev.key == K_f:
                            if self.freeze_target_stock>0:
                                # enter freeze targeting mode
                                self.message = "Cliquez une pièce ennemie à geler (1 tour)."
                                self.state = "freeze_target"
                    elif self.state == "freeze_target":
                        if ev.key == K_ESCAPE:
                            self.state = "play"
                    elif self.state == "shop":
                        if ev.key == K_c:
                            # continue to next stage
                            self.start_stage()
                            self.state = "play"
                    elif self.state == "meta":
                        if ev.key == K_RETURN:
                            # persist deck to meta
                            self.meta["starting_deck"] = self.player_army
                            save_meta(self.meta)
                            self.state = "menu"
                elif ev.type == MOUSEBUTTONDOWN and ev.button==1:
                    mx,my = ev.pos
                    if self.state == "menu":
                        pass
                    elif self.state == "play":
                        ox,oy,sp = self.draw_board()  # compute layout
                        cell = self.to_cell(mx,my,ox,oy)
                        if cell:
                            x,y = cell
                            if self.selection is None:
                                p = self.board.get(x,y)
                                if p and p.color == self.player_color and self.turn==self.player_color:
                                    self.selection=(x,y)
                                    self.legal_moves = self.board.legal_moves_for(x,y)
                                else:
                                    self.message = "Sélectionnez une de vos pièces."
                            else:
                                if (x,y) in self.legal_moves:
                                    x1,y1 = self.selection
                                    self.do_player_move(x1,y1,x,y)
                                    self.selection=None; self.legal_moves=[]
                                else:
                                    self.selection=None; self.legal_moves=[]
                        else:
                            self.selection=None; self.legal_moves=[]
                    elif self.state == "freeze_target":
                        ox,oy,sp = self.draw_board()
                        cell = self.to_cell(mx,my,ox,oy)
                        if cell:
                            x,y = cell
                            p = self.board.get(x,y)
                            if p and p.color == self.enemy_color:
                                self.frozen_coords.add((x,y))
                                self.freeze_target_stock -= 1
                                self.message = "Pièce ennemie gelée (1 tour)."
                                self.state = "play"
                    elif self.state == "shop":
                        self.handle_shop_click(mx,my)
            
            # Update logic
            if self.state == "play":
                if self.turn == self.enemy_color:
                    self.do_enemy_turn()
            
            # Draw
            if self.state == "menu":
                self.draw_menu()
            elif self.state in ("play","freeze_target"):
                self.screen.fill((16,18,24))
                ox,oy,sp = self.draw_board()
            elif self.state == "shop":
                self.draw_shop()
            elif self.state == "meta":
                self.draw_meta()
            
            pygame.display.flip()
        
        # on quit, save meta deck
        self.meta["starting_deck"] = self.player_army
        save_meta(self.meta)
        pygame.quit()

def main():
    app = ChessRogueliteApp()
    app.run()

if __name__ == "__main__":
    main()
