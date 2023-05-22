from Class.InGame.Collider import Collider
from Class.Vector import Vector
import pygame, math

SPRITE_LIB = pygame.image.load("./Sprites/Ship - parts.png")
DEBRIS_LIFE: int = 25
REGION_SIZE: int = 256
LOAD_RADIUS: int = 6

class Object:
    clearLagData: bool = False
    pos: Vector
    screen: pygame.Surface

    def centerOnPos(self, point: Vector):
        return point - self.pos + Vector.TupleToPos(self.screen.get_rect().size) / 2
    def dieFromRange(self) -> bool:
        return True

    def update(self, debug = False):
        pass
    def updatePhysics(self) -> bool:
        return False

class World:
    center_object: Object = None
    game_objects: dict[tuple[int, int], list[Object]] = {}

    def __init__(self):
        pass
    
    def centerPositionTo(self, point: Vector):
        if (self.center_object == None):
            return point
        return point - self.center_object.pos + Vector.TupleToPos(self.center_object.screen.get_rect().size) / 2

    def getRegion(self, pos: Vector) -> tuple[int, int]:
        return (pos / REGION_SIZE).round().toTuple()
    def AddObject(self, obj: Object):
        if (self.center_object == None):
            self.center_object = obj
            return

        self.game_objects.setdefault(self.getRegion(obj.pos), []).append(obj)
    def RemoveObject(self, obj: Object) -> bool:
        region = self.getRegion(obj.pos)
        if not(obj in self.game_objects[region]):
            return False
        
        self.game_objects[region].remove(obj)

        if self.game_objects[region] == []:
            self.game_objects.pop(region)
        return True
    
    def changeCenterObject(self, center_object: Object):
        self.AddObject(self.center_object)
        self.center_object = center_object

    def get_normal(mask1: pygame.Mask, mask2: pygame.Mask, offset: tuple[int, int]) -> Vector:
        """
        Calculate the normal and tangent vector between our object and other.
        In general this gives the most realistic collissions, but depending on
        the shapes of the colliding objects, it can also return problematic
        results.
        """
        dx = (mask1.overlap_area(mask2, (offset[0] + 1, offset[1]))
            -mask1.overlap_area(mask2, (offset[0] - 1, offset[1])))
        dy = (mask1.overlap_area(mask2, (offset[0], offset[1] + 1))
            -mask1.overlap_area(mask2, (offset[0], offset[1] - 1)))
        return Vector(dx, dy).normalize()
    def UpdateCollision(self, c1: Object | Collider, c2: Object | Collider):
        if not(issubclass(type(c1), Collider)): return
                        
        if (c1.canCollide(c2) and c2.canCollide(c1)):
            rect1 = c1.mask.get_rect(center = c1.pos.toTuple())
            rect2 = c2.mask.get_rect(center = c2.pos.toTuple())
            p = c1.mask.overlap(c2.mask, (rect2.left - rect1.left, rect2.top - rect1.top))
            if p == None: return

            point: Vector = Vector.TupleToPos(p)
            point -= Vector.TupleToPos(c1.mask.get_rect()[2:]) / 2
            point += c1.pos

            normal = World.get_normal(c1.mask, c2.mask, (rect2.left - rect1.left, rect2.top - rect1.top))

            c1.onCollide(c2, point, normal)
            c2.onCollide(c1, point, normal)
    def UpdateAllCollisionArround(self, c1: Collider, region1: tuple[int, int]):
        for region2 in [(region1[0] + x, region1[1] + y) for x in range(-1, 1) for y in range(-1, 2)]:
            if not(region2 in self.game_objects) or (region1[0] == region2[0] and region1[1] <= region2[1]):
                continue

            for c2 in self.game_objects[region2]:
                self.UpdateCollision(c1, c2)
    def UpdateAllCollision(self):
        centerRegion = self.getRegion(self.center_object.pos)
        for region1 in [(centerRegion[0] + x, centerRegion[1] + y) for x in range(-LOAD_RADIUS, LOAD_RADIUS+1) for y in range(-LOAD_RADIUS, LOAD_RADIUS+1)]:
            if not(region1 in self.game_objects):
                continue
                
            collideCenter: bool = abs(centerRegion[0] - region1[0]) <= LOAD_RADIUS and abs(centerRegion[1] - region1[1]) <= LOAD_RADIUS

            for i in range(len(self.game_objects[region1])):
                c1 = self.game_objects[region1][i]
                if not(issubclass(type(c1), Collider)): continue

                # Update collision with center object
                if collideCenter:
                    self.UpdateCollision(c1, self.center_object)

                # Update collision in same region
                for c2 in self.game_objects[region1][i + 1:]:
                    self.UpdateCollision(c1, c2)

                # Update collision in close region
                self.UpdateAllCollisionArround(c1, region1)
    
    def UpdateAllPhysics(self, deltaTime: float, clearLagNeeded: float = 0):
        self.UpdateAllCollision()

        self.center_object.updatePhysics(deltaTime)

        centerRegion = self.getRegion(self.center_object.pos)
        for region in [(centerRegion[0] + x, centerRegion[1] + y) for x in range(-LOAD_RADIUS, LOAD_RADIUS+1) for y in range(-LOAD_RADIUS, LOAD_RADIUS+1)]:

            if not(region in self.game_objects):
                continue

            i = 0
            while i < len(self.game_objects[region]):
                obj = self.game_objects[region][i]

                if obj.clearLagData and clearLagNeeded:
                    obj.alive *= (1 - clearLagNeeded * deltaTime)
                
                if not(obj.updatePhysics(deltaTime)):
                    self.game_objects[region].pop(i)
                    del(obj)
                else:
                    newRegion = self.getRegion(obj.pos)
                    if (region != newRegion):
                        self.game_objects[region].pop(i)

                        if abs(centerRegion[0] - newRegion[0]) <= LOAD_RADIUS and abs(centerRegion[1] - newRegion[1]) <= LOAD_RADIUS:
                            self.AddObject(obj)
                        elif not(obj.dieFromRange()):
                            self.AddObject(obj)
                        else:
                            del(obj)
                    else:
                        i += 1
        
        self.CollectGarbage()
    def UpdateAllGraphics(self, debug = False):
        centerRegion = self.getRegion(self.center_object.pos)

        # for region in [(centerRegion[0] + x, centerRegion[1] + y) for x in range(-1, 2) for y in range(-1, 2)]:
        for region in [(centerRegion[0] + x, centerRegion[1] + y) for x in range(-LOAD_RADIUS, LOAD_RADIUS + 1) for y in range(-LOAD_RADIUS, LOAD_RADIUS + 1)]:
            if not(region in self.game_objects):
                continue

            for o in self.game_objects[region].__reversed__():
                o.update(debug = debug)
        
        self.center_object.update(debug = debug)

    def CollectGarbage(self):
        centerRegion = self.getRegion(self.center_object.pos)

        arroundRegions = [(centerRegion[0] + x, centerRegion[1] + y) for x in range(-LOAD_RADIUS-1, LOAD_RADIUS+2) for y in [-LOAD_RADIUS-1, LOAD_RADIUS+1]]
        arroundRegions += [(centerRegion[0] + x, centerRegion[1] + y) for y in range(-LOAD_RADIUS, LOAD_RADIUS+1) for x in [-LOAD_RADIUS-1, LOAD_RADIUS+1]]
        
        for region in arroundRegions:

            if not(region in self.game_objects):
                continue

            i = 0
            while i < len(self.game_objects[region]):
                obj = self.game_objects[region][i]

                if obj.dieFromRange():
                    self.game_objects[region].pop(i)
                    del(obj)
                else:
                    i += 1