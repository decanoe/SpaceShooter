from Class.Utilities.Vector import Vector
from Class.Utilities.Collider import Collider
import Class.Utilities.ObjectRunner as runner
from Class.InGame.Debris import Debris
import pygame, math, random

ASTEROID_SIZE = 128

class Asteroid(Collider, runner.Object):
    # =============================================

    sprite: pygame.Surface = None
    rockIndex: int
    World: runner.World
    explosion_time: float = -1

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, pos: Vector) -> None:
        self.screen = screen

        super().__init__(Vector(0, -1), pos)
        self.mass = 3
        self.setVelocity(Vector.AngleToVector(random.random() * math.pi * 2) * self.mass * random.random() * 50)

        self.randomize()

        World.AddObject(self)
        self.World = World
    def randomize(self):
        self.rockIndex = random.randint(13, 17) * 32
        scaling = 0.5 + random.random()
        
        self.sprite = runner.SPRITE_LIB.subsurface((self.rockIndex, 32), (32, 32))
        self.sprite = pygame.transform.rotate(self.sprite, random.random() * 360)
        self.sprite = pygame.transform.scale(self.sprite, (int(scaling * ASTEROID_SIZE), int(scaling * ASTEROID_SIZE)))
        self.mask = pygame.mask.from_surface(self.sprite)
        
        self.size = 1 + self.mask.count() / (ASTEROID_SIZE * ASTEROID_SIZE) * 4

    def canCollide(self, collider: Collider) -> bool:
        if (self.explosion_time != -1): return False
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

        if (self.mask.count() <= (self.size - 1) * (ASTEROID_SIZE * ASTEROID_SIZE) / 16):
            self.size = 1 + self.mask.count() / (ASTEROID_SIZE * ASTEROID_SIZE) * 40
            self.explosion_time = 0
            if (type(collider).__name__ == "Projectile"):
                self.direction = (self.pos - (collider.pos - collider.velocity)).normalize()
            else:
                self.direction = normal
            self.velocity *= 0

            p = Vector.TupleToPos(self.mask.centroid())
            p -= Vector(self.sprite.get_width(), self.sprite.get_height()) / 2
            self.pos += p
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
    def blitImage(self, image: pygame.Surface):
        rotatedImage: pygame.Surface = pygame.transform.rotozoom(image, math.degrees(self.direction.getAngle(Vector(0, 1))), self.size)
        rect: pygame.Rect = rotatedImage.get_rect(center = self.World.centerPositionTo(self.pos).toTuple())
        self.screen.blit(rotatedImage, rect)
    def update(self, debug = False):
        if (self.explosion_time == -1):
            self.screen.blit(self.sprite, self.sprite.get_rect(center = self.World.centerPositionTo(self.pos).toTuple()))
        else:
            offset_frame: int = int(18 * self.explosion_time)
            offset_frame = min(17, offset_frame)
            self.blitImage(runner.EXPLOSION_LIB.subsurface((0, offset_frame * 64), (64, 64)))

    def updatePhysics(self, deltaTime: float) -> bool:
        super().updatePhysics(deltaTime)
        self.velocity /= 1 + deltaTime / 4

        if (self.explosion_time != -1):
            self.explosion_time += deltaTime * 2
        return self.explosion_time < 1