from __future__ import annotations
from Class.Utilities.Vector import Vector
from Class.Utilities.Collider import Collider
import Class.Utilities.ObjectRunner as runner
import pygame, math, random

PROJECTILE_SIZE = 32

class Projectile(Collider, runner.Object):
    # =============================================

    alive: float = 1
    World: runner.World
    faction: str = "neutral"
    timeBirth: float = 0.
    explodeStrength: int = 0
    speed: float
    sprites: pygame.Surface
    animation_length: int
    animation_speed: float

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, parentCollider: Collider, pos : Vector, direction : Vector,
                 sprites: pygame.Surface, animation_length = 0, animation_speed = 1, strength = 3, speed = 5) -> None:
        if (hasattr(parentCollider, "faction")):
            self.faction = parentCollider.faction
        self.screen = screen

        self.explodeStrength = strength
        self.sprites = sprites
        self.animation_length = animation_length
        self.animation_speed = animation_speed
        self.timeBirth = random.random() * animation_length

        super().__init__(direction, pos)
        self.mass = 0.1
        self.radius = 1
        self.setVelocity(direction * speed * self.mass * 100)

        self.updateMask()
        
        self.World = World
        World.AddObject(self)

    def onCollide(self, collider: Collider, point: Vector, normal: Vector):
        super().onCollide(collider, point, normal)
        self.direction = self.velocity.normalized()
        self.velocity *= 0.5

        self.alive = 0
    def canCollide(self, collider: Collider):
        if (self.alive != 1 or type(collider) == Projectile): return False

        if (self.faction == "neutral" or not(hasattr(collider, "faction"))): return True

        return self.faction != collider.faction

    def blitImage(self, image: pygame.Surface):
        rotatedImage = pygame.transform.rotate(image, math.degrees(self.direction.getAngle(Vector(0, -1))))
        rect: pygame.Rect = rotatedImage.get_rect(center = self.World.centerPositionTo(self.pos).toTuple())

        rotatedImage.set_alpha(int(255 * self.alive))
        self.screen.blit(rotatedImage, rect)
    def update(self, debug = False):
        offset_frame: int = int(self.animation_speed * self.timeBirth)
        offset_frame -= offset_frame // self.animation_length * self.animation_length

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