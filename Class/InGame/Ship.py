from Class.Utilities.Vector import Vector
from Class.Utilities.Collider import Collider
import Class.Utilities.ObjectRunner as runner
from Class.InGame.Gun import Gun
from Class.InGame.Debris import Debris
from Functions.ImageModifier import loadSprite, randomPaletteFor

import pygame, math, random, json, os

SHIP_SQUARE_SIZE = 64
COLLISION_DISABLE_TIME = .75

class Ship(Collider, runner.Object):
    # =============================================

    faction = "player"
    World: runner.World
    gun: Gun = None
    base_sprite: pygame.Surface = None
    sprite: pygame.Surface = None
    damage_Effects: pygame.Surface = None
    parts: dict

    thrust_direction: Vector = Vector(0, 0)
    exploded: bool = False

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
        self.exploded = False

    def propulse(self, deltaTime):
        if (self.timeSinceWallHit() >= COLLISION_DISABLE_TIME):
            direction = self.thrust_direction.changeBase(self.direction).clamp()
            counter = self.velocity.changeBase(self.direction) / 1024 * -1
            if abs(counter.x) > abs(direction.x):
                direction.x = counter.x * 1024
            if abs(counter.y) > abs(direction.y):
                direction.y = counter.y * 1024
            direction = direction.clamp()

            self.velocity += self.direction * max(0, direction.y) * self.mass * deltaTime * 512
            self.velocity += self.direction * min(0, direction.y) * self.mass * deltaTime * 256
            self.velocity += self.direction.normal() * direction.x * self.mass * deltaTime * 384
            
            # pygame.draw.line(self.screen, (255, 150, 150), self.World.centerPositionTo(self.pos).toTuple(), self.World.centerPositionTo(self.pos + self.direction.normal() * direction.x * -64).toTuple())
            # pygame.draw.line(self.screen, (255, 150, 150), self.World.centerPositionTo(self.pos).toTuple(), self.World.centerPositionTo(self.pos + self.direction * direction.y * -64).toTuple())
            # pygame.draw.line(self.screen, (0, 255, 0), self.World.centerPositionTo(self.pos).toTuple(), self.World.centerPositionTo(self.pos + self.direction * counter.y * -64).toTuple())

    def eventReactions(self, events: list[pygame.event.Event], deltaTime: float):
        self.gun.reload(deltaTime)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_5:
                    if pygame.mask.from_surface(self.sprite).count() == pygame.mask.from_surface(self.base_sprite).count():
                        self.randomize()
                if event.key == pygame.K_KP_9:
                    self.explode()
            if event.type == pygame.MOUSEBUTTONDOWN:                                      #Use mouse button
                pass

        # Continuous key press
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_r]:
            self.repair(10, deltaTime)
        if pygame.mouse.get_pressed()[2]:
            self.gun.fire(self, spread=0, focal=256 + Vector.distance(Vector.TupleToPos(pygame.mouse.get_pos()), self.World.centerPositionTo(self.pos)))

        self.thrust_direction *= 0
        if pygame.mouse.get_pressed()[0]:
            self.thrust_direction += self.direction
        if keys_pressed[pygame.K_z] or keys_pressed[pygame.K_UP]:
            self.thrust_direction.y -= 1
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            self.thrust_direction.y += 1
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            self.thrust_direction.x += 1
        if keys_pressed[pygame.K_q] or keys_pressed[pygame.K_LEFT]:
            self.thrust_direction.x -= 1
    def onCollide(self, collider: Collider, point: Vector, normal: Vector):
        t = self.lastWallHit

        if (type(collider) == Debris):
            return

        inSpritePoint: Vector = point - self.pos
        inSpritePoint = inSpritePoint.rotate(self.direction.getAngle(Vector(0, -1)))
        inSpritePoint += Vector(self.sprite.get_width(), self.sprite.get_height()) / 2

        if (type(collider).__name__ == "Projectile"):
            self.lastWallHit = t
            self.damageSprite(inSpritePoint, collider.explodeStrength)
            if (not(self.exploded) and self.mask.count() <= 512):
                self.explode()
                self.exploded = True
        else:
            super().onCollide(collider, point, normal)
            collisionStrength = (collider.last_frame_velocity * collider.mass - self.last_frame_velocity * self.mass).magnitude() / 200
            self.damageSprite(inSpritePoint, collisionStrength)
            if (not(self.exploded) and self.mask.count() <= 512):
                self.explode()
                self.exploded = True
    
    def explode(self):
        for key in [("Wings/", "wings"), ("Engines/", "engine"), ("Cockpit/", "cockpit")]:
            img = loadSprite(
                json.load(open("./Data/" + key[0] + self.parts[key[1]] + ".json", 'r')),
                runner.SPRITE_LIB,
                gridSize = 32,
                colors = self.parts[key[1] + "_colors"]
            )
            img = pygame.transform.scale(img, (SHIP_SQUARE_SIZE, SHIP_SQUARE_SIZE))
            xsplit = [0, random.randint(SHIP_SQUARE_SIZE // 4, SHIP_SQUARE_SIZE * 3 // 4), SHIP_SQUARE_SIZE]
            ysplit = [0, random.randint(SHIP_SQUARE_SIZE // 4, SHIP_SQUARE_SIZE * 3 // 4), SHIP_SQUARE_SIZE]
            
            for x in range(2):
                for y in range(2):
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
        edgeSprite = pygame.transform.rotozoom(edgeSprite, random.random() * 360 * 0, float(strength) / 8)
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
        pygame.draw.line(self.screen, (0, 255, 50), self.World.centerPositionTo(Vector(0, 0)).toTuple(), self.World.centerPositionTo(self.pos).toTuple())
        self.blitImage(self.sprite)
        self.blitImage(self.damage_Effects)
        self.gun.update(self)
    
    def updateMask(self):
        rotatedImage: pygame.Surface = pygame.transform.rotate(self.sprite, math.degrees(self.direction.getAngle(Vector(0, -1))))
        self.mask = pygame.mask.from_surface(rotatedImage)
    def updatePhysics(self, deltaTime: float) -> bool:
        self.propulse(deltaTime)
        Collider.updatePhysics(self, deltaTime)
        self.updateMask()
        
        self.damage_Effects.fill((0, 0, 0, 255 * deltaTime), special_flags=pygame.BLEND_RGBA_SUB)
        
        if (self.timeSinceWallHit() >= COLLISION_DISABLE_TIME):
            mouse_pos = Vector.TupleToPos(pygame.mouse.get_pos())
            mouse_pos -= Vector.TupleToPos(self.screen.get_rect().size) / 2
            angle = self.direction.getAngle(mouse_pos)
            self.angle_velocity = angle
            if self.angle_velocity > deltaTime:
                self.angle_velocity = 7.5
            elif self.angle_velocity < -deltaTime:
                self.angle_velocity = -7.5

        if self.World.global_effects.get("repair", None):
            area = self.World.global_effects["repair"][1]
            if Vector.sqrDistance(self.pos, Vector.TupleToPos(self.World.global_effects["repair"][0])) < area * area:
                self.repair(self.World.global_effects["repair"][2], deltaTime)
        
        return True