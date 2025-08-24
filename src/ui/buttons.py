
import pygame

class Button:
    def __init__(self, rect, text, on_click, font=None):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.on_click = on_click
        self.hover=False
        self.font = font or pygame.font.SysFont('arial', 20, bold=True)
    def draw(self, surface):
        base=(40,44,56); hov=(58,64,80)
        color = hov if self.hover else base
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        label=self.font.render(self.text, True, (235,238,245))
        lr=label.get_rect(center=self.rect.center)
        surface.blit(label, lr)
    def handle_event(self, ev):
        if ev.type==pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(ev.pos)
        elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
            if self.rect.collidepoint(ev.pos):
                self.on_click()
