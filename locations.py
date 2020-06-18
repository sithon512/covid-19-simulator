import pygame

from entity import Entity
from enums import LocationType

class Location(Entity):
	def __init__(self, x, y, width, height, texture, name, type):
		Entity.__init__(self, x, y, width, height, texture)

		self.name = name
		self.type = type

class House(Location):
	# Default values:

	# Dimensions
	default_width = 700 # px
	default_height = 500 # px

	def __init__(self, x, y, width, height, texture):
		Location.__init__(self, x, y, width, height, texture,
			"House", LocationType.HOUSE)

class GroceryStore(Location):
	# Default values:

	# Dimensions
	default_width = 2000 # px
	default_height = 1000 # px

	# Minimum spacing between aisles
	min_aisle_spacing = 300 # px

	# Number of shopping carts
	default_num_carts = 5

	def __init__(self, x, y, width, height, texture):
		Location.__init__(self, x, y, width, height, texture,
			"Grocery Store", LocationType.GROCERY_STORE)

class MapElement(Entity):
	pass

class Aisle(MapElement):
	def __init__(self, x, y, width, height, texture):
		Entity.__init__(self, x, y, width, height, texture)
