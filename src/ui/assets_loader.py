
import os
import pygame

class Assets:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.pieces = {}
        self.icons = {}
        self.logo = None
    
    def load(self, tile_size:int):
        # Load piece images and scale to tile_size-8
        pad = 8
        size = tile_size - pad
        for color in ('w','b'):
            for name in ('pawn','knight','bishop','rook','queen','king','amazon'):
                key = f"{color}_{name}"
                path = os.path.join(self.base_dir, "assets", "pieces", f"{key}.png")
                img = pygame.image.load(path).convert_alpha()
                self.pieces[key] = pygame.transform.smoothscale(img, (size,size))
        # icons
        for ico in ("coin","tick","freeze"):
            path = os.path.join(self.base_dir, "assets", "icons", f"{ico}.png")
            img = pygame.image.load(path).convert_alpha()
            self.icons[ico] = pygame.transform.smoothscale(img, (32,32))
        # logo
        path = os.path.join(self.base_dir, "assets", "logo.png")
        if os.path.exists(path):
            self.logo = pygame.image.load(path).convert_alpha()
