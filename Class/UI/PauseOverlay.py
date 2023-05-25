from Class.UI.Overlay import Overlay
from Class.UI.Button import Button
import pygame

class PauseOverlay(Overlay):
    # ==========================================
    active: bool = True
    # ==========================================

    def __init__(self, screen: pygame.Surface) -> None:
        self.buttons.append(Button(
            pygame.Rect(screen.get_rect().centerx - 128, screen.get_rect().centery + 64, 256, 64),
            callback=self.quitPause,
            text="continue",
            fontSize=45
            ))

        self.buttons.append(Button(
            pygame.Rect(screen.get_rect().centerx - 128, screen.get_rect().centery + 128 + 32, 256, 64),
            callback=self.quitGame,
            text="quit",
            fontSize=45
            ))

        super().__init__(screen)
    
    def quitPause(self) -> None:
        self.active = False
    def quitGame(self) -> None:
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    def eventReactions(self, events: list[pygame.event.Event]) -> bool:
        mouse = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.quitPause()
        if pygame.mouse.get_pressed()[0]:
            for button in self.buttons:
                button.click(mouse)
        
        return self.active
    
    def draw(self):
        mouse = pygame.mouse.get_pos()

        background = pygame.Surface((self.screen.get_width() - 32, self.screen.get_height() - 32))
        background.fill((100, 100, 100))
        background.set_alpha(50)
        self.screen.blit(background, (16, 16))
        
        for button in self.buttons:
            button.draw(self.screen, mouse)