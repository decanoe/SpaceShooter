from __future__ import annotations
import math

class Vector:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    def __add__(self, v2: Vector) -> Vector:
        '''add to vectors and return the result'''
        v3 = Vector(self.x + v2.x, self.y + v2.y)
        return v3
    def __sub__(self, v2: Vector) -> Vector:
        '''substract to vectors and return the result'''
        v3 = Vector(self.x - v2.x, self.y - v2.y)
        return v3
    def __mul__(self, float_: float) -> Vector:
        '''multiply a vector by a float and return the result'''
        v3 = Vector(self.x * float_, self.y * float_)
        return v3
    def mult(self, v2: Vector) -> Vector:
        '''multiply a vector by a vector and return the result'''
        v3 = Vector(self.x * v2.x, self.y * v2.y)
        return v3
    def __truediv__(self, float_: float) -> Vector:
        '''divide a vector by a float and return the result'''
        v3 = Vector(self.x / float_, self.y / float_)
        return v3
    def div(self, v2: Vector) -> Vector:
        '''divide a vector by a vector and return the result'''
        v3 = Vector(self.x / v2.x, self.y / v2.y)
        return v3
    def magnitude(self) -> float:
        '''return the magnitude (norme) of the vector'''
        return math.sqrt(self.x**2 + self.y**2)
    def sqrMagnitude(self) -> float:
        '''return the squared magnitude (norme) of the vector'''
        return self.x**2 + self.y**2
    def normalized(self) -> Vector:
        '''return the same vector with a magnitude of one (do not change the original vector)'''
        magn = self.magnitude()
        if (magn == 0): return self
        return Vector(self.x / magn, self.y / magn)
    def normalize(self) -> Vector:
        '''transform the vector to a vector with a magnitude of one'''
        magn = self.magnitude()
        if (magn == 0): return self
        self.x /= magn
        self.y /= magn
        return self
    def dot(self, v2: Vector) -> float:
        '''return the scalar product of two vector'''
        return self.x*v2.x + self.y*v2.y
    def distance(v1: Vector, v2: Vector) -> float:
        '''Return the distance between v1 and v2 as positions'''
        v3 = v2 - v1 #the movement from v1 to v2
        return v3.magnitude()
    def sqrDistance(v1: Vector, v2: Vector) -> float:
        '''Return the squared distance between v1 and v2 as positions'''
        v3 = v2 - v1 #the movement from v1 to v2
        return v3.sqrMagnitude()
    def toParametric(self, p: Vector) -> tuple[float, float, float]:
        '''Return parametric representation of the line of the vector passing through the point p'''
        a = -self.y/self.x
        b = 1
        c = -(p + self*(p.x/self.x)).y
        return (a, b, c)
    def distanceToLine(v1, p1: Vector, p2: Vector) -> float:
        '''return the distance between a point p2 and a line of vector v1 passing through p1'''
        a, b, c = v1.toParametric(p1)
        d = abs(a*p2.x + b*p2.y + c)
        d /= math.sqrt(a**2 + b**2)
        return d
    def normal(self) -> Vector:
        '''return a vector perpendicular to the vector'''
        return Vector(-self.y, self.x)
    def toTuple(self) -> tuple[float, float]:
        '''convert a vector into a tuple'''
        return(self.x, self.y)
    def AngleToVector(angle: float) -> Vector:
        '''return a vector matching an angle (in radiant)
        0 rad ==> right'''
        v = Vector(math.cos(angle), -math.sin(angle))
        return v
    def TupleToPos(tuple_: tuple[float, float]) -> Vector:
        return Vector(tuple_[0], tuple_[1])
    
    def round(self) -> Vector:
        '''return a vector with independently round x and y'''
        return Vector(round(self.x), round(self.y))
    def flat(self) -> Vector:
        '''return a vector which goes in the closest cardinal direction'''
        if (self.x == 0 == self.y):
            return Vector(1, 0)
        
        if (abs(self.x) == abs(self.y)):
            return Vector(self.x / abs(self.x), self.y / abs(self.y)).normalize()

        if (abs(self.x) > abs(self.y)):
            return Vector(self.x / abs(self.x), 0)
        return Vector(0, self.y / abs(self.y))
    
    def reflect(self, normal: Vector) -> Vector:
        '''return the reflection of the vector on a surface of normal given'''
        normal.normalize()
        return self - normal * 2 * self.dot(normal)
    def rotate(self, angle: float) -> Vector:
        '''rotate the vector by an angle'''
        return Vector(
            self.x * math.cos(angle) - self.y * math.sin(angle),
            self.x * math.sin(angle) + self.y * math.cos(angle)
        )
    def getAngle(self, v2: Vector) -> float:
        '''return the angle between 2 vectors'''
        return math.atan2(v2.y*self.x - v2.x*self.y, v2.x*self.x + v2.y*self.y)
    
    def mod(self, value: int) -> Vector:
        '''return the vector with components modulo <value>'''
        return Vector(self.x % value, self.y % value)