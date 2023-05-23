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
    World: runner.World

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, pos: Vector, img: pygame.Surface) -> None:
        self.alive = runner.DEBRIS_LIFE
        
        self.screen = screen
        self.clearLagData = True

        super().__init__(Vector(0, 1), pos)
        self.mass = 0.25
        self.setVelocity(Vector.AngleToVector(random.random() * math.pi * 2) * self.mass * random.random() * 200)
        self.direction = Vector.AngleToVector(random.random() * math.pi * 2)
        self.angle_velocity = (random.random() - 0.5) * 2
        self.pos += self.velocity / 10

        self.sprite = pygame.transform.scale_by(img, 0.75)
        self.mask = pygame.mask.from_surface(self.sprite)
        
        World.AddObject(self)
        self.World = World

    def canCollide(self, collider: Collider) -> bool:
        if (type(collider) == Debris or type(collider) == Projectile): return False
        return super().canCollide(collider)
    def onCollide(self, collider: Collider, point: Vector, normal: Vector):
        self.velocity /= self.mass
        self.mass = collider.mass
        self.velocity *= self.mass
        self.angle_velocity *= 0.1
        super().onCollide(collider, point, normal)

    def blitImage(self, image: pygame.Surface):
        rotatedImage: pygame.Surface = pygame.transform.rotate(image, math.degrees(self.direction.getAngle(Vector(0, -1))))
        rotatedImage.set_alpha(int(255 * min(1, self.alive / 10)))
        rect: pygame.Rect = rotatedImage.get_rect(center = self.World.centerPositionTo(self.pos).toTuple())
        self.screen.blit(rotatedImage, rect)
    def updateMask(self):
        self.mask = pygame.mask.from_surface(
            pygame.transform.rotate(self.sprite, math.degrees(self.direction.getAngle(Vector(0, -1)))))
    def update(self, debug = False):
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