from __future__ import annotations
from Class.Vector import Vector
from Class.InGame.Collider import Collider
import Class.InGame.ObjectRunner as runner
import pygame
import math

PROJECTILE_SIZE = 32

class Projectile(Collider, runner.Object):
    # =============================================

    alive: float = 1
    World: runner.World
    parentCollider: Collider = None
    timeBirth: int = 0
    explodeStrength: int = 0
    speed: float
    sprites: pygame.Surface
    animation_length: int
    animation_speed: float

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, parentCollider: Collider, pos : Vector, direction : Vector,
                 sprites: pygame.Surface, animation_length = 0, animation_speed = 1, strength = 3, speed = 5) -> None:
        self.parentCollider = parentCollider
        self.screen = screen
        self.persistantData = False

        self.explodeStrength = strength
        self.sprites = sprites
        self.animation_length = animation_length
        self.animation_speed = animation_speed

        super().__init__(direction, pos)
        self.mass = 0.1
        self.radius = 1
        self.setVelocity(direction * speed * self.mass * 100)
        # self.velocity += parentCollider.velocity / parentCollider.mass * self.mass

        self.updateMask()
        
        self.World = World
        World.AddObject(self)

    def onCollide(self, collider: Collider, point: Vector):
        super().onCollide(collider, point)
        self.direction = self.velocity.normalized()
        self.velocity *= 0.5

        if (type(collider).__name__ != "Wall"):
            self.alive = 0
        else:
            self.alive = 0.99
            self.updateMask()
    def canCollide(self, collider: Collider):
        if (type(collider) == Projectile): return False
        if (self.parentCollider == collider or self.alive != 1): return False
        return super().canCollide(collider)

    def blitImage(self, image: pygame.Surface):
        rotatedImage = pygame.transform.rotate(image, math.degrees(self.direction.getAngle(Vector(0, -1))))
        rect: pygame.Rect = rotatedImage.get_rect(center = self.World.centerPositionTo(self.pos).toTuple())

        rotatedImage.set_alpha(int(255 * self.alive))
        self.screen.blit(rotatedImage, rect)
    def update(self):
        offset_frame: int = int(self.animation_speed * self.timeBirth) % self.animation_length

        self.blitImage(self.sprites.subsurface(offset_frame * PROJECTILE_SIZE, 0, PROJECTILE_SIZE, PROJECTILE_SIZE))
    def updateMask(self):
        image: pygame.Surface = self.sprites.subsurface(0, 0, PROJECTILE_SIZE, PROJECTILE_SIZE)
        image = pygame.transform.rotate(image, math.degrees(self.direction.getAngle(Vector(0, -1))))
        self.mask = pygame.mask.from_surface(image)
    def updatePhysics(self, deltaTime: float) -> bool:
        super().updatePhysics(deltaTime)
        if (self.alive != 1):
            self.alive -= deltaTime * 2

        self.timeBirth += deltaTime
        self.pos -= self.velocity * deltaTime * 100 / (1 + self.mass) * (1 - self.alive)

        return self.alive > 0