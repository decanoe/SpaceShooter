# makes sure we are in the right directory
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
# ========================================

import pygame
from Class.Vector import Vector
from Class.Wall import Wall
from Class.EnemyShip import EnemyShip
from Class.Ship import Ship
from Class.Mine import Mine
import Class.ObjectRunner as runner
import random
import math

pygame.init()
clock = pygame.time.Clock()

#résolution de la fenêtre
size = width, height = 1024, 768
INNER_PART_SIZE = 0.4

stars: list[tuple[int, int, float]] = [(round(random.random() * width), round(random.random() * height), 1 - random.random() ** 2) for i in range(128)]

def update():
    screen.fill((0, 0, 0))

    for i in range(len(stars)):
        x: int = int(stars[i][0] - GAME_OBJECTS[0].pos.x * stars[i][2]) % width
        y: int = int(stars[i][1] - GAME_OBJECTS[0].pos.y * stars[i][2]) % height

        pygame.draw.line(screen, (255, 255, 255), (x, y), (x, y))
    
    # s = pygame.Surface(size)
    # s.set_alpha(1)
    # s.fill((0,0,0))
    # screen.blit(s, (0,0))
def Render_Text(string, color, where):
    font = pygame.font.Font(None, 30)
    text = font.render(string, 1, pygame.Color(color))
    screen.blit(text, where)

#création de l'interface graphique
screen: pygame.Surface = pygame.display.set_mode(size)
pygame.display.set_caption('OmegaRace2')
process: bool = True

GAME_OBJECTS: list[runner.Object] = []
ship: Ship = Ship(screen, GAME_OBJECTS, Vector(width * (1 - INNER_PART_SIZE) / 4, height / 2))
EnemyShip(screen, GAME_OBJECTS)
EnemyShip(screen, GAME_OBJECTS)
EnemyShip(screen, GAME_OBJECTS)
EnemyShip(screen, GAME_OBJECTS)

while process:
    deltaTime: float = clock.tick() / 1000.
    update()
    runner.UpdateAllPhysics(GAME_OBJECTS, deltaTime)
    runner.UpdateAllGraphics(GAME_OBJECTS)

    Render_Text(str(int(clock.get_fps())), (255,0,0), (0,0))

    events = pygame.event.get()
    ship.eventReactions(events, deltaTime)

    #on vérifie dans la liste des évènements si l'utilisateur appuie sur des touches ou clique avec sa souris
    for event in events:
        if event.type == pygame.QUIT:
            process = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:                                                               #Quit the game
                process = False
    
    pygame.display.update()

pygame.quit()