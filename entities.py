import sdl2, math, random

from enums import (
	TextureType,
	LocationType,
	ItemType, SupplyType,
	PetType,
	CharacterType,
	AisleType,
	MapElementType
)
from locations import (
	Location,
	House,
	GroceryStore,
	GasStation,
	Road,
	Sidewalk,
	Counter,
	Desk
)
from items import (
	Item,
	Vehicle,
	Sink,
	ShoppingCart,
	Supply,
	Door,
	SelfCheckout,
	Closet
)
from factories import (
	CharacterFactory,
	LocationFactory,
	ItemFactory,
	SupplyFactory,
	MapElementFactory
)
from player import Player
from npcs import Character, Pet, Civilian

# Contains all entities
class Entities:
	def __init__(self):
		self.player = Player()
		
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
		return location

	# Creates and adds new item of parameter type
	def add_item(self, type, x, y, textures):
		item = self.item_factory.create(type, x, y, textures)
		self.items.append(item)
		return item

	# Creates and adds new supply of parameter type
	def add_supply(self, type, x, y, textures):
		supply = self.supply_factory.create(type, x, y, textures)

		# Determine the price for the supply
		# TO DO: pass difficulty to this function
		supply.generate_price(1.0)

		self.items.append(supply)
		return supply

	# Creates and adds new character of parameter type
	def add_character(self, type, x, y, name, textures):
		character = self.character_factory.create(type, x, y, name, textures)
		self.characters.append(character)
		return character

	# Creates and adds new map element of parameter type
	def add_map_element(self, type, x, y, width, height, textures):
		map_element = self.map_element_factory.create(type, x, y, width,
			height, textures)
		self.map_elements.append(map_element)
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
		self.displayed_inventory = False

		# Text to be displayed in the user interface
		self.location_text = '' # located at the top
		self.interaction_text = '' # located at the bottom
		self.messages = [] # message stack

		# Player's current meters
		self.current_money = 0
		self.current_health = 0
		self.current_morale = 0

		self.last_message = 0

	def update_entities(self, entities):
		# Handle location collisions
		for location in entities.locations:
			# Whether the player is inside the location
			player_inside = False

			if location.entity_inside(entities.player):
				location.toggle_visibility(True)
				player_inside = True
			if entities.player.check_collision(location):
				self.location_text = location.name
				location.handle_collision(entities.player)

				# Player is running into a wall
				if location.is_visible() and not player_inside:
					location.block_player_from_exiting(entities.player)
			else:
				location.toggle_visibility(False)

		# Handle map element collisions if applicable
		for element in entities.map_elements:
			# Only check collisions for map elements that are collidable
			if element.is_collidable:
				if entities.player.check_collision(element):
					element.handle_collision(entities.player)

		# Remove removed characters and items
		# TO DO: do this in the same iteration as the handle loop
		for item in entities.items:
			if item.removed:
				entities.items.remove(item)
				break

		for character in entities.characters:
			if character.removed:
				entities.characters.remove(character)
				break

		# Handle item collisions/interactions
		for item in entities.items:
			if entities.player.check_collision(item):
				item.handle_collision(entities.player)
				entities.player.add_nearby_item(item)
				self.interaction_text = item.name + ": "\
					+ item.interaction_message

		# Handle character collisions/interactions
		for character in entities.characters:
			character.update(entities)
			if entities.player.check_collision(character):
				# TO DO: add close proximity instead of just collision
				character.handle_collision(entities.player)
				entities.player.add_nearby_character(character)
				self.interaction_text = character.name + ": "\
					+ character.interaction_message

		# Update player
		entities.player.adjust_velocity(
			self.player_x_change,
			self.player_y_change,
			self.player_running)
		
		if self.player_interacted:
			entities.player.interact(self.messages)

		# TO DO: this is just a placeholder method to see what is in the
		# player's inventory
		if self.displayed_inventory	and 500\
		< sdl2.SDL_GetTicks() - self.last_message:
			self.messages.append('Closet contents: '
				+ str(entities.player.closet))

			self.messages.append('Backpack contents: '
				+ str(entities.player.backpack))

			self.last_message = sdl2.SDL_GetTicks()

		entities.player.update()

		# Nearby items and characters are updated every frame
		entities.player.reset_nearby_lists()

		self.current_money = entities.player.money
		self.current_health = entities.player.health
		self.current_morale = entities.player.morale

		self.reset_values()

	# Generates new NPCs
	def generate_NPCs(self, entities, textures):
		for location in entities.locations:
			if location.type == LocationType.GROCERY_STORE\
			or location.type == LocationType.GAS_STATION:
				self.generate_shoppers(entities, textures, location)

	# Generates new shoppers for grocery store every random shopper
	# genereation interval
	# TO DO: can tie generation time upper bound to game difficulty
	# for a more dense population
	def generate_shoppers(self, entities, textures, store):
		if store.time_before_next_npc_generation < sdl2.SDL_GetTicks()\
		- store.last_npc_generated:

			entities.add_character(
				CharacterType.SHOPPER,
				store.entrance_x,
				store.entrance_y - Civilian.default_height,
				"Shopper",
				textures)

			# Determine next time to generate shopper, within bounds
			store.time_before_next_npc_generation = random.randrange(
				5000, 25000) # ms
			store.last_npc_generated = sdl2.SDL_GetTicks()

	# Returns true if the player's meters are good
	# Returns false if the player lost the game
	def check_player_meters(self, entities):
		if entities.player.morale == 0:
			print("Player's morale is 0")
			return False

		elif entities.player.health == 0:
			print("Player's health is 0")
			return False

		return True

	# Interface Methods:

	# Interface between the controller and the UI for player movement input
	# Adds/subtracts to player up, down, left, and right changes
	# based on parameters and sets whether the player is running
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

	# Interface between the controller and the UI for player interaction
	def interact_player(self):
		self.player_interacted = True

	# Interface between the controller and the UI for player inventory
	def display_inventory(self):
		self.displayed_inventory = True

	# Interface between the controller and the UI for updating messages
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
		info_text.set(
			self.current_money,
			self.current_health,
			self.current_morale)

	# Resets values that are only valid for each frame
	def reset_values(self):
		self.player_x_change = 0
		self.player_y_change = 0
		self.player_running = False
		self.player_interacted = False
		self.displayed_inventory = False

	# Game Initialization Methods:
	# NOTE: these methods will be heavily refactored as we go
	# they are just here as placeholders to test the game world

	# Initializes the locations
	def init_map(self, entities, textures):
		house = self.create_house(entities, textures)

		grocery_store = self.create_grocery_store(entities, textures, 
			House.default_width * 7, 0, 1.0)

		gas_station = self.create_gas_station(entities, textures, 
			House.default_width * 4, 0, 1.0)

		road = self.create_road_system(entities, textures, house, grocery_store)

		# Sidewalk from house to road
		self.create_road(entities, textures, MapElementType.SIDEWALK,
			house.x + house.width / 2 - Sidewalk.default_width / 2,
			house.y + house.height,
			house.x + house.width / 2 - Sidewalk.default_width / 2,
			road.y,
			Sidewalk.default_width,
			True)

		# Driveway from house to road
		self.create_road(entities, textures, MapElementType.DRIVEWAY,
			house.x + house.width + Vehicle.default_height * 1.5
			- Road.default_width / 4,
			house.y + house.height * 0.40,
			house.x + house.width,
			road.y,
			Road.default_width / 2,
			True)

		# Parking lot from gas station to road
		self.create_parking_lot(entities, textures,
			gas_station.x - Vehicle.default_width,
			gas_station.y + gas_station.height,
			gas_station.x + gas_station.width + Vehicle.default_width, road.y)

		# Parking lot from grocery store to road
		self.create_parking_lot(entities, textures,
			grocery_store.x, grocery_store.y + grocery_store.height,
			grocery_store.x + grocery_store.width, road.y)

	# Creates house with door, sink, closet, dog, and car
	def create_house(self, entities, textures):
		house = entities.add_location(LocationType.HOUSE,
			-Player.default_width, -Player.default_height, 1.0, textures)
		house.y -= house.height
		house.facade.y = house.y

		entities.add_item(ItemType.DOOR, house.x + house.width / 2 - 
			Door.default_width / 2,	house.y + house.height -
			Door.default_height / 2, textures)

		kitchen = entities.add_item(ItemType.KITCHEN,
			house.x, house.y, textures)

		sink = entities.add_item(ItemType.SINK, kitchen.x + kitchen.width,
			house.y, textures)

		entities.add_item(ItemType.BED, house.x + house.width * 0.70,
			house.y + sink.height / 6, textures)

		desk = entities.add_map_element(MapElementType.DESK, house.x, house.y
			/ 2, Desk.default_width, Desk.default_height, textures)

		entities.add_item(ItemType.COMPUTER, desk.x, desk.y, textures)

		entities.add_map_element(MapElementType.COUNTER, sink.x + sink.width,
			house.y, Counter.default_width, sink.height, textures)

		entities.add_item(ItemType.CLOSET, house.x + house.width
			- Closet.default_width, house.y + house.height / 2, textures)

		entities.add_character(CharacterType.PET, house.x + house.width
			- house.width / 3, house.y + house.height * 0.75, "Dog", textures)

		vehicle = entities.add_item(ItemType.VEHICLE, house.x + house.width + 
			Vehicle.default_height, house.y + house.height / 2, textures)
		vehicle.angle = 90

		return house

	# Creates grocery store at the x and y position
	def create_grocery_store(self, entities, textures, x, y, size):
		store = entities.add_location(
			LocationType.GROCERY_STORE,	x, y, size,	textures)

		store.y -= store.height
		store.facade.y = store.y
		store.stockroom = self.create_stock(entities, textures)

		# Each store will have two entrances/exits
		door = entities.add_item(
			ItemType.DOOR,
			store.x + Door.default_width,
			store.y + store.height - Door.default_height / 2,
			textures)

		store.entrance_x = door.x
		store.entrance_y = door.y

		entities.add_item(
			ItemType.DOOR,
			store.x + store.width - Door.default_width * 2,
			store.y + store.height - Door.default_height / 2,
			textures)

		# Add shopping carts
		cart = 0
		while cart < GroceryStore.default_num_carts * size:
			entities.add_item(
				ItemType.SHOPPING_CART,
				store.x + ShoppingCart.default_width * 3, 
				store.y + store.height
				- GroceryStore.min_aisle_spacing * (cart + 1) / 2,
				textures).angle = 90.0
			cart += 1

		# Add aisles
		num_aisles = store.width / (GroceryStore.min_aisle_spacing +
			Supply.default_width * 2) - 1

		aisle = 0
		aisle_x = x
		while aisle < num_aisles:
			random_aisle_type = random.randrange(0, 3)

			# Manipulate chances of each aisle
			if random_aisle_type == AisleType.TOILETRIES:
				if random.randrange(0, 100) < 30:
					random_aisle_type -= 1
			if random_aisle_type == AisleType.PET_SUPPLIES:
				if random.randrange(0, 100) < 60:
					random_aisle_type -= 1

			random_aisle_density = random.randrange(0, 100)

			self.create_aisle(
				entities,
				textures,
				aisle_x,
				store.y + GroceryStore.min_aisle_spacing,
				store.height - GroceryStore.min_aisle_spacing * 3,
				random_aisle_type,
				random_aisle_density,
				False)

			self.create_aisle(
				entities,
				textures,
				aisle_x + GroceryStore.min_aisle_spacing,
				store.y + GroceryStore.min_aisle_spacing,
				store.height - GroceryStore.min_aisle_spacing * 3,
				random_aisle_type,
				random_aisle_density,
				True)

			aisle += 1
			aisle_x += GroceryStore.min_aisle_spacing\
				+ Supply.default_width * 1.5

		# Always have at least one grocery aisle that is wider
		# on the right side of the store
		self.create_aisle(
			entities,
			textures,
			aisle_x,
			store.y + GroceryStore.min_aisle_spacing,
			store.height - GroceryStore.min_aisle_spacing * 3,
			AisleType.GROCERIES,
			random_aisle_density,
			False)

		self.create_aisle(
			entities,
			textures,
			store.x + store.width - Supply.default_width,
			store.y + GroceryStore.min_aisle_spacing,
			store.height - GroceryStore.min_aisle_spacing * 3,
			AisleType.GROCERIES,
			random_aisle_density,
			False)

		# Add checkout registers
		num_checkouts = int(size) * GroceryStore.default_num_registers

		checkout = 0
		while checkout < num_checkouts:
			entities.add_item(
				ItemType.SELF_CHECKOUT,
				store.x + store.width / 3 +
				checkout * SelfCheckout.default_width * 4, 
				store.y + store.height - SelfCheckout.default_height * 3,
				textures)
			checkout += 1

		# Add stockers
		entities.add_character(CharacterType.STOCKER, door.x, store.y,
			'Stocker', textures)
		entities.add_character(CharacterType.STOCKER, door.x, store.y,
			'Stocker', textures)
		entities.add_character(CharacterType.STOCKER, door.x, store.y,
			'Stocker', textures)

		return store

	# Creates aisle starting at the x and y position of a certain length
	# type (AisleType) defines what type of supplies to put
	# density [0, 100] defines how populated the aisle is
	# center_aisle determines whether to make the aisle bigger
	def create_aisle(self, entities, textures, x, y, length, type, density,
		center_aisle):
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
			supply += 1

		# Create aisle map element
		width = Supply.default_width

		if center_aisle:
			width = Supply.default_width * 1.5

		aisle = entities.add_map_element(
			MapElementType.AISLE,
			x,
			y - Supply.default_height / 2,
			width,
			length,
			textures)
		aisle.supplies = type

		return aisle

	# Creates conveniance store for gas station
	def create_conveniance_store(self, entities, textures, x, y, size):
		store = entities.add_location(
			LocationType.GAS_STATION, x, y, size, textures)

		store.y -= store.height
		store.facade.y = store.y
		store.stockroom = self.create_stock(entities, textures)

		# Conveniance stores only have one door
		door = entities.add_item(
			ItemType.DOOR,
			store.x + Door.default_width,
			store.y + store.height - Door.default_height / 2,
			textures)
		store.entrance_x = door.x
		store.entrance_y = door.y

		num_aisles = GasStation.default_num_aisles

		# Add aisles
		aisle = 0
		while aisle < num_aisles:
			random_aisle_type = random.randrange(0, 3)
			random_aisle_density = random.randrange(0, 100)

			self.create_aisle(
				entities,
				textures,
				store.x + aisle * GasStation.min_aisle_spacing,
				store.y + GasStation.min_aisle_spacing * 1.25,
				store.height - int(GasStation.min_aisle_spacing * 2.25),
				random_aisle_type,
				random_aisle_density,
				False)
			aisle += 1

		# Add one checkout register
		entities.add_item(
			ItemType.SELF_CHECKOUT,
			store.x + store.width / 3, 
			store.y + store.height - SelfCheckout.default_height,
			textures)

		return store

	# Randomly creates a list of supplies for the stockroom of a store
	def create_stock(self, entities, textures):
		stock = []

		supply = 0
		while supply < GroceryStore.default_stockroom_size:
			stock.append(entities.add_supply(
				random.randrange(0, SupplyType.PET_SUPPLIES),
				-1000000, # out of map
				-1000000, # out of map
				textures))
			supply += 1

		return stock

	def create_gas_station(self, entities, textures, x, y, size):
		store = self.create_conveniance_store(entities, textures, x, y, 1.0)

		y = store.y + store.height + GasStation.min_dispenser_spacing / 2
		num_dispensers = size * GasStation.default_num_dispensers

		dispensers = 0
		while dispensers < num_dispensers:
			fuel_dispenser = entities.add_item(ItemType.FUEL_DISPENSER,
				x + dispensers * GasStation.min_dispenser_spacing, y, textures)

			fuel_dispenser.price = 3.0
			dispensers += 1

		return store

	# For now, creates a straight road from the starting to the ending entity
	# TO DO: create road system from the starting entity to the ending entity
	def create_road_system(self, entities, textures, start_entity, end_entity):
		start_x = start_entity.x - start_entity.width
		end_x = end_entity.x + end_entity.width * 2

		start_y = start_entity.y + start_entity.height * 2

		return entities.add_map_element(
			MapElementType.ROAD,
			start_x,
			start_y,
			abs(start_x - end_x),
			int(Road.default_width),
			textures)

	# Creates the desired road type from the starting to the ending positions
	# vertical determinines whether the sidewalk is vertical or horizontal
	def create_road(self, entities, textures, type, start_x, start_y, 
		end_x, end_y, width, vertical):
		if vertical:
			entities.add_map_element(
				type,
				start_x,
				start_y,
				width,
				abs(start_y - end_y),
				textures)
		else:
			entities.add_map_element(
				type,
				start_x,
				start_y,
				abs(start_x - end_x),
				width,
				textures)

	# Creates parking lot from the starting positions to the ending positions
	def create_parking_lot(self, entities, textures, start_x, start_y,
		end_x, end_y):
		entities.add_map_element(
				MapElementType.PARKING_LOT,
				start_x,
				start_y,
				abs(start_x - end_x),
				abs(start_y - end_y),
				textures)