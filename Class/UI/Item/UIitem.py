import pygame

class UIitem:
    # ==========================================
    rect: pygame.Rect
    # ==========================================

    def __init__(self, rect: pygame.Rect) -> None:
        self.rect = rect

    def inside(self, pos: tuple[int, int], area: pygame.Rect) -> bool:
        return self.rect.move(area.topleft).contains(pos, (0, 0))
    def handleEvents(self, events: list[pygame.event.Event], parentArea: pygame.Rect, deltaTime: float, canDetectMouse: bool = True):
        pass
    def draw(self, screen: pygame.Surface, blitArea: pygame.Rect, parentArea: pygame.Rect, canDetectMouse: bool = True):
        pass