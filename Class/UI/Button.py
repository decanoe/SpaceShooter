import pygame

class Button:
    # ==========================================
    rect: pygame.Rect
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
        self.rect = rect
        self.text = pygame.font.Font(None, fontSize).render(text, 1, pygame.Color(fontColor))
        self.color1 = color1
        self.color2 = color2
        self.callback = callback

    def inside(self, pos: tuple[int, int]) -> bool:
        return self.rect.contains(pos, (0, 0))
    def click(self, pos: tuple[int, int]):
        if self.inside(pos):
            self.callback()
    def draw(self, screen: pygame.Surface, cursor: tuple[int, int]):
        if self.inside(cursor):
            pygame.draw.rect(screen, self.color2, self.rect)
        else:
            pygame.draw.rect(screen, self.color1, self.rect)
        
        screen.blit(self.text, self.text.get_rect(center = self.rect.center))