import os, pygame

# makes sure we are in the right directory
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
# ========================================

#résolution de la fenêtre
WINDOW_SIZE = width, height = 1024, 768

pygame.init()
pygame.display.set_mode(WINDOW_SIZE)

from Class.Utilities.Game import Game

game: Game = Game(1)
while game.gameLoop():
    pass

game.quit()