from Class.Utilities.Vector import Vector
from Class.Utilities.Collider import Collider
import Class.Utilities.ObjectRunner as runner
from Class.InGame.Projectile import Projectile
import pygame
import math
import random

SHIP_SQUARE_SIZE = 64

class Debris(Collider, runner.Object):
    # =============================================

    alive: float = 0
    sprite: pygame.Surface = None
    base_sprite: pygame.Surface = None
    World: runner.World

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, pos: Vector, img: pygame.Surface) -> None:
        self.alive = runner.DEBRIS_LIFE
        
        self.screen = screen

        super().__init__(Vector(0, 1), pos)
        self.mass = 2
        self.setVelocity(Vector.AngleToVector(random.random() * math.pi * 2) * self.mass * random.random() * 200)
        self.direction = Vector.AngleToVector(random.random() * math.pi * 2)
        self.angle_velocity = (random.random() - 0.5) * 2
        self.pos += self.velocity / 10

        mask = pygame.mask.from_surface(img)

        if len(mask.get_bounding_rects()) == 0:
            self.alive = 0
            self.base_sprite = pygame.transform.scale_by(img, 0.75)
            self.mask = pygame.mask.from_surface(self.base_sprite)
        else:
            self.base_sprite = pygame.transform.scale_by(img.subsurface(mask.get_bounding_rects()[0]), 0.75)
            self.mask = pygame.mask.from_surface(self.base_sprite)
        self.sprite = self.base_sprite
        
        World.AddObject(self)
        self.World = World

    def canCollide(self, collider: Collider) -> bool:
        if (type(collider) == Debris or type(collider) == Projectile): return False
        return super().canCollide(collider)
    def onCollide(self, collider: Collider, point: Vector, normal: Vector):
        self.angle_velocity = max(-.5, min(.5, self.angle_velocity))
        super().onCollide(collider, point, normal)

    def updateMask(self):
        self.mask = pygame.mask.from_surface(
            pygame.transform.rotate(self.sprite, math.degrees(self.direction.getAngle(Vector(0, -1)))))
    def update(self, debug = False):
        self.sprite.set_alpha(int(255 * min(1, self.alive / 10)))
        self.screen.blit(self.sprite, self.sprite.get_rect(center = self.World.centerPositionTo(self.pos).toTuple()))
    def updatePhysics(self, deltaTime: float) -> bool:
        super().updatePhysics(deltaTime)

        if abs(self.angle_velocity) < 0.01:
            self.angle_velocity = 0
        else:
            self.sprite = pygame.transform.rotate(self.base_sprite, math.degrees(self.direction.getAngle(Vector(0, -1))))
            self.updateMask()

        self.velocity /= 1 + deltaTime / 2
        self.alive -= deltaTime
        return self.alive > 0