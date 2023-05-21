from Class.Vector import Vector
from Class.InGame.Collider import Collider
import Class.InGame.ObjectRunner as runner
from Class.InGame.Projectile import Projectile
import pygame
import math
import random

SHIP_SQUARE_SIZE = 64

class Debris(Collider, runner.Object):
    # =============================================

    alive: float = 0
    sprite: pygame.Surface = None
    World: runner.World

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, pos: Vector, img: pygame.Surface) -> None:
        self.alive = runner.DEBRIS_LIFE
        
        self.screen = screen
        self.persistantData = False
        self.clearLagData = True

        super().__init__(Vector(0, 1), pos)
        self.mass = 0.25
        self.setVelocity(Vector.AngleToVector(random.random() * math.pi * 2) * self.mass * 200)
        self.direction = Vector.AngleToVector(random.random() * math.pi * 2)
        self.angle_velocity = (random.random() - 0.5) * 2
        self.pos += self.velocity / 10

        self.sprite = img
        self.mask = pygame.mask.from_surface(img)
        
        World.AddObject(self)
        self.World = World

    def getHitbox(self) -> pygame.Rect :
        return self.sprite.get_rect()
    def canCollide(self, collider: Collider) -> bool:
        if (type(collider) == Debris or type(collider) == Projectile): return False
        return super().canCollide(collider)
    def onCollide(self, collider: Collider, point: Vector):
        self.velocity /= self.mass
        self.mass = collider.mass
        self.velocity *= self.mass
        super().onCollide(collider, point)

    def blitImage(self, image: pygame.Surface):
        rotatedImage: pygame.Surface = pygame.transform.rotozoom(image, math.degrees(self.direction.getAngle(Vector(0, -1))), SHIP_SQUARE_SIZE / 48)
        rotatedImage.set_alpha(int(255 * min(1, self.alive / 10)))
        rect: pygame.Rect = rotatedImage.get_rect(center = self.World.centerPositionTo(self.pos).toTuple())
        self.screen.blit(rotatedImage, rect)
    def updateMask(self):
        self.mask = pygame.mask.from_surface(
            pygame.transform.rotozoom(self.sprite, math.degrees(self.direction.getAngle(Vector(0, -1))), 1.5))
    def update(self):
        self.blitImage(self.sprite)
    def updatePhysics(self, deltaTime: float) -> bool:
        a = self.angle_velocity

        # if (self.velocity.magnitude() > self.mass * 40):
        #     self.velocity = self.velocity.normalize() * self.mass * 40

        super().updatePhysics(deltaTime)
        self.angle_velocity = a

        self.updateMask()

        self.velocity /= 1 + deltaTime / 2
        self.alive -= deltaTime
        return self.alive > 0