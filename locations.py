import sdl2

from entity import Entity
from enums import LocationType, MapElementType

class Location(Entity):
	def __init__(self, x, y, width, height, texture, facade_texture, name, type):
		Entity.__init__(self, x, y, width, height, texture)

		self.name = name
		self.type = type

		# Covers the interior of the location when the player is not inside
		self.facade = Facade(x, y, width, height, facade_texture)

		# Position coordinates of the entrance
		self.entrance_x = 0
		self.entrance_y = 0

		# Last time a NPC was generated for this location
		self.last_npc_generated = 0

		# Time before next NPC is generated for this location
		self.time_before_next_npc_generation = 0
	
	# Blocks player movement if the player is not inside
	def handle_collision(self, player):
		# Only check collision with bottom half of player if the player is
		# trying to access an item
		if not self.check_collision(player):
			return

		if not self.facade.visible:
			if (player.x > self.x and player.x_velocity < 0):
				player.block_movement()
			if (player.x < self.x and player.x_velocity > 0):
				player.block_movement()
			if (player.y > self.y and player.y_velocity < 0):
				player.block_movement()
			if (player.y < self.y and player.y_velocity > 0):
				player.block_movement()

	# Returns true if the entirety of the entity are inside the location
	def entity_inside(self, entity):
		if not entity.x > self.x:
			return False
		if not entity.y > self.y:
			return False
		if not entity.x + entity.width < self.x + self.width:
			return False
		if not entity.y + entity.height < self.y + self.height:
			return False

		return True

	# Toggles whether the interior of the location is visible
	def toggle_visibility(self, boolean):
		if boolean == True or boolean == False:
			self.facade.visible = boolean

	# Blocks player movement if trying to move out of the building
	def block_player_from_exiting(self, player):
		if (player.x > self.x and player.x_velocity > 0):
			player.block_movement()
		if (player.x < self.x and player.x_velocity < 0):
			player.block_movement()
		if (player.y > self.y and player.y_velocity > 0):
			player.block_movement()
		if (player.y < self.y and player.y_velocity < 0):
			player.block_movement()

	def is_visible(self):
		return self.facade.visible

class House(Location):
	# Default values:

	# Dimensions
	default_width = 700 # px
	default_height = 500 # px

	def __init__(self, x, y, width, height, texture, facade_texture):
		Location.__init__(self, x, y, width, height, texture,
			facade_texture, "House", LocationType.HOUSE)

class GroceryStore(Location):
	# Default values:

	# Dimensions
	default_width = 2400 # px
	default_height = 1500 # px

	# Minimum spacing between aisles
	min_aisle_spacing = 250 # px

	# Number of checkout stations
	default_num_registers = 3

	# Number of shopping carts
	default_num_carts = 2

	# Number of supplies to initialize stockroom with
	default_stockroom_size = 100 # supply items

	def __init__(self, x, y, width, height, texture, facade_texture):
		Location.__init__(self, x, y, width, height, texture,
			facade_texture, "Grocery Store", LocationType.GROCERY_STORE)

		# List of supply object thestore has in its stock room
		self.stockroom = []

class GasStation(Location):
	# Default values:

	# Dimensions
	default_width = 1000 # px
	default_height = 800 # px

	# Number of fuel dispensers for a default sized gas station
	default_num_dispensers = 4

	# Number of aisles for a default sized gas station
	default_num_aisles = 5

	# Minimum spacing between aisles
	min_aisle_spacing = 200 # px

	# Minimum spacing between dispensers
	min_dispenser_spacing = 300 # px

	def __init__(self, x, y, width, height, texture, facade_texture):
		Location.__init__(self, x, y, width, height, texture,
			facade_texture, "Gas Station", LocationType.GAS_STATION)

		# List of supply object thestore has in its stock room
		self.stockroom = []

class MapElement(Entity):
	# Default method
	# Block player movement if moving towards the element
	def handle_collision(self, player):
		# Only check collision with bottom half of player
		if not self.check_collision(player):
			return
			
		if (player.x > self.x and player.x_velocity < 0):
			player.block_movement()
		if (player.x < self.x and player.x_velocity > 0):
			player.block_movement()
		if (player.y > self.y and player.y_velocity < 0):
			player.block_movement()
		if (player.y < self.y and player.y_velocity > 0):
			player.block_movement()

class Aisle(MapElement):
	def __init__(self, x, y, width, height, texture):
		Entity.__init__(self, x, y, width, height, texture)
		self.type = MapElementType.AISLE
		self.supplies = 0

		self.is_collidable = True

class Road(MapElement):
	# Default values:

	# Dimensions
	default_width = 300 # px

	def __init__(self, x, y, width, height, texture):
		Entity.__init__(self, x, y, width, height, texture)
		self.type = MapElementType.ROAD

		self.is_collidable = False

class Sidewalk(MapElement):
	# Default values:

	# Dimensions
	default_width = 100 # px

	def __init__(self, x, y, width, height, texture):
		Entity.__init__(self, x, y, width, height, texture)
		self.type = MapElementType.SIDEWALK

		self.is_collidable = False

class Counter(MapElement):
	# Default values:

	# Dimensions
	default_width = 40 # px

	def __init__(self, x, y, width, height, texture):
		Entity.__init__(self, x, y, width, height, texture)
		self.type = MapElementType.COUNTER

		self.is_collidable = True

class Desk(MapElement):
	# Default values:

	# Dimensions
	default_width = 40 # px
	default_height = 120 # px

	def __init__(self, x, y, width, height, texture):
		Entity.__init__(self, x, y, width, height, texture)
		self.type = MapElementType.DESK

		self.is_collidable = True

# No relation to facade design pattern

class Facade(Entity):
	def __init__(self, x, y, width, height, texture):
		Entity.__init__(self, x, y, width, height, texture)

		# Whether the location is visible
		self.visible = True

	# Only renders the facade if the building is not location
	def render(self, renderer, camera_x, camera_y):
		if not self.visible:
			Entity.render(self, renderer, camera_x, camera_y)