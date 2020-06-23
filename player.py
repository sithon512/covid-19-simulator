import sdl2

from entity import Entity, MovableEntity
from items import Item, Vehicle, Supply, Inventory
from enums import InventoryType, ItemType, SupplyType

class Player(MovableEntity):
	# Default values:

	# Dimensions for collisions
	default_width = 50 # px
	default_height = 50 # px

	# Height to render the player
	render_height = 100 # px

	# Maximum speeds
	walking_speed = 100 # px / s
	running_speed = 250 # px / s

	# Default constructor
	def __init__(self):
		# Set starting position and texture later
		MovableEntity.__init__(
			self,
			0.0,
			0.0, 
			Player.default_width,
			Player.default_height,
			None,
			Player.walking_speed)

		# Survival meters
		self.money = 0
		self.health = 0
		self.morale = 0

		# Consumption controller
		self.consumption = ConsumptionController()

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

		distance_traveled = self.update_position()

		# Update walked distance if player is walking
		if self.vehicle == None:
			self.consumption.walk_distance += distance_traveled

	# Handles interact action
	def interact(self, messages):
		for item in self.nearby_items:
			item.handle_interaction(self, messages)

		for character in self.nearby_characters:
			character.handle_interaction(self, messages)

	# Adjusts player's velocity based on the parameters
	# Caps each component to player's maximum speed
	# Sets maximum speed based on whether the player is driving/running/walking
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
	# Renders the player with its render height
	def render(self, renderer, camera_x, camera_y):
		if self.vehicle == None:
			sdl2.SDL_RenderCopyEx(renderer, self.texture, None,
			sdl2.SDL_Rect(int(self.x - camera_x),
			int(self.y - camera_y - self.height), int(self.width),
			int(Player.render_height)), 0, None, sdl2.SDL_FLIP_NONE)

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
	# Returns false if the player's closet does not contain the 
	# quantity of that supply type
	# Returns true if the use is successful
	def use_supply(self, supply_type, quantity):
		for supply in range(quantity):
			if not self.closet.remove_supply(supply_type):
				return False
		return True

	def maintain_within_map(self, map_rectangle):
		if self.check_collision_directly(map_rectangle[0],\
		map_rectangle[1], map_rectangle[2], map_rectangle[3]):
			return

		if (self.x > map_rectangle[0] and self.x_velocity > 0):
			self.block_movement()
		if (self.x < map_rectangle[0] and self.x_velocity < 0):
			self.block_movement()
		if (self.y > map_rectangle[1] and self.y_velocity > 0):
			self.block_movement()
		if (self.y < map_rectangle[1] and self.y_velocity < 0):
			self.block_movement()

	# Also checks collision on the vehicle if player is driving
	def check_collision(self, other):
		if self.vehicle != None:
			if other == self.vehicle:
				other = self
				return self.vehicle.check_collision(other)

			# TO DO: damage player for crashing car

			return self.vehicle.check_collision(other)
		else:
			collision = other.check_collision_directly(
			self.x,
			self.y - self.height,
			self.width,
			Player.render_height)

			# If player touched an item, add to items touched
			if collision and isinstance(other, Item):
				self.consumption.items_touched.add(other)

			return collision

