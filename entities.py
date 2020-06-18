import pygame, math, random

from enums import TextureType, LocationType, ItemType, SupplyType, PetType, CharacterType, AisleType, MapElementType
from locations import Location, House, GroceryStore
from player import Player
from items import Item, Vehicle, Sink, ShoppingCart, Supply
from npcs import Character, Pet
from factories import CharacterFactory, LocationFactory, ItemFactory, SupplyFactory, MapElementFactory

# Contains all entities
class Entities:
	def __init__(self):
		self.player = Player()

		# TO DO: add lists locations, characters, pets, and supplies

		# Containers
		self.locations = []
		self.items = []
		self.characters = []
		self.map_elements = []

		# Factories
		self.character_factory = CharacterFactory()
		self.location_factory = LocationFactory()
		self.item_factory = ItemFactory()
		self.supply_factory = SupplyFactory()
		self.map_element_factory = MapElementFactory()

	# Add Methods:

	# Creates and adds new location of parameter type
	def add_location(self, type, x, y, size, textures):
		location = self.location_factory.create(type, x, y, size, textures)
		self.locations.append(location)
		print("[Info] Created location " + str(type) + " at (" + str(x) + ", " + str(y) + ")")
		return location

	# Creates and adds new item of parameter type
	def add_item(self, type, x, y, textures):
		item = self.item_factory.create(type, x, y, textures)
		self.items.append(item)
		print("[Info] Created item " + str(type) + " at (" + str(x) + ", " + str(y) + ")")
		return item

	# Creates and adds new supply of parameter type
	def add_supply(self, type, x, y, textures):
		supply = self.supply_factory.create(type, x, y, textures)
		self.items.append(supply)
		print("[Info] Created supply " + str(type) + " at (" + str(x) + ", " + str(y) + ")")
		return supply

	# Creates and adds new character of parameter type
	def add_character(self, type, x, y, name, textures):
		character = self.character_factory.create(type, x, y, name, textures)
		self.characters.append(character)
		print("[Info] Created character " + str(type) + " at (" + str(x) + ", " + str(y) + ")")
		return character

	# Creates and adds new map element of parameter type
	def add_map_element(self, type, x, y, width, height, textures):
		map_element = self.map_element_factory.create(type, x, y, width, height, textures)
		self.map_elements.append(map_element)
		print("[Info] Created map element " + str(type) + " at (" + str(x) + ", " + str(y) + ")")
		return map_element

	# Remove Methods:

	# Various Methods:

	# Initialize player's starting position/meters and set texture
	def init_player(self, x, y, texture, money, health, morale):
		self.player.x = x
		self.player.y = y

		self.player.texture = texture

		self.player.money = money
		self.player.health = health
		self.player.morale = morale

