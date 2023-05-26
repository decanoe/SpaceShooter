from Class.UI.Item.UIitem import UIitem
import pygame

class Button(UIitem):
    # ==========================================
    text: pygame.Surface
    color1 : tuple[int, int, int]
    color2 : tuple[int, int, int]
    callback: classmethod
    # ==========================================

    def __init__(self, rect: pygame.Rect, callback: classmethod, text: str = "",
                 fontColor: tuple[int, int, int] = (255, 255, 255),
                 fontSize: int = 20,
                 color1: tuple[int, int, int] = (150, 150, 150),
                 color2: tuple[int, int, int] = (200, 200, 200)) -> None:
        super().__init__(rect)
        self.text = pygame.font.Font(None, fontSize).render(text, 1, pygame.Color(fontColor))
        self.color1 = color1
        self.color2 = color2
        self.callback = callback

    def handleEvents(self, events: list[pygame.event.Event], parentArea: pygame.Rect, deltaTime: float, canDetectMouse: bool = True):
        cursor = pygame.mouse.get_pos()
        if canDetectMouse and self.inside(cursor, parentArea) and pygame.mouse.get_pressed()[0]:
            self.callback()
    def draw(self, screen: pygame.Surface, blitArea: pygame.Rect, parentArea: pygame.Rect, canDetectMouse: bool = True):
        blitZone: pygame.Rect = self.rect.move(blitArea.topleft).clip(screen.get_rect())
        if blitZone.width == 0 or blitZone.height == 0:
            return
        cursor = pygame.mouse.get_pos()
        if canDetectMouse and self.inside(cursor, parentArea):
            pygame.draw.rect(screen, self.color2, blitZone)
        else:
            pygame.draw.rect(screen, self.color1, blitZone)
        
        screen.blit(self.text, self.text.get_rect(center = self.rect.move(blitArea.topleft).center))