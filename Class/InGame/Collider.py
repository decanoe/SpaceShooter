from __future__ import annotations
from Class.Vector import Vector
import pygame
import math

class Collider:
    # =============================================

    pos: Vector
    direction: Vector
    velocity: Vector
    mass: float = 1
    last_frame_velocity: Vector
    angle_velocity: float = 0
    lastWallHit: float = 0

    lastObjectHit = None

    mask: pygame.Mask = None

    # =============================================

    def __init__(self, direction: Vector, pos : Vector) -> None:
        self.pos = pos
        self.direction = direction.normalized()
        self.velocity = Vector(0, 0)
        self.last_frame_velocity = self.velocity

    def canCollide(self, collider: Collider) -> bool:
        if (self.mask == None):
            return False
        if (self.lastObjectHit != None and self.lastWallHit < .25):
            return collider != self.lastObjectHit
        return True
    def onCollide(self, collider: Collider, point: Vector, normal: Vector):
        self.lastWallHit = 0

        if collider == None: return
        self.lastObjectHit = collider
        
        self.velocity -= normal * (
            2 * collider.mass * (self.velocity - collider.last_frame_velocity).dot(normal)
            / ((self.mass + collider.mass))
            )
        # self.velocity *= 0.8

        self.pos += normal * .1

    def computeRotation(self, deltaTime: float):
        self.direction = self.direction.rotate(self.angle_velocity * deltaTime)

        self.angle_velocity *= 1 - deltaTime * 2
    
    def updatePhysics(self, deltaTime: float) -> bool:
        self.computeRotation(deltaTime)
        
        if (self.lastWallHit < 32):
            self.lastWallHit += deltaTime
        else:
            self.lastObjectHit = None
        
        self.pos += self.velocity * deltaTime / self.mass

        self.last_frame_velocity = self.velocity

    
    def timeSinceWallHit(self) -> float:
        return self.lastWallHit
    def setVelocity(self, velocity: Vector) -> None:
        self.velocity = velocity
    def getVelocity(self) -> Vector:
        return self.velocity