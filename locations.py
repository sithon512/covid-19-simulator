import pygame

from entity import Entity
from enums import LocationType

class Location(Entity):
    def __init__(self, x, y, width, height, texture, name, type):
        Entity.__init__(self, x, y, width, height, texture)

        self.name = name
        self.type = type

class House(Location):
    def __init__(self, x, y, width, height, texture):
        Location.__init__(self, x, y, width, height, texture,
            "House", LocationType.HOUSE)

class GroceryStore(Location):
    def __init__(self, x, y, width, height, texture):
        Location.__init__(self, x, y, width, height, texture,
            "Grocery Store", LocationType.GROCERY_STORE)