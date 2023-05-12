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

    mask: pygame.Mask = None

    # =============================================

    def __init__(self, direction: Vector, pos : Vector) -> None:
        self.pos = pos
        self.direction = direction.normalized()
        self.velocity = Vector(0, 0)
        self.last_frame_velocity = self.velocity

    def getNormal(self, point: Vector, collider: Collider) -> Vector:
        return (point - self.pos).normalized()
    
    def canCollide(self, collider: Collider) -> bool:
        return self.mask != None
    def onCollide(self, collider: Collider, point: Vector):
        self.lastWallHit = 0

        if collider == None: return

        normal: Vector = collider.getNormal(point, self)
        
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
        
        self.pos += self.velocity * deltaTime * 100 / (1 + self.mass)

        self.last_frame_velocity = self.velocity

    
    def timeSinceWallHit(self) -> float:
        return self.lastWallHit
    def setVelocity(self, velocity: Vector) -> None:
        self.velocity = velocity
    def getVelocity(self) -> Vector:
        return self.velocity