from Class.Vector import Vector
from Class.InGame.Collider import Collider
import Class.InGame.ObjectRunner as runner
from Class.InGame.Gun import Gun
from Class.InGame.Debris import Debris
from Functions.ImageModifier import loadSprite, randomPaletteFor

import pygame, math, random, json, os

SHIP_SQUARE_SIZE = 64

class Ship(Collider, runner.Object):
    # =============================================

    faction = "player"
    World: runner.World
    gun: Gun = None
    base_sprite: pygame.Surface = None
    sprite: pygame.Surface = None
    damage_Effects: pygame.Surface = None
    parts: dict

    # =============================================

    def __init__(self, screen : pygame.Surface, World: runner.World, pos : Vector, parts: dict) -> None:
        self.screen = screen
        self.parts = parts

        Collider.__init__(self, Vector(0, -1).normalize(), pos)
        self.mass = 2
        
        self.gun = Gun(World, parts["weapon"], colors=parts["weapon_colors"])
        self.gun.mouseAim = True

        self.resetSprite()

        self.damage_Effects = pygame.Surface((SHIP_SQUARE_SIZE, SHIP_SQUARE_SIZE), flags=pygame.SRCALPHA)
        self.damage_Effects.fill((0, 0, 0, 0))

        self.damageSprite(Vector(0, 0), 64)
        self.damageSprite(Vector(48, 48), 64)
        
        self.World = World
        self.World.AddObject(self)
    def randomize(self):
        self.parts["cockpit"] = random.choice(os.listdir("./Data/Cockpit/")).split('.')[0]
        self.parts["cockpit_colors"] = randomPaletteFor("./Data/Cockpit/" + self.parts["cockpit"] + ".json")

        self.parts["wings"] = random.choice(os.listdir("./Data/Wings/")).split('.')[0]
        self.parts["wings_colors"] = randomPaletteFor("./Data/Wings/" + self.parts["wings"] + ".json")
        
        self.parts["engine"] = random.choice(os.listdir("./Data/Engines/")).split('.')[0]
        self.parts["engine_colors"] = randomPaletteFor("./Data/Engines/" + self.parts["engine"] + ".json")
        
        self.gun.gunType = random.choice(os.listdir("./Data/Weapons/")).split('.')[0]
        self.gun.colors = randomPaletteFor("./Data/Weapons/" + self.gun.gunType + ".json")
        self.gun.getInfo()
        self.resetSprite()
        self.gun.fireCooldown = 0

    def propulse(self, deltaTime, force: float = 5, direction: Vector = None):
        if (self.timeSinceWallHit() >= 0.4):
            if (direction == None):
                direction = self.direction
            self.velocity += direction * force * (1 + self.mass) * deltaTime * 45

    def propulseForce(self, direction) -> float:
        f: float = 2 + 4 * abs(self.direction.dot(direction))
        if (self.direction.dot(direction) > -0.25):
            return f
        else:
            return f / 2
    def eventReactions(self, events: list[pygame.event.Event], deltaTime: float):
        self.gun.reload(deltaTime)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_5:
                    self.randomize()
                if event.key == pygame.K_KP_9:
                    self.explode()
            if event.type == pygame.MOUSEBUTTONDOWN:                                      #Use mouse button
                pass

        # Continuous key press
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_r]:
            self.repair(50, deltaTime)

        if pygame.mouse.get_pressed()[0]:
            self.propulse(deltaTime)
        if pygame.mouse.get_pressed()[2]:
            self.gun.fire(self, spread=0, focal=256 + Vector.distance(Vector.TupleToPos(pygame.mouse.get_pos()), self.World.centerPositionTo(self.pos)))
        if keys_pressed[pygame.K_z] or keys_pressed[pygame.K_UP]:
            self.propulse(deltaTime, force = self.propulseForce(Vector(0, -1)), direction = Vector(0, -1))
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            self.propulse(deltaTime, force = self.propulseForce(Vector(0, 1)), direction = Vector(0, 1))
        if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
            self.propulse(deltaTime, force = self.propulseForce(Vector(1, 0)), direction = Vector(1, 0))
        if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_q]:
            self.propulse(deltaTime, force = self.propulseForce(Vector(-1, 0)), direction = Vector(-1, 0))
    def onCollide(self, collider: Collider, point: Vector):
        t = self.lastWallHit

        if (type(collider) == Debris):
            return
        super().onCollide(collider, point)

        inSpritePoint: Vector = point - self.pos
        inSpritePoint = inSpritePoint.rotate(self.direction.getAngle(Vector(0, -1)))
        inSpritePoint += Vector(self.sprite.get_width(), self.sprite.get_height()) / 2

        if (type(collider).__name__ == "Projectile"):
            self.lastWallHit = t
            self.damageSprite(inSpritePoint, collider.explodeStrength)
            if (self.mask.count() <= 128):
                self.explode()
        else:
            collisionStrength = (collider.last_frame_velocity * collider.mass - self.last_frame_velocity * self.mass).magnitude() / 200
            self.damageSprite(inSpritePoint, collisionStrength)
            if (self.mask.count() <= 128):
                self.explode()
    
    def explode(self):
        for key in [("Wings/", "wings"), ("Engines/", "engine"), ("Cockpit/", "cockpit")]:
            img = loadSprite(
                json.load(open("./Data/" + key[0] + self.parts[key[1]] + ".json", 'r')),
                runner.SPRITE_LIB,
                gridSize = 32,
                colors = self.parts[key[1] + "_colors"]
            )
            xsplit = [0, random.randint(32 / 4, 32 / 2), random.randint(32 / 2, 32 * 3 / 4), 32]
            ysplit = [0, random.randint(32 / 4, 32 / 2), random.randint(32 / 2, 32 * 3 / 4), 32]
            
            for x in range(3):
                for y in range(3):
                    Debris(self.screen, self.World, self.pos, img.subsurface(
                        xsplit[x], ysplit[y],
                        xsplit[x + 1] - xsplit[x], ysplit[y + 1] - ysplit[y]
                    ))
    
    def repair(self, amount: float, deltaTime: float):
        cutout: pygame.Mask = pygame.mask.from_surface(self.sprite, 215)
        cutoutBase: pygame.Mask = pygame.mask.from_surface(self.sprite, 215)
        cutout.draw(cutoutBase, (0, -1))
        cutout.draw(cutoutBase, (-1, 0))
        cutout.draw(cutoutBase, (1, 0))
        cutout.draw(cutoutBase, (0, 1))

        noise = pygame.transform.scale(runner.SPRITE_LIB.subsurface((12*32, 32), (32, 32)), (SHIP_SQUARE_SIZE, SHIP_SQUARE_SIZE))
        noise = pygame.transform.rotate(noise, random.random() * 360)

        newEffect: pygame.Surface = cutout.to_surface(setcolor=(0, 200, 255, 255), unsetcolor=(0, 0, 0, 0))
        # newEffect.blit(noise, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        newEffect.blit(cutoutBase.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(255, 255, 255, 255)), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.damage_Effects.blit(newEffect, (0, 0))
        
        base = self.base_sprite.copy()
        base.blit(noise, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        base.blit(cutout.to_surface(setcolor=(255, 255, 255, min(255, 255 * deltaTime * amount)), unsetcolor=(0, 0, 0, 0)), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        

        self.sprite.blit(base, (0, 0))# = cutout.to_surface(unsetcolor=(0, 0, 0, 0))
        self.updateMask()

        cutout = pygame.mask.from_surface(self.sprite, 215).to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
        self.damage_Effects.blit(cutout, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

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
        strength /= 2
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
        # rect: pygame.Rect = rotatedImage.get_rect(center = self.pos.toTuple())
        rect: pygame.Rect = rotatedImage.get_rect(center = self.World.centerPositionTo(self.pos).toTuple())
        self.screen.blit(rotatedImage, rect)
        # self.screen.blit(self.mask.to_surface(), rect)
    def update(self, debug = False):
        self.blitImage(self.sprite)
        self.blitImage(self.damage_Effects)
        self.gun.update(self)
    
    def updateMask(self):
        rotatedImage: pygame.Surface = pygame.transform.rotate(self.sprite, math.degrees(self.direction.getAngle(Vector(0, -1))))
        self.mask = pygame.mask.from_surface(rotatedImage)
    def updatePhysics(self, deltaTime: float) -> bool:
        self.angle_velocity = max(min(self.angle_velocity, math.pi), -math.pi)
        self.velocity /= 1 + deltaTime * 0.75
        
        Collider.updatePhysics(self, deltaTime)
        self.updateMask()
        
        self.damage_Effects.fill((0, 0, 0, 255 * deltaTime), special_flags=pygame.BLEND_RGBA_SUB)
        
        mouse_pos = Vector.TupleToPos(pygame.mouse.get_pos())
        mouse_pos -= Vector.TupleToPos(self.screen.get_rect().size) / 2
        angle = self.direction.getAngle(mouse_pos)
        self.angle_velocity = angle * 5
        
        return True