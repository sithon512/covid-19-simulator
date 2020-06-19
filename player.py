import sdl2

from entity import Entity, MovableEntity
from items import Vehicle, Supply, Inventory
from enums import InventoryType, ItemType

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

		# Items that the player is currently colliding with
		self.nearby_items = []

		# Characters that the player is currently nearby
		self.nearby_characters = []

		# Vehicle the player is driving
		# None if the player is not currently driving
		self.vehicle = None

		# Item the player is carrying
		# None if the player is not carrying anything
		self.item_being_carried = None

		# Most recent shopping cart the player touched
		# Its contents will be checked out when the player
		# goes to a checkout lane
		self.shopping_cart = None

		# Whether the user is running
		self.running = False

		# Inventories

		# What the player can carry on foot
		self.backpack = Inventory(InventoryType.BACKPACK,
			Inventory.default_backpack_capacity)

		# What the player can hold at their house,
		# daily requirements are subtracted from here
		self.closet = Inventory(InventoryType.CLOSET,
			Inventory.default_closet_capacity)

	# Moves the player based on their velocity
	def update(self):
		if self.vehicle != None:
			self.vehicle.drive(self)

		if self.item_being_carried != None:
			self.item_being_carried.carry(self)

		self.update_position()

	# Handles interact action
	def interact(self, messages):
		for item in self.nearby_items:
			item.handle_interaction(self, messages)

		for character in self.nearby_characters:
			character.handle_interaction(self, messages)

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
	def render(self, renderer, camera_x, camera_y):
		if self.vehicle == None:
			MovableEntity.render(self, renderer, camera_x, camera_y)

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

	# Decreases supply count by the quantity for the supply type
	# from the player's closet
	# Returns false if the player's closet does not contain the quantity of that supply type
	# Returns true if the use is successful
	def use_supply(self, supply_type, quantity):
		num = 0
		while num < quantity:
			if not self.closet.remove_supply(supply_type):
				return False
			num += 1
		return True

	# Also checks collision on the vehicle if player is driving
	def check_collision(self, other):
		if self.vehicle != None:
			if other == self.vehicle:
				other = self
				return self.vehicle.check_collision(other)
			
			# Damage player from vehicle accident depending on the speed
			vehicle_collision = self.vehicle.check_collision(other)
			if vehicle_collision and self.running and self.health > 25:
				self.health = 25
			elif vehicle_collision and self.health > 50:
				self.health = 50

			return vehicle_collision
		else:
			return other.check_collision(self)

	# TO DO: add methods for adding and removing supplies
