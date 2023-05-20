# makes sure we are in the right directory
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
# ========================================

import pygame
import Functions.Loader as loader
from Class.Vector import Vector
from Class.InGame.EnemyShip import EnemyShip
from Class.InGame.Ship import Ship
import Class.InGame.ObjectRunner as runner
import random, math, json

pygame.init()
clock = pygame.time.Clock()

#résolution de la fenêtre
size = width, height = 1024, 768
INNER_PART_SIZE = 0.4

stars: list[tuple[int, int, float]] = [(round(random.random() * width), round(random.random() * height), 1 - random.random() * random.random()) for i in range(128)]

def update():
    screen.fill((0, 0, 0))

    for i in range(len(stars)):
        x: int = int(stars[i][0] - WORLD.center_object.pos.x * stars[i][2]) % width
        y: int = int(stars[i][1] - WORLD.center_object.pos.y * stars[i][2]) % height

        pygame.draw.line(screen, (255, 255, 255), (x, y), (x, y))
    
    region = WORLD.getRegion(WORLD.center_object.pos)
    for x_ in range(-runner.LOAD_RADIUS // 2, runner.LOAD_RADIUS // 2 + 1):
        for y in range(-runner.LOAD_RADIUS, runner.LOAD_RADIUS + 1):
            x = x_ * 2 + (y - region[1] + region[0])%2

            color = (0, 255, 255)
            if abs(x) == runner.LOAD_RADIUS or abs(y) == runner.LOAD_RADIUS:
                color = (0, 0, 255)

            pos = Vector(x + region[0] - 0.5, y + region[1] - 0.5) * runner.REGION_SIZE
            pygame.draw.rect(
                screen,
                color,
                pygame.Rect(WORLD.centerPositionTo(pos).toTuple(), (runner.REGION_SIZE, runner.REGION_SIZE)),
                1)
    
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

WORLD: runner.World = runner.World()
ship: Ship = loader.loadPlayerShip(1, screen, WORLD)
EnemyShip(screen, WORLD)
EnemyShip(screen, WORLD)
EnemyShip(screen, WORLD)
EnemyShip(screen, WORLD)

while process:
    deltaTime: float = clock.tick() / 1000.
    update()
    WORLD.UpdateAllPhysics(deltaTime, clearLagNeeded = (100 - clock.get_fps()) / 50)
    WORLD.UpdateAllGraphics()

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