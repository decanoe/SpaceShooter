from Class.Utilities.Vector import Vector
from Class.Utilities.Collider import Collider
import Class.Utilities.ObjectRunner as runner
import pygame
import math
import random

ASTEROID_SIZE = 128

class Asteroid(Collider, runner.Object):
    # =============================================

    sprite: pygame.Surface = None
    World: runner.World

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, pos: Vector) -> None:
        self.screen = screen

        super().__init__(Vector(0, -1), pos)
        self.mass = 3
        self.setVelocity(Vector.AngleToVector(random.random() * math.pi * 2) * self.mass * random.random() * 200)

        self.randomize()

        World.AddObject(self)
        self.World = World
    def randomize(self):
        x = random.randint(13, 17) * 32
        
        self.sprite = runner.SPRITE_LIB.subsurface((x, 32), (32, 32)).copy()
        self.sprite = pygame.transform.rotate(self.sprite, random.random() * 360)
        self.sprite = pygame.transform.scale(self.sprite, (ASTEROID_SIZE, ASTEROID_SIZE)).copy()
        self.mask = pygame.mask.from_surface(self.sprite)

    def canCollide(self, collider: Collider) -> bool:
        if (type(collider) == Asteroid): return False
        return super().canCollide(collider)
    def onCollide(self, collider: Collider, point: Vector, normal: Vector):
        if (type(collider).__name__ == "Debris"):
            return

        inSpritePoint: Vector = point - self.pos
        inSpritePoint += Vector(self.sprite.get_width(), self.sprite.get_height()) / 2

        if (type(collider).__name__ == "Projectile"):
            self.damageSprite(inSpritePoint, collider.explodeStrength)
        else:
            super().onCollide(collider, point, normal)
            collisionStrength = (collider.last_frame_velocity * collider.mass - self.last_frame_velocity * self.mass).magnitude() / 100
            self.damageSprite(inSpritePoint, collisionStrength)
    def dieFromRange(self) -> bool:
        return False

    def damageSprite(self, point: Vector, strength: int):
        pygame.draw.circle(self.sprite, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 50), point.toTuple(), strength)
        cutout: pygame.Surface = pygame.mask.from_surface(self.sprite, 215).to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))

        edgeSprite: pygame.Surface = runner.SPRITE_LIB.subsurface((12*32, 0), (32, 32))
        edgeSprite = pygame.transform.rotozoom(edgeSprite, random.random() * 360 * 0, float(strength) / 8)
        rect: pygame.Rect = edgeSprite.get_rect(center = point.toTuple())
        self.sprite.blit(edgeSprite, rect)

        self.sprite.blit(cutout, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.mask = pygame.mask.from_surface(self.sprite)
    def update(self, debug = False):
        if (debug):
            img = self.mask.to_surface(setcolor=(255, 0, 0), unsetcolor=(0, 0, 0, 0))
            self.screen.blit(img, img.get_rect(center = self.World.centerPositionTo(self.pos).toTuple()))
        else:
            self.screen.blit(self.sprite, self.sprite.get_rect(center = self.World.centerPositionTo(self.pos).toTuple()))
    def updatePhysics(self, deltaTime: float) -> bool:
        super().updatePhysics(deltaTime)

        # self.updateMask()

        self.velocity /= 1 + deltaTime / 2
        return self.mask.count() > 256