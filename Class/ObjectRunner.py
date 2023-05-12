from Class.Collider import Collider
from Class.Vector import Vector
import pygame

SPRITE_LIB = pygame.image.load("./Sprites/Ship - parts.png")

class Object:
    pos: Vector
    screen: pygame.Surface

    def centerOnPos(self, point: Vector):
        return point - self.pos + Vector.TupleToPos(self.screen.get_rect().size) / 2
    def dieFromRange(self):
        pass

    def update(self):
        pass
    def updatePhysics(self) -> bool:
        return False

def UpdateColliding(game_objects: list[Object|Collider]):
    for i in range(len(game_objects)):
        c1 = game_objects[i]
        if not(issubclass(type(c1), Collider)): continue

        for c2 in game_objects[i + 1:]:
            if not(issubclass(type(c1), Collider)): continue
            
            if (c1.canCollide(c2) and c2.canCollide(c1)):
                rect1 = c1.mask.get_rect(center = c1.pos.toTuple())
                rect2 = c2.mask.get_rect(center = c2.pos.toTuple())
                p = c1.mask.overlap(c2.mask, (rect2.left - rect1.left, rect2.top - rect1.top))
                if p == None: continue

                point: Vector = Vector.TupleToPos(p)
                point -= Vector.TupleToPos(c1.mask.get_rect()[2:]) / 2
                point += c1.pos

                c1.onCollide(c2, point)
                c2.onCollide(c1, point)

def UpdateAllPhysics(game_objects: list[Object], deltaTime: float):
    UpdateColliding(game_objects)
    i = 0
    while i < len(game_objects):
        if not(game_objects[i].updatePhysics(deltaTime)):
            game_objects.pop(i)
        elif Vector.sqrDistance(game_objects[i].pos, game_objects[0].pos) > 1536*1536:
            game_objects[i].dieFromRange()
            game_objects.pop(i)
        else:
            i += 1
def UpdateAllGraphics(game_objects: list):
    for o in game_objects:
        o.update()