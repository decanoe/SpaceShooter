from Class.UI.Interface.Overlay import Overlay
from Class.UI.Item.Button import Button
import pygame

class PauseOverlay(Overlay):
    # ==========================================
    active: bool = True
    # ==========================================

    def __init__(self, screen: pygame.Surface) -> None:
        super().__init__(screen, rect=pygame.Rect(16, 16, screen.get_width() - 32, screen.get_height() - 32))

        self.items.append(Button(
            pygame.Rect(screen.get_rect().centerx - 128 - 32, screen.get_rect().centery + 32, 256, 64),
            callback=self.quitPause,
            text="continue",
            fontSize=45
            ))

        self.items.append(Button(
            pygame.Rect(screen.get_rect().centerx - 128 - 32, screen.get_rect().centery + 128, 256, 64),
            callback=self.quitGame,
            text="quit",
            fontSize=45
            ))
    
    def quitPause(self) -> None:
        self.active = False
    def quitGame(self) -> None:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
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
        
        super().draw()