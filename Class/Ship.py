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

    mouseFollow: bool = True
    GAME_OBJECTS: list[runner.Object] = None
    gun: Gun = None
    parts: dict[str, tuple[int, int]] = {"ship" : (0, 0),
                   "wings" : (3*32, 64),
                   "engine" : (0, 128)}
    sprite: pygame.Surface = None

    # =============================================

    def __init__(self, screen : pygame.Surface, game_objects: list[runner.Object], pos : Vector) -> None:
        self.GAME_OBJECTS = game_objects
        self.GAME_OBJECTS.append(self)
        
        self.screen = screen

        Collider.__init__(self, Vector(0, -1).normalize(), pos)
        self.mass = 2
        
        self.gun = Gun(game_objects)
        self.gun.gunType = "small cannon"
        self.resetSprite()

    def propulse(self):
        if (self.timeSinceWallHit() >= 0.5):
            self.velocity = self.direction * 2 * (1 + self.mass)

    def eventReactions(self, events: list[pygame.event.Event], deltaTime: float):
        self.gun.reload(deltaTime)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LCTRL:
                    self.mouseFollow = not(self.mouseFollow)
                    self.gun.mouseAim = self.mouseFollow
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
        
        if self.mouseFollow:
            if pygame.mouse.get_pressed()[0]:
                self.propulse()
            if pygame.mouse.get_pressed()[2]:
                self.gun.fire(self)
        else:
            if keys_pressed[pygame.K_SPACE]:
                self.gun.fire(self)
            if keys_pressed[pygame.K_z] or keys_pressed[pygame.K_UP]:
                self.propulse()
            if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
                self.angle_velocity += math.pi * deltaTime * 10
            if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_q]:
                self.angle_velocity -= math.pi * deltaTime * 10
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
        self.gun.update(self)
    def debug_update(self):
        pygame.draw.rect(self.screen, (0, 255, 0), self.getHitbox(), width=2)
        self.debugDirection()
    def updateMask(self):
        rotatedImage: pygame.Surface = pygame.transform.rotate(self.sprite, math.degrees(self.direction.getAngle(Vector(0, -1))))
        self.mask = pygame.mask.from_surface(rotatedImage)
    def updatePhysics(self, deltaTime: float) -> bool:
        self.angle_velocity = max(min(self.angle_velocity, math.pi), -math.pi)
        
        Collider.updatePhysics(self, deltaTime)
        self.updateMask()
        
        if (self.mouseFollow):
            mouse_pos = Vector.TupleToPos(pygame.mouse.get_pos())
            mouse_pos -= Vector.TupleToPos(self.screen.get_rect().size) / 2
            angle = self.direction.getAngle(mouse_pos)
            self.angle_velocity = angle * 500
        
        return True