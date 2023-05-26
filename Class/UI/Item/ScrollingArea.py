from Class.UI.Item.UIitem import UIitem
import pygame

class ScrollingArea(UIitem):
    # ==========================================
    rect: pygame.Rect
    color1 : tuple[int, int, int]
    color2 : tuple[int, int, int]
    items: list[UIitem] = []
    minY: int
    maxY: int
    targetY: int
    currentY: int
    # ==========================================

    def __init__(self, rect: pygame.Rect,
                 color1: tuple[int, int, int] = (150, 150, 150),
                 color2: tuple[int, int, int] = (200, 200, 200),
                 minY: int = 0, maxY: int = -1, startY: int = 0) -> None:
        super().__init__(rect)
        self.color1 = color1
        self.color2 = color2
        self.currentY = startY
        self.targetY = startY
        self.minY = minY
        if (maxY < minY):
            self.maxY = rect.height
        else:
            self.maxY = maxY

    def handleEvents(self, events: list[pygame.event.Event], parentArea: pygame.Rect, delaTime: float, canDetectMouse: bool = True):
        cursor = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEWHEEL and self.inside(cursor, parentArea):
                self.targetY = min(self.maxY, max(self.minY, self.targetY + event.y * 32))
        
        self.currentY += (self.targetY - self.currentY) * delaTime * 5

        for item in self.items:
            item.handleEvents(events, parentArea.move(self.rect.topleft).move(0, self.currentY), delaTime, canDetectMouse=self.inside(cursor, parentArea))
    def draw(self, screen: pygame.Surface, blitArea: pygame.Rect, parentArea: pygame.Rect, canDetectMouse: bool = True):
        blitZone: pygame.Rect = self.rect.move(blitArea.topleft).clip(screen.get_rect())
        if blitZone.width == 0 or blitZone.height == 0:
            return
        cursor = pygame.mouse.get_pos()

        pygame.draw.rect(screen, self.color1, blitZone)
        pygame.draw.rect(screen, self.color1, pygame.Rect(blitZone.right + 8, blitZone.top, 8, blitZone.height))
        sliderHeight = (blitZone.height - 2) * (1 - (self.maxY - self.minY) / (blitZone.height - 2)) * 2
        progress = self.currentY / (self.maxY - self.minY) * (blitZone.height - 2 - sliderHeight)
        pygame.draw.rect(screen, self.color2, pygame.Rect(blitZone.right + 9, blitZone.top + 1 + progress, 6, sliderHeight))

        for item in self.items:
            item.draw(screen.subsurface(blitZone), pygame.Rect((0, self.currentY), blitZone.size), parentArea.move(self.rect.topleft).move(0, self.currentY), canDetectMouse=self.inside(cursor, parentArea))