from Functions.ImageModifier import loadSprite, random_hsl
from Class.Vector import Vector
from Class.InGame.Collider import Collider
import Class.InGame.ObjectRunner as runner
from Class.InGame.Gun import Gun
from Class.InGame.Debris import Debris
import pygame, math, random, json, os

SHIP_SQUARE_SIZE = 64

class EnemyShip(Collider, runner.Object):
    # =============================================

    gun: Gun = None
    propulseCooldown: float = 0
    World: runner.World
    lives: int = 1024
    parts: dict
    sprite: pygame.Surface
    base_sprite: pygame.Surface

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, pos: Vector = None) -> None:
        self.screen = screen

        if (pos == None):
            pos = World.center_object.pos
            pos += Vector.AngleToVector(random.random() * math.pi * 2) * runner.LOAD_RADIUS * runner.REGION_SIZE
        
        Collider.__init__(self, Vector(0, -1).normalize(), pos)
        self.mass = 2
        
        gtype = random.choice(os.listdir("./Data/Weapons")).split('.')[0]
        self.gun = Gun(World, gtype)

        self.parts = {}
        self.parts["cockpit"] = random.choice(os.listdir("./Data/Cockpit/")).split('.')[0]
        self.parts["cockpit_color1"] = random_hsl(maxs=100, maxl=10)
        self.parts["cockpit_color2"] = random_hsl(maxs=100, maxl=25)

        self.parts["wings"] = random.choice(os.listdir("./Data/Wings/")).split('.')[0]
        self.parts["wings_color1"] = random_hsl(maxs=100, maxl=10)
        self.parts["wings_color2"] = random_hsl(maxs=100, maxl=25)
        
        self.parts["engine"] = random.choice(os.listdir("./Data/Engines/")).split('.')[0]
        self.parts["engine_color1"] = random_hsl(maxs=100, maxl=10)
        self.parts["engine_color2"] = random_hsl(maxs=100, maxl=25)

        self.resetSprite()
        
        self.World = World
        self.World.AddObject(self)

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
        xsplit = [0, random.randint(SHIP_SQUARE_SIZE / 4, SHIP_SQUARE_SIZE / 2), random.randint(SHIP_SQUARE_SIZE / 2, SHIP_SQUARE_SIZE * 3 / 4), SHIP_SQUARE_SIZE]
        ysplit = [0, random.randint(SHIP_SQUARE_SIZE / 4, SHIP_SQUARE_SIZE / 2), random.randint(SHIP_SQUARE_SIZE / 2, SHIP_SQUARE_SIZE * 3 / 4), SHIP_SQUARE_SIZE]
        
        for x in range(3):
            for y in range(3):
                Debris(self.screen, self.World, self.pos, self.base_sprite.subsurface(
                    xsplit[x], ysplit[y],
                    xsplit[x + 1] - xsplit[x], ysplit[y + 1] - ysplit[y]
                ))
        
        EnemyShip(self.screen, self.World)
        
    def onCollide(self, collider: Collider, point: Vector):
        if type(collider) != Debris:
            super().onCollide(collider, point)

        if (type(collider).__name__ == "Projectile"):
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
        EnemyShip(self.screen, self.World)

    def resetSprite(self):
        self.base_sprite = loadSprite(
            json.load(open("./Data/Wings/" + self.parts["wings"] + ".json", 'r')),
            runner.SPRITE_LIB,
            gridSize = 32,
            color1 = self.parts.get("wings_color1", (0, 0, 0)),
            color2 = self.parts.get("wings_color2", (0, 0, 0))
        )

        self.base_sprite.blit(loadSprite(
            json.load(open("./Data/Engines/" + self.parts["engine"] + ".json", 'r')),
            runner.SPRITE_LIB,
            gridSize = 32,
            color1 = self.parts.get("engine_color1", (0, 0, 0)),
            color2 = self.parts.get("engine_color2", (0, 0, 0))
        ), (0, 0))

        self.base_sprite.blit(loadSprite(
            json.load(open("./Data/Cockpit/" + self.parts["cockpit"] + ".json", 'r')),
            runner.SPRITE_LIB,
            gridSize = 32,
            color1 = self.parts.get("cockpit_color1", (0, 0, 0)),
            color2 = self.parts.get("cockpit_color2", (0, 0, 0))
        ), (0, 0))
        
        self.base_sprite = pygame.transform.scale(self.base_sprite, (SHIP_SQUARE_SIZE, SHIP_SQUARE_SIZE))
        self.sprite = self.base_sprite.copy()
    def damageSprite(self, point: Vector, strength: int):
        pygame.draw.circle(self.sprite, (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 50), point.toTuple(), strength)
        cutout: pygame.Surface = pygame.mask.from_surface(self.sprite, 215).to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))

        edgeSprite: pygame.Surface = runner.SPRITE_LIB.subsurface((12*32, 0), (32, 32))
        edgeSprite = pygame.transform.rotozoom(edgeSprite, random.random() * 360 * 0, float(strength) / 11)
        rect: pygame.Rect = edgeSprite.get_rect(center = point.toTuple())
        self.sprite.blit(edgeSprite, rect)

        self.sprite.blit(cutout, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.updateMask()
    def blitImage(self, image: pygame.Surface):
        rotatedImage: pygame.Surface = pygame.transform.rotate(image, math.degrees(self.direction.getAngle(Vector(0, -1))))
        rect: pygame.Rect = rotatedImage.get_rect(center = self.World.centerPositionTo(self.pos).toTuple())
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

        Collider.updatePhysics(self, deltaTime)
        self.updateMask()
        
        target_pos: Vector = self.World.center_object.pos
        dist = Vector.distance(self.pos, target_pos)
        direction: Vector = target_pos - self.pos
        self.gun.reload(deltaTime)

        if dist < self.screen.get_height() * 0.75:
            timeToReach = dist / (self.gun.projectile_speed * 100)
            target_pos += self.World.center_object.velocity / self.World.center_object.mass * timeToReach * (1 + deltaTime)
            pygame.draw.line(self.screen, (255, 0, 0), self.World.center_object.centerOnPos(self.pos).toTuple(), self.World.center_object.centerOnPos(target_pos).toTuple())

            angle = self.direction.getAngle(target_pos - self.pos)
            self.angle_velocity = max(min(angle * 50, math.pi), -math.pi)
        
            if (timeToReach < 3 and abs(angle) < .025):
                self.gun.fire(self, focal=Vector.distance(self.pos, target_pos))

            if (self.propulseCooldown > 0):
                self.propulseCooldown -= deltaTime
            if Vector.distance(self.pos, target_pos) > 128:
                self.propulse()
        else:
            line = (self.World.centerPositionTo(target_pos).toTuple(), self.World.centerPositionTo(self.pos).toTuple())
            self.screen.get_rect().clipline(line)

            angle = direction.getAngle(Vector(0, 1))
            overlay = runner.SPRITE_LIB.subsurface((13*32, 0), (32, 32))
            overlay = pygame.transform.scale(overlay, (80, 80))
            overlay = pygame.transform.rotate(overlay, math.degrees(angle))
            overlay.fill((255, 150, 10), special_flags=pygame.BLEND_RGBA_MULT)
            rect = overlay.get_rect(center = self.World.centerPositionTo(target_pos - direction.normalized() * 64).toTuple())
            self.screen.blit(overlay, rect)

        if (self.mask == None):
            return True
        else:
            return self.mask.count() > 1024