from Class.Vector import Vector
from Class.Projectile import Projectile
import Class.ObjectRunner as runner
import pygame
import math
import random

SPRITE_SIZE = 64

COOLDOWNS: dict = {
    "sparkle" : 0.25,
    "red sparkle" : 0.25,
    "small cannon": 1,
    "red small cannon": 1,
    "rocket": 1,
    "red rocket": 1,
    "sparkle (ennemy)" : 1,
    "red sparkle (ennemy)" : 1,
    "small cannon (ennemy)": 2,
    "red small cannon (ennemy)": 2,
    "rocket (ennemy)": 3,
    "red rocket (ennemy)": 3
    }
SPRITE: dict = {
    "sparkle" : (0, 6),
    "red sparkle" : (6, 6),
    "small cannon": (0, 7),
    "red small cannon": (6, 7),
    "rocket": (0, 8),
    "red rocket": (6, 8),
    "sparkle (ennemy)" : (0, 6),
    "red sparkle (ennemy)" : (6, 6),
    "small cannon (ennemy)": (0, 7),
    "red small cannon (ennemy)": (6, 7),
    "rocket (ennemy)": (0, 8),
    "red rocket (ennemy)": (6, 8)
    }
OFFSET: dict = {
    "sparkle" : [7 * SPRITE_SIZE / 32, -7 * SPRITE_SIZE / 32],
    "red sparkle" : [7 * SPRITE_SIZE / 32, -7 * SPRITE_SIZE / 32],
    "small cannon": [6 * SPRITE_SIZE / 32],
    "red small cannon": [6 * SPRITE_SIZE / 32],
    "rocket": [11 * SPRITE_SIZE / 32],
    "red rocket": [11 * SPRITE_SIZE / 32],
    "sparkle (ennemy)" : [7 * SPRITE_SIZE / 32, -7 * SPRITE_SIZE / 32],
    "red sparkle (ennemy)" : [7 * SPRITE_SIZE / 32, -7 * SPRITE_SIZE / 32],
    "small cannon (ennemy)": [6 * SPRITE_SIZE / 32],
    "red small cannon (ennemy)": [6 * SPRITE_SIZE / 32],
    "rocket (ennemy)": [10 * SPRITE_SIZE / 32],
    "red rocket (ennemy)": [10 * SPRITE_SIZE / 32]
    }

class Gun():
    # =============================================

    fireCooldown: float = 0
    World: runner.World
    gunType: str = "small cannon"
    flip: bool = False
    mouseAim: bool = False

    # =============================================

    def __init__(self, World: runner.World, gunType: str = "small cannon") -> None:
        self.World = World
        self.gunType = gunType

    def fire(self, ship, spread: float = 0.5, focal: float = 256) -> Vector:
        if (self.fireCooldown > 0): return
        self.flip = not(self.flip)
        self.fireCooldown = COOLDOWNS[self.gunType]

        for value in OFFSET[self.gunType]:
            offset: Vector = ship.direction.normal().normalize()
            offset *= value
            if self.flip:
                offset *= -1

            direction: Vector = (ship.pos + ship.direction * focal - (ship.pos + offset)).normalize()

            pr = Projectile(ship.screen, self.World,
                            parentCollider=ship,
                            pos=ship.pos + offset,
                            direction=direction,
                            gunType=self.gunType)
            rotation: float = random.random() - 0.5
            rotation *= 0
            pr.velocity = pr.velocity.rotate(rotation * rotation * spread)
            pr.velocity += ship.velocity / ship.mass * pr.mass
            
            ship.velocity -= pr.velocity * pr.mass / ship.mass
    def reload(self, deltaTime: float):
        if (self.fireCooldown > 0):
            self.fireCooldown -= deltaTime
    def update(self, ship):
        loading: float = COOLDOWNS[self.gunType] - self.fireCooldown
        offset_frame: int = round(5 * loading / COOLDOWNS[self.gunType] - 0.5)
        offset_frame = max(0, min(offset_frame, 4))

        image: pygame.Surface = runner.SPRITE_LIB.subsurface((
            (SPRITE[self.gunType][0] + offset_frame) * 32,
            SPRITE[self.gunType][1] * 32),
            (32, 32))

        image = pygame.transform.flip(image, self.flip, False)
        image: pygame.Surface = pygame.transform.scale(image, (SPRITE_SIZE, SPRITE_SIZE))
        image: pygame.Surface = pygame.transform.rotate(image, math.degrees(ship.direction.getAngle(Vector(0, -1))))
        rect: pygame.Rect = image.get_rect(center = self.World.centerPositionTo(ship.pos).toTuple())
        ship.screen.blit(image, rect)