from Functions.ImageModifier import loadSprite, randomPaletteFor
from Class.Vector import Vector
from Class.InGame.Collider import Collider
import Class.InGame.ObjectRunner as runner
from Class.InGame.Gun import Gun
from Class.InGame.Debris import Debris
import pygame, math, random, json, os

SHIP_SQUARE_SIZE = 64

class EnemyShip(Collider, runner.Object):
    # =============================================

    faction = "enemy"
    gun: Gun = None
    propulseCooldown: float = 0
    World: runner.World
    lives: int = 1024
    parts: dict
    sprite: pygame.Surface
    base_sprite: pygame.Surface

    debug_target_pos: Vector = None

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, pos: Vector = None) -> None:
        self.screen = screen

        if (pos == None):
            pos = World.center_object.pos
            pos += Vector.AngleToVector(random.random() * math.pi * 2) * runner.REGION_SIZE * 3.5
        
        Collider.__init__(self, Vector(0, -1).normalize(), pos)
        self.mass = 2
        
        gtype = random.choice(os.listdir("./Data/Weapons")).split('.')[0]
        self.gun = Gun(World, gtype, randomPaletteFor("./Data/Weapons/" + gtype + ".json"))

        self.parts = {}
        self.parts["cockpit"] = random.choice(os.listdir("./Data/Cockpit/")).split('.')[0]
        self.parts["cockpit_colors"] = randomPaletteFor("./Data/Cockpit/" + self.parts["cockpit"] + ".json")

        self.parts["wings"] = random.choice(os.listdir("./Data/Wings/")).split('.')[0]
        self.parts["wings_colors"] = randomPaletteFor("./Data/Wings/" + self.parts["wings"] + ".json")
        
        self.parts["engine"] = random.choice(os.listdir("./Data/Engines/")).split('.')[0]
        self.parts["engine_colors"] = randomPaletteFor("./Data/Engines/" + self.parts["engine"] + ".json")

        self.resetSprite()
        
        self.World = World
        self.World.AddObject(self)

    def propulse(self, deltaTime, force: float = 5, direction: Vector = None):
        if (self.timeSinceWallHit() >= 0.4):
            if (direction == None):
                direction = self.direction
            self.velocity += direction * force * (1 + self.mass) * deltaTime * 40
    def propulseForce(self, direction) -> float:
        f: float = 2 + 4 * abs(self.direction.dot(direction))
        if (self.direction.dot(direction) > -0.25):
            return f
        else:
            return f / 2
    
    def explode(self):
        for key in [("Wings/", "wings"), ("Engines/", "engine"), ("Cockpit/", "cockpit")]:
            img = loadSprite(
                json.load(open("./Data/" + key[0] + self.parts[key[1]] + ".json", 'r')),
                runner.SPRITE_LIB,
                gridSize = 32,
                colors = self.parts[key[1] + "_colors"]
            )
            xsplit = [0, random.randint(32 // 4, 32 * 3 // 4), 32]
            ysplit = [0, random.randint(32 // 4, 32 * 3 // 4), 32]
            
            for x in range(2):
                for y in range(2):
                    Debris(self.screen, self.World, self.pos, img.subsurface(
                        xsplit[x], ysplit[y],
                        xsplit[x + 1] - xsplit[x], ysplit[y + 1] - ysplit[y]
                    ))
        
        EnemyShip(self.screen, self.World)
        
    def onCollide(self, collider: Collider, point: Vector, normal: Vector):
        if type(collider) == Debris:
            return
        super().onCollide(collider, point, normal)

        inSpritePoint: Vector = point - self.pos
        inSpritePoint = inSpritePoint.rotate(self.direction.getAngle(Vector(0, -1)))
        inSpritePoint += Vector(self.sprite.get_width(), self.sprite.get_height()) / 2

        if (type(collider).__name__ == "Projectile"):
            self.damageSprite(inSpritePoint, collider.explodeStrength)
            if (self.mask.count() <= 1024):
                self.explode()
        else:
            collisionStrength = (collider.last_frame_velocity * collider.mass - self.last_frame_velocity * self.mass).magnitude() / 200
            self.damageSprite(inSpritePoint, collisionStrength)
            if (self.mask.count() <= 1024):
                self.explode()
    def dieFromRange(self):
        EnemyShip(self.screen, self.World)
        return True

    def resetSprite(self):
        self.base_sprite = loadSprite(
            json.load(open("./Data/Wings/" + self.parts["wings"] + ".json", 'r')),
            runner.SPRITE_LIB,
            gridSize = 32,
            colors = self.parts.get("wings_colors", [])
        )

        self.base_sprite.blit(loadSprite(
            json.load(open("./Data/Engines/" + self.parts["engine"] + ".json", 'r')),
            runner.SPRITE_LIB,
            gridSize = 32,
            colors = self.parts.get("engine_colors", [])
        ), (0, 0))

        self.base_sprite.blit(loadSprite(
            json.load(open("./Data/Cockpit/" + self.parts["cockpit"] + ".json", 'r')),
            runner.SPRITE_LIB,
            gridSize = 32,
            colors = self.parts.get("cockpit_colors", [])
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
    def update(self, debug = False):
        
        # rect: pygame.Rect = self.mask.to_surface().get_rect(center = self.pos.toTuple())
        # self.screen.blit(self.mask.to_surface(), rect)

        self.blitImage(self.sprite)
        self.gun.update(self)

        if (debug and self.debug_target_pos != None):
            pygame.draw.line(self.screen, (255, 0, 0), self.World.center_object.centerOnPos(self.pos).toTuple(), self.World.center_object.centerOnPos(self.debug_target_pos).toTuple())
    
    def aimPlayer(self, deltaTime: float):
        target_pos: Vector = self.World.center_object.pos
        dist = Vector.distance(self.pos, target_pos)
        direction: Vector = target_pos - self.pos

        if dist < self.screen.get_height() * 0.75:
            timeToReach = dist / (self.gun.projectile_speed * 100)
            target_pos += self.World.center_object.velocity / self.World.center_object.mass * timeToReach * (1 + deltaTime)
            self.debug_target_pos = target_pos

            angle = self.direction.getAngle(target_pos - self.pos)
            self.angle_velocity = max(min(angle * 50, math.pi), -math.pi)
        
            if (timeToReach < 3 and abs(angle) < .025):
                self.gun.fire(self, focal=Vector.distance(self.pos, target_pos))

            if Vector.distance(self.pos, target_pos) > 256:
                self.propulse(deltaTime)
            elif Vector.distance(self.pos, target_pos) < 64:
                self.propulse(deltaTime, self.propulseForce(self.direction * -1), self.direction * -1)
        else:
            line = (self.World.centerPositionTo(target_pos).toTuple(), self.World.centerPositionTo(self.pos).toTuple())
            self.screen.get_rect().clipline(line)

            angle = direction.getAngle(Vector(0, 1))
            overlay = runner.SPRITE_LIB.subsurface((13*32, 0), (32, 32))
            overlay = pygame.transform.rotate(overlay, math.degrees(angle))
            overlay.fill((255, 150, 10), special_flags=pygame.BLEND_RGBA_MULT)
            rect = overlay.get_rect(center = self.World.centerPositionTo(target_pos - direction.normalized() * 64).toTuple())
            self.screen.blit(overlay, rect)
    def fleeCoords(self, coord: Vector, deltaTime: float):
        if Vector.sqrDistance(self.pos, coord) > 768 * 768:
            return

        angle = self.direction.getAngle(self.pos - coord)
        self.angle_velocity = max(min(angle * 50, math.pi), -math.pi)
    
        if (abs(angle) < .025):
            self.propulse(deltaTime)

    def updateMask(self):
        self.mask = pygame.mask.from_surface(
            pygame.transform.rotate(self.sprite, math.degrees(self.direction.getAngle(Vector(0, -1)))))
    def updatePhysics(self, deltaTime: float) -> bool:
        self.velocity /= 1 + deltaTime * 0.5

        Collider.updatePhysics(self, deltaTime)
        self.updateMask()

        self.gun.reload(deltaTime)
        if (self.propulseCooldown > 0):
            self.propulseCooldown -= deltaTime
        
        if not(self.World.global_effects.get("peace", None)):
            self.aimPlayer(deltaTime)
        else:
            self.fleeCoords(Vector.TupleToPos(self.World.global_effects["peace"]), deltaTime)

        if (self.mask == None):
            return True
        else:
            return self.mask.count() > 1024