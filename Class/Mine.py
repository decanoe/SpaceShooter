from Class.Vector import Vector
from Class.Collider import Collider
import Class.ObjectRunner as runner
import pygame
import math

MINE_RADIUS: float = 10

class Mine(Collider, runner.Object):
    # =============================================

    alive: bool = True
    GAME_OBJECTS: list[runner.Object] = None

    # =============================================

    def __init__(self, screen : pygame.Surface, game_objects: list[runner.Object], pos : Vector) -> None:
        self.GAME_OBJECTS = game_objects
        self.GAME_OBJECTS.append(self)
        Collider.__init__(self, screen, Vector(0, -1).normalize(), pos)
        self.radius = MINE_RADIUS
        self.mass = 2.5


    def onCollide(self, collider: Collider, point: Vector):
        super().onCollide(collider, point)

    def getHitbox(self) -> pygame.Rect :
        rect = pygame.Rect(
            self.pos.x - MINE_RADIUS,
            self.pos.y - MINE_RADIUS,
            MINE_RADIUS + MINE_RADIUS,
            MINE_RADIUS + MINE_RADIUS)
        return rect

    def update(self):
        pygame.draw.circle(self.screen, (150, 150, 150), self.pos.toTuple(), self.radius)
    def updatePhysics(self, deltaTime: float) -> bool:
        super().updatePhysics(deltaTime)

        return self.alive