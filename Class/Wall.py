from Class.Vector import Vector
from Class.Collider import Collider
import Class.ObjectRunner as runner
import pygame
import math

class Wall(Collider, runner.Object):
    # =============================================

    World: runner.World
    sprite: pygame.Surface = None
    mask: pygame.Mask = None
    invert: bool = False

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, pos: Vector, size : Vector, invert: bool = False) -> None:
        self.sprite = pygame.Surface(size.toTuple())
        
        self.screen = screen
        
        Collider.__init__(self, Vector(0, 0), pos)
        self.mass = 16

        if not(invert):
            self.sprite = pygame.Surface(size.toTuple())
            self.sprite.fill((255, 255, 255))
            self.mask = pygame.mask.from_surface(self.sprite)
        else:
            self.invert = True
            self.sprite = pygame.Surface((size + Vector(2, 2)).toTuple(), pygame.SRCALPHA, 32)
            self.sprite.fill((255, 255, 255)) # walls
            self.sprite.fill((100, 100, 100, 10), pygame.Rect((1, 1), size.toTuple())) # hole
            self.mask = pygame.mask.from_surface(self.sprite)
        
        self.World = World
        self.World.AddObject(self)

    def getNormal(self, point: Vector, collider: Collider) -> Vector:
        rect: pygame.Rect = self.sprite.get_rect()
        d = (collider.pos - self.pos).div(Vector(rect.width / 2, rect.height / 2))

        if(self.invert):
            return d.flat() * -1
        else:
            return d.flat()
    def getHitbox(self) -> pygame.Rect:
        return pygame.Rect(
            self.pos.x - self.sprite.get_width() / 2,
            self.pos.y - self.sprite.get_height() / 2,
            self.sprite.get_width(),
            self.sprite.get_height())
    def canCollide(self, collider: Collider) -> bool:
        return self.mask != None
    def onCollide(self, collider: Collider, point: Vector):
        self.velocity = Vector(0, 0)

    def debug_update(self):
        rect: pygame.Rect = self.mask.get_rect(center = self.pos.toTuple())
        self.screen.blit(self.mask.to_surface(), rect)
    def update(self):
        if (self.invert): return
        rect: pygame.Rect = self.sprite.get_rect(center = self.World.centerPositionTo(self.pos).toTuple())
        self.screen.blit(self.sprite, rect)
    def updatePhysics(self, deltaTime: float) -> bool:
        return True