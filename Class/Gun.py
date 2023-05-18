from Class.Vector import Vector
from Class.Projectile import Projectile
import Class.ObjectRunner as runner
import pygame, math, random, json

SPRITE_SIZE = 64
PROJECTILE_SIZE = 32

# COOLDOWNS: dict = {
#     "sparkle" : 0.25,
#     "red sparkle" : 0.25,
#     "small cannon": 1,
#     "red small cannon": 1,
#     "rocket": 1,
#     "red rocket": 1,
#     "sparkle (ennemy)" : 1,
#     "red sparkle (ennemy)" : 1,
#     "small cannon (ennemy)": 2,
#     "red small cannon (ennemy)": 2,
#     "rocket (ennemy)": 3,
#     "red rocket (ennemy)": 3
#     }
# SPRITE: dict = {
#     "sparkle" : (0, 6),
#     "red sparkle" : (6, 6),
#     "small cannon": (0, 7),
#     "red small cannon": (6, 7),
#     "rocket": (0, 8),
#     "red rocket": (6, 8),
#     "sparkle (ennemy)" : (0, 6),
#     "red sparkle (ennemy)" : (6, 6),
#     "small cannon (ennemy)": (0, 7),
#     "red small cannon (ennemy)": (6, 7),
#     "rocket (ennemy)": (0, 8),
#     "red rocket (ennemy)": (6, 8)
#     }
# OFFSET: dict = {
#     "sparkle" : [7 * SPRITE_SIZE / 32, -7 * SPRITE_SIZE / 32],
#     "red sparkle" : [7 * SPRITE_SIZE / 32, -7 * SPRITE_SIZE / 32],
#     "small cannon": [6 * SPRITE_SIZE / 32],
#     "red small cannon": [6 * SPRITE_SIZE / 32],
#     "rocket": [11 * SPRITE_SIZE / 32],
#     "red rocket": [11 * SPRITE_SIZE / 32],
#     "sparkle (ennemy)" : [7 * SPRITE_SIZE / 32, -7 * SPRITE_SIZE / 32],
#     "red sparkle (ennemy)" : [7 * SPRITE_SIZE / 32, -7 * SPRITE_SIZE / 32],
#     "small cannon (ennemy)": [6 * SPRITE_SIZE / 32],
#     "red small cannon (ennemy)": [6 * SPRITE_SIZE / 32],
#     "rocket (ennemy)": [10 * SPRITE_SIZE / 32],
#     "red rocket (ennemy)": [10 * SPRITE_SIZE / 32]
#     }

class Gun():
    # =============================================

    reload_cooldown: float = 1
    sprites: pygame.Surface = None
    barrel_offset: list[int] = []
    animation_length: int = 1
    animation_start: float = 0
    animation_end: float = 1

    projectile_speed: float = 3
    projectile_strength: float = 5
    projectile_sprites: pygame.Surface = None
    projectile_animation_length: pygame.Surface = None

    currentCooldown: float = 0
    World: runner.World
    gunType: str = "small cannon"
    flip: bool = False
    mouseAim: bool = False

    # =============================================

    def __init__(self, World: runner.World, gunType: str = "small cannon") -> None:
        self.World = World
        self.gunType = gunType
        self.getInfo()

    def getInfo(self):
        with open('./Data/Weapons/' + self.gunType + '.json', 'r') as f:
            data: dict = json.load(f)
            self.barrel_offset = data.get('barrel_offset', [0])
            self.reload_cooldown = data.get('cooldown', 1)

            self.animation_length = data.get('animation_length', 1)
            self.sprites = pygame.transform.scale(runner.SPRITE_LIB.subsurface(
                data.get('animation_position', 0)[0] * 32,
                data.get('animation_position', 0)[1] * 32,
                self.animation_length * 32,
                32
                ), (self.animation_length * SPRITE_SIZE, SPRITE_SIZE))
            
            self.animation_start = data.get('animation_start', 0)
            self.animation_end = data.get('animation_end', 1)

            # projectile info
            pData = data.get('projectile', {})
            self.projectile_speed = pData.get('speed', 3)
            self.projectile_strength = pData.get('strength', 5)

            self.projectile_animation_length = pData.get('animation_length', 1)
            self.projectile_sprites = pygame.transform.scale(runner.SPRITE_LIB.subsurface(
                pData.get('animation_position', 0)[0] * 16,
                pData.get('animation_position', 0)[1] * 16,
                self.projectile_animation_length * 16,
                16
                ), (self.projectile_animation_length * PROJECTILE_SIZE, PROJECTILE_SIZE))

    def fire(self, ship, spread: float = 0.5, focal: float = 256) -> Vector:
        if (self.currentCooldown > 0): return
        self.flip = not(self.flip)
        self.currentCooldown = self.reload_cooldown

        for value in self.barrel_offset:
            offset: Vector = ship.direction.normal().normalize()
            offset *= value * SPRITE_SIZE / 32
            if self.flip:
                offset *= -1

            direction: Vector = (ship.pos + ship.direction * focal - (ship.pos + offset)).normalize()

            pr = Projectile(ship.screen, self.World,
                            parentCollider = ship,
                            pos = ship.pos + offset,
                            direction = direction,
                            sprites = self.projectile_sprites,
                            animation_length = self.projectile_animation_length,
                            strength = self.projectile_strength,
                            speed = self.projectile_speed)
            rotation: float = random.random() - 0.5
            rotation *= 0
            pr.velocity = pr.velocity.rotate(rotation * rotation * spread)
            pr.velocity += ship.velocity / ship.mass * pr.mass
            
            ship.velocity -= pr.velocity * pr.mass / ship.mass * (self.projectile_strength / 5)
    def reload(self, deltaTime: float):
        if (self.currentCooldown > 0):
            self.currentCooldown -= deltaTime
    def update(self, ship):
        loading: float = 1 - self.currentCooldown / self.reload_cooldown
        offset_frame: int = round(5 * loading - 0.5)
        offset_frame = max(0, min(offset_frame, 4))

        image = pygame.transform.flip(self.sprites.subsurface((offset_frame * SPRITE_SIZE, 0), (SPRITE_SIZE, SPRITE_SIZE)), self.flip, False)
        image: pygame.Surface = pygame.transform.rotate(image, math.degrees(ship.direction.getAngle(Vector(0, -1))))
        rect: pygame.Rect = image.get_rect(center = self.World.centerPositionTo(ship.pos).toTuple())
        ship.screen.blit(image, rect)