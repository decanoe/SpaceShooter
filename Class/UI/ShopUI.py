from Class.UI.Overlay import Overlay
import pygame

class ShopUI(Overlay):
    # ==========================================

    # ==========================================

    def __init__(self, screen) -> None:
        super().__init__(screen)
    
    def draw(self) -> bool:
        mouse = pygame.mouse.get_pos()

        background = pygame.Surface((self.screen.get_width() - 32, self.screen.get_height() - 32))
        background.fill((100, 100, 100))
        background.set_alpha(50)
        self.screen.blit(background, (16, 16))
        
        for button in self.buttons:
            button.draw(self.screen, mouse)

        return super().draw()