from Class.Vector import Vector
from Class.Collider import Collider
import Class.ObjectRunner as runner
from Class.Gun import Gun, COOLDOWNS
from Class.Debris import Debris
import pygame
import math
import random

SHIP_SQUARE_SIZE = 64

class Ship(Collider, runner.Object):
    # =============================================

    GAME_OBJECTS: list[runner.Object] = None
    gun: Gun = None
    parts: dict[str, tuple[int, int]] = {"ship" : (0, 0),
                   "wings" : (3*32, 64),
                   "engine" : (0, 128)}
    sprite: pygame.Surface = None
    damage_Effects: pygame.Surface = None

    # =============================================

    def __init__(self, screen : pygame.Surface, game_objects: list[runner.Object], pos : Vector) -> None:
        self.GAME_OBJECTS = game_objects
        self.GAME_OBJECTS.append(self)
        
        self.screen = screen

        Collider.__init__(self, Vector(0, -1).normalize(), pos)
        self.mass = 2
        
        self.gun = Gun(game_objects)
        self.gun.gunType = "small cannon"
        self.gun.mouseAim = True
        self.resetSprite()

        self.damage_Effects = pygame.Surface((SHIP_SQUARE_SIZE, SHIP_SQUARE_SIZE), flags=pygame.SRCALPHA)
        self.damage_Effects.fill((0, 0, 0, 0))

        # self.damageSprite(Vector(0, 0), 32)
        # self.damageSprite(Vector(48, 48), 32)

    def propulse(self, deltaTime, force: float = 5, direction: Vector = None):
        if (self.timeSinceWallHit() >= 0.4):
            if (direction == None):
                direction = self.direction
            self.velocity += direction * force * (1 + self.mass) * deltaTime * 35

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
                    self.parts["ship"] = (random.randint(0, 17) * 32, random.randint(0, 1) * 32)
                    self.parts["wings"] = (random.randint(0, 17) * 32, random.randint(2, 3) * 32)
                    self.parts["engine"] = (random.randint(0, 10) * 32, random.randint(4, 5) * 32)
                    self.gun.gunType = random.choice(list(COOLDOWNS.keys()))
                    self.resetSprite()
                    if self.gun.gunType.endswith(" (ennemy)"):
                        self.gun.gunType = self.gun.gunType[:-9]
                    self.gun.fireCooldown = 0
                if event.key == pygame.K_KP_9:
                    self.explode()
            if event.type == pygame.MOUSEBUTTONDOWN:                                      #Use mouse button
                pass
            
        # Continuous key press
        keys_pressed = pygame.key.get_pressed()

        if keys_pressed[pygame.K_r]:
            self.repair(5, deltaTime)

        if pygame.mouse.get_pressed()[0]:
            self.propulse(deltaTime)
        if pygame.mouse.get_pressed()[2]:
            self.gun.fire(self, spread=0)
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

        if (type(collider) != Debris):
            super().onCollide(collider, point)

        if (type(collider).__name__ == "Projectile"):
            self.lastWallHit = t
            inSpritePoint: Vector = point - self.pos
            inSpritePoint = inSpritePoint.rotate(self.direction.getAngle(Vector(0, -1)))
            inSpritePoint += Vector(self.sprite.get_width(), self.sprite.get_height()) / 2

            # self.screen.blit(self.sprite, (800, 500))
            # pygame.draw.circle(self.screen, (255, 0, 0), (inSpritePoint + Vector(800, 500)).toTuple(), 2)

            self.damageSprite(inSpritePoint, collider.explodeStrength)
    def getHitbox(self) -> pygame.Rect:
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
    
    def repair(self, amount: float, deltaTime: float):
        cutout: pygame.Mask = pygame.mask.from_surface(self.sprite, 215)
        cutoutBase: pygame.Mask = pygame.mask.from_surface(self.sprite, 215)
        cutout.draw(cutoutBase, (0, -1))
        cutout.draw(cutoutBase, (-1, 0))
        cutout.draw(cutoutBase, (1, 0))
        cutout.draw(cutoutBase, (0, 1))

        newEffect: pygame.Surface = cutout.to_surface(setcolor=(0, 255, 150, 255), unsetcolor=(0, 0, 0, 0))
        newEffect.blit(cutoutBase.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=(255, 255, 255, 255)), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        self.damage_Effects.blit(newEffect, (0, 0))

        base = runner.SPRITE_LIB.subsurface(self.parts["wings"], (32, 32)).copy()
        base.blit(runner.SPRITE_LIB.subsurface(self.parts["engine"], (32, 32)), (0, 0))
        base.blit(runner.SPRITE_LIB.subsurface(self.parts["ship"], (32, 32)), (0, 0))
        base = pygame.transform.scale(base, (SHIP_SQUARE_SIZE, SHIP_SQUARE_SIZE))
        
        base.blit(cutout.to_surface(setcolor=(255, 255, 255, 255 * deltaTime * amount), unsetcolor=(0, 0, 0, 0)), (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        self.sprite.blit(base, (0, 0))# = cutout.to_surface(unsetcolor=(0, 0, 0, 0))
        self.updateMask()

        cutout = pygame.mask.from_surface(self.sprite, 215).to_surface(setcolor=(255, 255, 255, 255), unsetcolor=(0, 0, 0, 0))
        self.damage_Effects.blit(cutout, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

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
        # rect: pygame.Rect = rotatedImage.get_rect(center = self.pos.toTuple())
        rect: pygame.Rect = rotatedImage.get_rect(center = self.GAME_OBJECTS[0].centerOnPos(self.pos).toTuple())
        self.screen.blit(rotatedImage, rect)
        # self.screen.blit(self.mask.to_surface(), rect)
    def update(self):
        self.blitImage(self.sprite)
        self.blitImage(self.damage_Effects)
        self.gun.update(self)
    def debug_update(self):
        pygame.draw.rect(self.screen, (0, 255, 0), self.getHitbox(), width=2)
        self.debugDirection()
    def updateMask(self):
        rotatedImage: pygame.Surface = pygame.transform.rotate(self.sprite, math.degrees(self.direction.getAngle(Vector(0, -1))))
        self.mask = pygame.mask.from_surface(rotatedImage)
    def updatePhysics(self, deltaTime: float) -> bool:
        self.angle_velocity = max(min(self.angle_velocity, math.pi), -math.pi)
        self.velocity /= 1 + deltaTime * 0.5
        
        Collider.updatePhysics(self, deltaTime)
        self.updateMask()
        
        self.damage_Effects.fill((0, 0, 0, 255 * deltaTime), special_flags=pygame.BLEND_RGBA_SUB)
        
        mouse_pos = Vector.TupleToPos(pygame.mouse.get_pos())
        mouse_pos -= Vector.TupleToPos(self.screen.get_rect().size) / 2
        angle = self.direction.getAngle(mouse_pos)
        self.angle_velocity = angle * 500
        
        return True