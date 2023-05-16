from Class.Vector import Vector
from Class.Collider import Collider
import Class.ObjectRunner as runner
from Class.Gun import Gun, COOLDOWNS
from Class.Projectile import Projectile, SPEED
from Class.Debris import Debris
import pygame
import math
import random

SHIP_SQUARE_SIZE = 64

class EnemyShip(Collider, runner.Object):
    # =============================================

    gun: Gun = None
    propulseCooldown: float = 0
    GAME_OBJECTS: list[runner.Object | Collider] = None
    lives: int = 1024
    parts: dict[str, tuple[int, int]] = {"ship" : (0, 0),
                   "wings" : (0, 64),
                   "engine" : (0, 128)}
    sprite: pygame.Surface = None

    # =============================================

    def __init__(self, screen : pygame.Surface, game_objects: list[runner.Object], pos: Vector = None) -> None:
        self.GAME_OBJECTS = game_objects
        self.GAME_OBJECTS.append(self)
        
        self.screen = screen

        if (pos == None):
            pos = game_objects[0].pos
            pos += Vector.AngleToVector(random.random() * math.pi * 2) * 768
        
        Collider.__init__(self, Vector(0, -1).normalize(), pos)
        self.mass = 2
        
        self.gun = Gun(game_objects)

        self.parts["ship"] = (random.randint(0, 17) * 32, random.randint(0, 1) * 32)
        self.parts["wings"] = (random.randint(0, 17) * 32, random.randint(2, 3) * 32)
        self.parts["engine"] = (random.randint(0, 10) * 32, random.randint(4, 5) * 32)

        self.gun.gunType = random.choice(list(COOLDOWNS.keys()))
        if not(self.gun.gunType.endswith(" (ennemy)")):
            self.gun.gunType += " (ennemy)"
        
        self.resetSprite()

    def propulse(self):
        if (self.timeSinceWallHit() >= 0.5 and self.propulseCooldown <= 0):
            self.velocity = self.direction * (1 + self.mass) * 125
            self.propulseCooldown = 1

    def getHitbox(self) -> pygame.Rect :
        rect = pygame.Rect(
            self.pos.x - 15,
            self.pos.y - 15,
            30,
            30)
        return rect
    def explode(self):
        for key in ["wings", "engine", "ship"]:
            mask = pygame.mask.from_surface(runner.SPRITE_LIB.subsurface(self.parts[key], (32, 32)), 254)
            
            for rect in mask.get_bounding_rects():
                Debris(self.screen, self.GAME_OBJECTS, self.pos, self.direction, rect.move(self.parts[key]))
        
        EnemyShip(self.screen, self.GAME_OBJECTS)
    def onCollide(self, collider: Collider, point: Vector):
        if type(collider) != Debris:
            super().onCollide(collider, point)

        if (type(collider) == Projectile):
            # self.lives -= 1
            # if (self.lives <= 0):
            #     self.explode()
        
            inSpritePoint: Vector = point - self.pos
            inSpritePoint = inSpritePoint.rotate(self.direction.getAngle(Vector(0, -1)))
            inSpritePoint += Vector(self.sprite.get_width(), self.sprite.get_height()) / 2

            # self.screen.blit(self.sprite, (800, 500))
            # pygame.draw.circle(self.screen, (255, 0, 0), (inSpritePoint + Vector(800, 500)).toTuple(), 2)

            self.damageSprite(inSpritePoint, collider.explodeStrength)
            if (self.mask.count() <= 1024):
                self.explode()
    def dieFromRange(self):
        EnemyShip(self.screen, self.GAME_OBJECTS)

    def resetSprite(self):
        self.sprite = runner.SPRITE_LIB.subsurface(self.parts["wings"], (32, 32)).copy()
        self.sprite.blit(runner.SPRITE_LIB.subsurface(self.parts["engine"], (32, 32)), (0, 0))
        self.sprite.blit(runner.SPRITE_LIB.subsurface(self.parts["ship"], (32, 32)), (0, 0))
        self.sprite = pygame.transform.scale(self.sprite, (SHIP_SQUARE_SIZE, SHIP_SQUARE_SIZE))
    def damageSprite(self, point: Vector, strength: int):
        pygame.draw.circle(self.sprite, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 50), point.toTuple(), strength)
        cutout: pygame.Surface = pygame.mask.from_surface(self.sprite, 215).to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))

        edgeSprite: pygame.Surface = runner.SPRITE_LIB.subsurface((12*32, 4 * 32), (32, 32))
        edgeSprite = pygame.transform.rotozoom(edgeSprite, random.random() * 360 * 0, float(strength) / 11)
        rect: pygame.Rect = edgeSprite.get_rect(center = point.toTuple())
        self.sprite.blit(edgeSprite, rect)

        self.sprite.blit(cutout, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.updateMask()
    def blitImage(self, image: pygame.Surface):
        rotatedImage: pygame.Surface = pygame.transform.rotate(image, math.degrees(self.direction.getAngle(Vector(0, -1))))
        rect: pygame.Rect = rotatedImage.get_rect(center = self.GAME_OBJECTS[0].centerOnPos(self.pos).toTuple())
        self.screen.blit(rotatedImage, rect)
    def update(self):
        
        # rect: pygame.Rect = self.mask.to_surface().get_rect(center = self.pos.toTuple())
        # self.screen.blit(self.mask.to_surface(), rect)

        self.blitImage(self.sprite)
        self.gun.update(self)
    def updateMask(self):
        self.mask = pygame.mask.from_surface(
            pygame.transform.rotate(self.sprite, math.degrees(self.direction.getAngle(Vector(0, -1)))))
    def updatePhysics(self, deltaTime: float) -> bool:
        self.velocity /= 1 + deltaTime * 0.5
        
        target_pos: Vector = self.GAME_OBJECTS[0].pos
        bulletSpeed = SPEED[self.gun.gunType]
        timeToReach = Vector.distance(self.pos, target_pos) / bulletSpeed
        target_pos += self.GAME_OBJECTS[0].velocity / (1 + self.GAME_OBJECTS[0].mass) * timeToReach * (1 + deltaTime)
        # pygame.draw.line(self.screen, (255, 0, 0), self.GAME_OBJECTS[0].centerOnPos(self.pos).toTuple(), self.GAME_OBJECTS[0].centerOnPos(target_pos).toTuple())

        direction: Vector = target_pos - self.pos

        angle = self.direction.getAngle(direction)
        self.angle_velocity = max(min(angle * 500, math.pi), -math.pi)
        

        Collider.updatePhysics(self, deltaTime)
        self.updateMask()

        self.gun.reload(deltaTime)
        if (timeToReach < 3 and abs(angle) < 0.01):
            self.gun.fire(self, focal=Vector.distance(self.pos, target_pos))

        if (self.propulseCooldown > 0):
            self.propulseCooldown -= deltaTime
        if Vector.distance(self.pos, target_pos) > 128:
            self.propulse()

        if (self.mask == None):
            return True
        else:
            return self.mask.count() > 1024