class ConsumptionController:
	# Default values:

	# Starting consumption values for each day
	default_food_consumption = 3
	default_soap_consumption = 1
	default_toilet_paper_consumption = 2
	default_pet_supply_consumption = 1

	# Player travel distance per extra increase in food consumption
	# i.e. if the player walks 25000 pixels, their food consumption will
	# increase by one for that day
	distance_per_food = 25000 # px

	# Items touched per extra increase in soap consumption
	# i.e. if the player touches 10 items, their soap consumption will
	# increase by one for that day
	items_touched_per_soap = 15

	# Message strings
	insufficient_food_message = ''
	insufficient_soap_message = ''
	insufficient_toilet_paper_message = ''
	insufficient_pet_supplies_message = ''

	def __init__(self):
		# Amount of each supply the player uses in a game day
		self.food_usage = 0
		self.soap_usage = 0
		self.toilet_paper_usage = 0
		self.pet_supplies_usage = 0

		# Daily amounts

		# Amount of distance the player walked
		self.walk_distance = 0 # px

		# Set of items the player touched
		self.items_touched = set()

		# Number of additional meals the player ate
		self.additional_meals_eaten = 0

		# Amount of distance the player's pet walked
		self.pet_walk_distance = 0

	# Consumes the usage amount for each supply
	# and sends message if the player does not have enough
	def consume_supplies(self, player, messages):
		self.calculate_consumption()

		if not self.check_sufficient_supplies(SupplyType.FOOD, self.food_usage,
			player.closet):
			messages.append(ConsumptionController.insufficient_food_message)
			# TO DO: deteriorate health and morale

		if not self.check_sufficient_supplies(SupplyType.SOAP, self.food_usage,
			player.closet):
			messages.append(ConsumptionController.insufficient_soap_message)
			# TO DO: deteriorate health and morale

		if not self.check_sufficient_supplies(SupplyType.TOILET_PAPER,
			self.food_usage, player.closet):
			messages.append(
				ConsumptionController.insufficient_toilet_paper_message)
			# TO DO: deteriorate health and morale

		if not self.check_sufficient_supplies(SupplyType.PET_SUPPLIES,
			self.food_usage, player.closet):
			messages.append(
				ConsumptionController.insufficient_pet_supplies_message)
			# TO DO: deteriorate pet's health
	
	# Removes the supply amount of supply type from the inventory
	# and returns false if the inventory does not that amount
	def check_sufficient_supplies(self, supply_type, supply_amount, inventory):
		supply = 0
		while supply < supply_amount:
			if not inventory.remove_supply(supply_type):
				return False
		return True

	# Calculates consumptions for each supply
	def calculate_consumption(self):
		self.food_usage = self.calculate_food_consumption()
		self.soap_usage = self.calculate_soap_consumption()
		self.toilet_paper_usage = self.calculate_toilet_paper_consumption()
		self.pet_supplies_usage = self.calculate_pet_supplies_consumption()

	# Food consumption is proportional to the amount of distance
	# the player walked
	def calculate_food_consumption(self):
		return int(ConsumptionController.default_food_consumption\
			+ self.walk_distance / ConsumptionController.distance_per_food)

	# Soap consumption is proportional to the amount of items the player touched
	def calculate_soap_consumption(self):
		return int(ConsumptionController.default_soap_consumption\
			+ (len(self.items_touched)\
			/ ConsumptionController.items_touched_per_soap))

	# Toilet paper consumption is proportional to amount of additional
	# meals the player ate
	def calculate_toilet_paper_consumption(self):
		return int(ConsumptionController.default_toilet_paper_consumption\
			+ self.additional_meals_eaten)

	# Pet supplies consumption is proportional to the amount of distance
	# the player's pet walked
	def calculate_pet_supplies_consumption(self):
		return int(self.pet_walk_distance\
			/ ConsumptionController.default_pet_supply_consumption\
			+ ConsumptionController.default_pet_supply_consumption)

	def reset_values(self):
		self.food_usage = 0
		self.soap_usage = 0
		self.toilet_paper_usage = 0
		self.pet_supplies_usage = 0
		self.walk_distance = 0
		self.items_touched = 0
		self.additional_meals_eaten = 0
		self.pet_walk_distance = 0

	# For debugging purposes
	def __str__(self):
		self.calculate_consumption()
		return 'Food: ' + str(self.food_usage) + '\n'\
			+ 'Soap: ' + str(self.soap_usage) + '\n'\
			+ 'Toilet Paper: ' + str(self.toilet_paper_usage) + '\n'\
			+ 'Pet Supplies: ' + str(self.pet_supplies_usage) + '\n'\
			+ 'Walk distance: ' + str(self.walk_distance) + '\n'\
			+ 'Items touched: ' + str(len(self.items_touched)) + '\n'\
			+ 'Additional meals eated: ' + str(self.additional_meals_eaten)\
			+ '\n' + 'Pet walk distance: ' + str(self.pet_walk_distance) + '\n'
