from Class.UI.Interface.Overlay import Overlay
from Class.UI.Item.ScrollingArea import ScrollingArea
from Class.UI.Item.Button import Button
import pygame

class ShopUI(Overlay):
    # ==========================================
    active: bool = True
    # ==========================================

    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen, rect = pygame.Rect(
            (screen.get_width() / 2 + 48, 16),
            (screen.get_width() / 2 - 64, screen.get_height() - 32)))
        
        scrollArea: ScrollingArea = ScrollingArea(
            pygame.Rect(16, 16, self.rect.width - 32 - 16, self.rect.height - 32),
            color1=(100, 100, 100),
            maxY=self.rect.height - 64 - 32 - 16
            )
        scrollArea.items.append(Button(
            pygame.Rect(8, 8, scrollArea.rect.width - 16, 64),
                callback=self.quitPause,
                text="test"
            ))
        self.items.append(scrollArea)
    
    def quitPause(self):
        self.active = False
    def handleEvents(self, events: list[pygame.event.Event], deltaTime: float) -> bool:
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quitPause()
        
        super().handleEvents(events, deltaTime)
        
        return self.active
    
    def draw(self):
        background = pygame.Surface(self.rect.size, flags=pygame.SRCALPHA)
        background.fill((100, 100, 100, 50))
        self.screen.blit(background, self.rect.topleft)
        
        return super().draw()