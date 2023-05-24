# makes sure we are in the right directory
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)
# ========================================

#résolution de la fenêtre
size = width, height = 1024, 768
INNER_PART_SIZE = 0.4
SAVE_SLOT = 1
DEBUG_STATE = False

import pygame

pygame.init()
#création de l'interface graphique
screen: pygame.Surface = pygame.display.set_mode(size)
pygame.display.set_caption('OmegaRace2')
process: bool = True
clock = pygame.time.Clock()

import Functions.Loader as loader
from Class.Utilities.Vector import Vector
from Class.InGame.EnemyShip import EnemyShip
from Class.InGame.Asteroid import Asteroid
from Class.InGame.Station import Station
from Class.InGame.Ship import Ship
import Class.Utilities.ObjectRunner as runner
import random, math, time

stars: list[tuple[int, int, float]] = [(round(random.random() * width), round(random.random() * height), 1 - random.random() * random.random()) for i in range(128)]

def update():
    screen.fill((0, 0, 0))

    for i in range(len(stars)):
        x: int = int(stars[i][0] - WORLD.center_object.pos.x * stars[i][2])
        x -= math.floor(x / width) * width
        y: int = int(stars[i][1] - WORLD.center_object.pos.y * stars[i][2])
        y -= math.floor(y / height) * height

        pygame.draw.circle(screen, (200 * (1 - stars[i][2]*stars[i][2]*stars[i][2]), 55 + 150 * stars[i][2], 55 + 150 * stars[i][2] * stars[i][2]), (x, y), 1)
    
    if (DEBUG_STATE):
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

WORLD: runner.World = runner.World()
ship: Ship = loader.loadPlayerShip(SAVE_SLOT, screen, WORLD)
Station(screen, WORLD, Vector(0, 0))
for i in range(32):
    EnemyShip(screen, WORLD)
for i in range(32):
    Asteroid(screen, WORLD, Vector.AngleToVector(random.random() * math.pi * 2) * (random.random() + 1) * 512)

WORLD.score = 0

while process:
    deltaTime: float = clock.tick() / 1000.
    update()
    
    text = ""
    if not(ship.exploded):
        text = WORLD.UpdateAllPhysics(deltaTime, clearLagNeeded = (100 - clock.get_fps()) / 50)
        
    start = time.perf_counter()
    WORLD.UpdateAllGraphics(debug = DEBUG_STATE)
    finish = time.perf_counter()
    for i in range(len(text.split("\n"))):
        Render_Text(text.split("\n")[i], (255,0,0), (0, i * 16 + 16))
    Render_Text(f"graphics : {round(finish-start, 3)}", (255,0,0), (0, 16 * 5))

    if (ship.exploded):
        Render_Text(f"SCORE : {WORLD.score}", (255,255,255), (width / 2 - 50, height / 2))


    if (DEBUG_STATE):
        Render_Text(str(int(clock.get_fps())) + "   " + str(int(ship.pos.x)) + "/" + str(int(ship.pos.y)), (255,0,0), (0,0))

    events = pygame.event.get()
    if not(ship.exploded):
        ship.eventReactions(events, deltaTime)

    # Continuous key press
    keys_pressed = pygame.key.get_pressed()
    #on vérifie dans la liste des évènements si l'utilisateur appuie sur des touches ou clique avec sa souris
    for event in events:
        if event.type == pygame.QUIT:
            process = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:                                                               #Quit the game
                process = False
            if event.key == pygame.K_s:
                if keys_pressed[pygame.K_LCTRL]:
                    loader.savePlayerShip(SAVE_SLOT, ship)
            if event.key == pygame.K_F3:
                DEBUG_STATE = not(DEBUG_STATE)
    
    pygame.display.update()
pygame.quit()