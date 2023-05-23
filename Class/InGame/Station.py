from Class.Vector import Vector
from Class.InGame.Collider import Collider
import Class.InGame.ObjectRunner as runner
from Functions.ImageModifier import loadSprite, randomPaletteFor

import pygame, math, random, json, os

class Station(Collider, runner.Object):
    # =============================================

    faction = "neutral"
    World: runner.World
    sprite: pygame.Surface = None

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, pos : Vector) -> None:
        self.screen = screen

        Collider.__init__(self, Vector(0, -1).normalize(), pos)
        self.mass = 16
        
        self.resetSprite()
        
        self.World = World
        self.World.AddObject(self)

    def onCollide(self, collider: Collider, point: Vector, normal: Vector):
        return
    def dieFromRange(self) -> bool:
        return False

    def resetSprite(self):
        self.sprite = loadSprite(
            json.load(open("./Data/Cockpit/arrow.json", 'r')),
            runner.SPRITE_LIB,
            gridSize = 32,
            colors = randomPaletteFor("./Data/Cockpit/arrow.json")
        )
        
        self.sprite = pygame.transform.scale(self.sprite, (256, 256))
        self.updateMask()
    def update(self, debug = False):
        rect = self.sprite.get_rect(center=self.World.centerPositionTo(self.pos).toTuple())
        self.screen.blit(self.sprite, rect)

        if Vector.sqrDistance(self.pos, self.World.center_object.pos) < 512*512:
            self.World.global_effects["peace"] = self.pos.toTuple()
        elif self.World.global_effects.get("peace", (0, 0)) == self.pos.toTuple():
            self.World.global_effects.pop("peace")
        if (debug):
            pygame.draw.circle(self.screen, (0, 150, 255), rect.center, 512, 2)
    
    def updateMask(self):
        self.mask = pygame.mask.from_surface(self.sprite)
    def updatePhysics(self, deltaTime: float) -> bool:
        return True