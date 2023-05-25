from Class.UI.Button import Button
import pygame

class Overlay:
    # ==========================================
    buttons: list[Button] = []
    pauseGame: bool = True
    screen: pygame.Surface
    # ==========================================

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
    
    def eventReactions(self, events: list[pygame.event.Event]) -> bool:
        return False
    def draw(self):
        pass