from Class.UI.Item.UIitem import UIitem
import pygame

class Overlay:
    # ==========================================
    items: list[UIitem]
    pauseGame: bool = True
    screen: pygame.Surface
    rect: pygame.Rect
    # ==========================================

    def __init__(self, screen: pygame.Surface, rect: pygame.Rect = None) -> None:
        if rect == None:
            self.rect = screen.get_rect()
        else:
            self.rect = rect
        self.screen = screen
        self.items = []
    
    def handleEvents(self, events: list[pygame.event.Event], deltaTime: float) -> bool:
        '''
        return true if the overlay need to stay, false if no longer needed
        '''
        for item in self.items:
            item.handleEvents(events, self.rect, deltaTime)
        return True
    def draw(self):
        blitZone: pygame.Rect = self.rect.clip(self.screen.get_rect())
        if blitZone.width == 0 or blitZone.height == 0:
            return
        for item in self.items:
            item.draw(self.screen.subsurface(blitZone), pygame.Rect((0, 0), blitZone.size), self.rect)