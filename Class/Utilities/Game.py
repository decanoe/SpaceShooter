import pygame, math, time, random
from Class.Utilities.Vector import Vector
from Class.Utilities.ObjectRunner import World
import Functions.Loader as loader

from Class.UI.Overlay import Overlay
from Class.UI.PauseOverlay import PauseOverlay

from Class.InGame.Ship import Ship
from Class.InGame.EnemyShip import EnemyShip
from Class.InGame.Station import Station
from Class.InGame.Asteroid import Asteroid

SAVE_SLOT = 1
WINDOW_SIZE = width, height = pygame.display.get_window_size()

class Game:
    world: World
    screen: pygame.Surface
    clock: pygame.time.Clock
    DEBUG_STATE = False

    overlayList: list[Overlay] = []

    def __init__(self, saveSlot: int = 0):
        
        self.screen: pygame.Surface = pygame.display.get_surface()
        pygame.display.set_caption('OmegaRace2')
        self.clock = pygame.time.Clock()

        self.world: World = World(WINDOW_SIZE)
        self.ship: Ship = loader.loadPlayerShip(saveSlot, self.screen, self.world)
        Station(self.screen, self.world, Vector(0, 0))
        for i in range(8):
            EnemyShip(self.screen, self.world)
        for i in range(32):
            Asteroid(self.screen, self.world, Vector.AngleToVector(random.random() * math.pi * 2) * (random.random() + 1) * 512)

        self.world.score = 0
    
    
    def Render_Text(self, string, color, where):
        font = pygame.font.Font(None, 30)
        text = font.render(string, 1, pygame.Color(color))
        self.screen.blit(text, where)

    def gameLoop(self) -> bool:
        paused = False
        events: list[pygame.event.Event] = pygame.event.get()
        deltaTime: float = self.clock.tick() / 1000.
        
        start = time.perf_counter()
        self.world.UpdateAllGraphics(self.screen, debug = self.DEBUG_STATE)

        i = 0
        while i < len(self.overlayList):
            if self.overlayList[0].pauseGame:
                paused = True
            
            if self.overlayList[0].eventReactions(events):
                self.overlayList[0].draw()
                i += 1
            else:
                self.overlayList.pop(i)
                continue
        
        finish = time.perf_counter()

        text = ""
        if not(self.ship.exploded or paused):
            text = self.world.UpdateAllPhysics(deltaTime)
        for i in range(len(text.split("\n"))):
            self.Render_Text(text.split("\n")[i], (255,0,0), (0, i * 16 + 16))
        self.Render_Text(f"graphics : {round(finish-start, 3)}", (255,0,0), (0, 16 * 5))

        if (self.ship.exploded):
            self.Render_Text(f"SCORE : {self.world.score}", (255,255,255), (width / 2 - 50, height / 2))

        if (self.DEBUG_STATE):
            self.Render_Text(str(int(self.clock.get_fps())) + "   " + str(int(self.ship.pos.x)) + "/" + str(int(self.ship.pos.y)), (255,0,0), (0,0))

        if not(self.ship.exploded or paused):
            self.ship.eventReactions(events, deltaTime)

        # Continuous key press
        keys_pressed = pygame.key.get_pressed()
        #on vérifie dans la liste des évènements si l'utilisateur appuie sur des touches ou clique avec sa souris
        for event in events:
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and not(paused):
                    self.overlayList.append(PauseOverlay(self.screen))
                if event.key == pygame.K_s:
                    if keys_pressed[pygame.K_LCTRL]:
                        loader.savePlayerShip(SAVE_SLOT, self.ship)
                if event.key == pygame.K_F3:
                    self.DEBUG_STATE = not(self.DEBUG_STATE)
        
        pygame.display.update()
        return True
    
    def quit(self):
        pygame.quit()