from Class.InGame.Ship import Ship
from Class.Vector import Vector
import json

def loadPlayerShip(slot: int, screen, world):
    with open('./Saves/slot' + str(slot) + '.json', 'r') as f:
        data: dict = json.load(f)["ship"]

        ship: Ship = Ship(screen, world, Vector.TupleToPos(data.get("attributes", {"position": (0, 0)})["position"]), data["parts"])
        return ship