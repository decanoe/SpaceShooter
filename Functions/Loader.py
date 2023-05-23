from Class.InGame.Ship import Ship
from Class.Utilities.Vector import Vector
import json

def loadPlayerShip(slot: int, screen, world):
    with open('./Saves/slot' + str(slot) + '.json', 'r') as f:
        data: dict = json.load(f)["ship"]

        ship: Ship = Ship(screen, world, Vector.TupleToPos(data.get("attributes", {"position": (0, 0)})["position"]), data["parts"])
        return ship

def savePlayerShip(slot: int, ship: Ship):
    data: dict = json.load(open('./Saves/slot' + str(slot) + '.json', 'r'))

    data["ship"]["attributes"]["position"] = ship.pos.toTuple()
    for key, values in ship.parts.items():
        data["ship"]["parts"][key] = values
    data["ship"]["parts"]["weapon"] = ship.gun.gunType
    data["ship"]["parts"]["weapon_colors"] = ship.gun.colors
    
    json.dump(data, open('./Saves/slot' + str(slot) + '.json', 'w'), indent=4)