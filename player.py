import pygame

from entity import Entity, MovableEntity
from items import Vehicle
from enums import InventoryType

class Player(MovableEntity):
	# Default values:

	# Dimensions
	default_width = 50 # px
	default_height = 50 # px

	# Maximum speeds
	walking_speed = 100 # px / s
	running_speed = 250 # px / s

	# Default constructor
	def __init__(self):
		# Set starting position and texture later
		MovableEntity.__init__(self, 0.0, 0.0, 
			Player.default_width, Player.default_height, None, Player.walking_speed)

		# Survival meters
		self.money = 0
		self.health = 0
		self.morale = 0

		# Maps supply type to supply quantity
		# <SupplyType, int>
		self.supplies = {}

		# Items that the player is currently colliding with
		self.nearby_items = []

		# Characters that the player is currently nearby
		self.nearby_characters = []

		# Vehicle the player is driving
		# None if the player is not currently driving
		self.vehicle = None

		# Whether the user is running
		self.running = False

		# Inventory
		self.backpack = Inventory(InventoryType.BACKPACK,
			Inventory.default_backpack_capacity)

	# Moves the player based on their velocity
	def update(self):
		if self.vehicle != None:
			self.drive()

		self.update_position()

	# Handles interact action
	def interact(self, messages):
		for item in self.nearby_items:
			item.handle_interaction(self, messages)

		for character in self.nearby_characters:
			character.handle_interaction(self, messages)

	# Adjusts vehicle to the player
	def drive(self):
		self.vehicle.x = self.x
		self.vehicle.y = self.y

	# Adjusts player's velocity based on the parameters
	# Caps each component to player's maximum speed
	# Sets maximum speed based on whether the player is driving, running, or walking
	# Resets if there is no change
	def adjust_velocity(self, x_change, y_change, running):
		# Toggle running status
		self.running = running

		# Sets maximum speed
		if self.vehicle != None and running: # Vehicle turbo
			self.speed = Vehicle.turbo_speed
		elif self.vehicle != None: # Vehicle regular
			self.speed = Vehicle.regular_speed
		elif self.running: # Running
			self.speed = Player.running_speed
		else: # Walking
			self.speed = Player.walking_speed

		self.x_velocity += x_change * 0.10 * self.speed
		self.y_velocity += y_change * 0.10 * self.speed

		# Cap to maximum speed
		if self.x_velocity >= self.speed:
			self.x_velocity = self.speed

		if self.x_velocity <= -self.speed:
			self.x_velocity = -self.speed

		if self.y_velocity >= self.speed:
			self.y_velocity = self.speed

		if self.y_velocity <= -self.speed:
			self.y_velocity = -self.speed

		# No change, reset
		if x_change == 0:
			self.x_velocity = 0
		
		if y_change == 0:
			self.y_velocity = 0

	# Does not render player if they are driving
	def render(self, window, camera_x, camera_y):
		if self.vehicle == None:
			MovableEntity.render(self, window, camera_x, camera_y)

	# Adds item to the player's nearby items list
	def add_nearby_item(self, item):
		self.nearby_items.append(item)

	# Adds character to the player's nearby character list
	def add_nearby_character(self, character):
		self.nearby_characters.append(character)

	# Clears the nearby items and characters lists
	def reset_nearby_lists(self):
		self.nearby_items.clear()
		self.nearby_characters.clear()

	# Also checks collision on the vehicle if player is driving
	def check_collision(self, other):
		if self.vehicle != None:
			return self.vehicle.check_collision(other)
		else:
			return other.check_collision(self)

	# TO DO: add methods for adding and removing supplies

class Inventory:
	# Default values:

	default_backpack_capacity = 10 # supplies

	def __init__(self, type, capacity):
		# Inventory type
		self.type = type

		# Maps supply type to quantity
		# <SupplyType, int>
		self.supplies = {}

		# Number of items currently stored
		self.size = 0

		# Maximum limit for number of items
		self.capacity = capacity

	# Increases quantity for the supply type
	# Returns false if the inventory is full,
	# true if the add is successful
	def add_supply(self, supply_type):
		if self.size >= self.capacity:
			return False

		if supply_type in self.supplies:
			self.supplies[supply_type] = self.supplies.get(supply_type) + 1
		else:
			self.supplies[supply_type] = 1
		self.size += 1

		return True

	# Decreases quantity for the supply type
	def remove_supply(self, supply_type):
		if supply_type in self.supplies:
			self.supplies[supply_type] = self.supplies.get(supply_type) - 1
			self.size -= 1