# Performs operations on entities
class Controller:
	def __init__(self):

		# Changes in the player's x and y velocities each frame
		self.player_x_change = 0
		self.player_y_change = 0
		self.player_running = False
		self.player_interacted = False

		# Text to be displayed in the user interface
		self.location_text = '' # located at the top
		self.interaction_text = '' # located at the bottom
		self.messages = [] # message stack

		# Player's current meters
		self.current_money = 0
		self.current_health = 0
		self.current_morale = 0

	def update_entities(self, entities):
		# Handle location collisions
		for location in entities.locations:
			if location.check_collision(entities.player):
				self.location_text = location.name

		# Remove removed items
		# TO DO: do this in the same iteration as the handle loop
		for item in entities.items:
			if item.removed == True:
				entities.items.remove(item)
				break

		# Handle item collisions/interactions
		for item in entities.items:
			if item.check_collision(entities.player):
				item.handle_collision(entities.player)
				entities.player.add_nearby_item(item)
				self.interaction_text = item.name + ": " + item.interaction_message

		# Handle character collisions/interactions
		for character in entities.characters:
			if character.check_collision(entities.player):
				# TO DO: add close proximity instead of just collision
				character.handle_collision(entities.player)
				entities.player.add_nearby_character(character)
				self.interaction_text = character.name + ": " + character.interaction_message

		# Update player
		entities.player.adjust_velocity(
			self.player_x_change,
			self.player_y_change,
			self.player_running)
		
		if self.player_interacted:
			entities.player.interact(self.messages)
		
		entities.player.update()

		# Nearby items and characters are updated every frame
		entities.player.reset_nearby_lists()

		self.current_money = entities.player.money
		self.current_health = entities.player.health
		self.current_morale = entities.player.morale

		self.reset_values()

	# Interface Methods:

	# Interface between the controller and the user interface for player movement input
	# Adds/subtracts to player up, down, left, and right changes based on parameters
	# and sets whether the player is running
	def move_player(self, up, down, left, right, running):
		if up:
			self.player_y_change -= 1
		if down:
			self.player_y_change += 1
		if left:
			self.player_x_change -= 1
		if right:
			self.player_x_change += 1
		if running:
			self.player_running = True

	# Interface between the controller and the user interface for player interaction
	def interact_player(self):
		self.player_interacted = True

	# Interface between the controller and the user interface for updating messages
	def update_messages(self, middle_text, info_text, message_stack):
		# Update location and interaction messages
		middle_text.set_top(self.location_text)
		self.location_text = ''

		middle_text.set_bottom(self.interaction_text)
		self.interaction_text = ''

		# Update message stack
		message_stack.insert(self.messages)
		self.messages.clear()

		# Update info display
		info_text.set(self.current_money, self.current_health, self.current_morale)

	# Resets values that are only valid for each frame
	def reset_values(self):
		self.player_x_change = 0
		self.player_y_change = 0
		self.player_running = False
		self.player_interacted = False

	# Game Initialization Methods:

	# Initializes the locations
	def init_map(self, entities, textures):
		self.create_house(entities, textures)

		self.create_grocery_store(entities, textures, 
			House.default_width * 5, -House.default_height, 1.0)

		self.create_grocery_store(entities, textures, 
			0, House.default_width * 3, 2.0)

	def create_house(self, entities, textures):
		house = entities.add_location(LocationType.HOUSE, 0, 0, 1.0, textures)

		sink = entities.add_item(ItemType.SINK, house.x + house.width -
			Sink.default_width, house.y, textures)

		pet = entities.add_character(CharacterType.PET, house.x + house.width / 3,
			house.y + house.height / 3, "Dog", textures)

		car = entities.add_item(ItemType.VEHICLE, house.x + house.width + 
			Vehicle.default_width / 2, house.y + house.height / 2, textures)

	# Creates grocery store at the x and y position
	def create_grocery_store(self, entities, textures, x, y, size):

		store = entities.add_location(LocationType.GROCERY_STORE, x, y, size, textures)

		cart_num = 0
		while cart_num < GroceryStore.default_num_carts:
			entities.add_item(ItemType.SHOPPING_CART, store.x + store.width / 4 +
				cart_num * ShoppingCart.default_width * 2, store.y -
				ShoppingCart.default_height * 2, textures)
			cart_num += 1

		num_aisles = store.width / GroceryStore.min_aisle_spacing - 1

		aisle = 0
		while aisle < num_aisles:
			random_aisle_type = random.randrange(0, 3)
			random_aisle_density = random.randrange(0, 100)

			self.create_aisle(
				entities,
				textures,
				store.x + (aisle + 1) * GroceryStore.min_aisle_spacing,
				store.y + GroceryStore.min_aisle_spacing / 2,
				store.height,
				random_aisle_type,
				random_aisle_density)
			aisle += 1

	# Creates aisle starting at the x and y position of a certain length
	# type (AisleType) defines what type of supplies to put
	# density [0, 100] defines how populated the aisle is
	def create_aisle(self, entities, textures, x, y, length, type, density):
		# Types of supplies to place in aisle
		valid_supply_types = []

		# Determine valid supplies depending on aisle type
		if type == AisleType.GROCERIES:
			valid_supply_types.append(SupplyType.FOOD)
		elif type == AisleType.TOILETRIES:
			valid_supply_types.append(SupplyType.SOAP)
			valid_supply_types.append(SupplyType.HAND_SANITIZER)
			valid_supply_types.append(SupplyType.TOILET_PAPER)
		elif type == AisleType.PET_SUPPLIES:
			valid_supply_types.append(SupplyType.PET_SUPPLIES)

		# Minimum spacing between supplies
		min_spacing = Supply.default_height * 1.5

		# Maximum number of supplies for the aisle
		max_num_supplies = int(length / (Supply.default_height + min_spacing))

		supply = 0
		while supply < max_num_supplies:
			# Decide whether to add supply based on density
			random_int = random.randrange(0, 100)
			if random_int > density:
				supply += 1
				continue

			# Pick random supply from valid supplies
			# This has no effect for groceries and pet supplies since
			# there is only valid supply type for those aisles;
			# however, we may add more in the future
			random_int = random.randrange(0, len(valid_supply_types))
			supply_type = valid_supply_types[random_int]

			entities.add_supply(supply_type, x,
				y + supply * min_spacing, textures)

		# Create aisle map element
		entities.add_map_element(
			MapElementType.AISLE,
			x - Supply.default_width / 2,
			y - Supply.default_height / 2,
			Supply.default_width * 2,
			length - GroceryStore.min_aisle_spacing,
			textures)