import sdl2, math, random

from enums import (
	TextureType,
	LocationType,
	ItemType, SupplyType,
	PetType,
	CharacterType,
	AisleType,
	MapElementType,
	RoadType
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
	Bed,
	Computer,
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

		self.map_rectangle = (0, 0, 0, 0)

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
	# Real-time length of game day
	# Keep in mind that sleeping and working skips most of it
	game_day_length = 600000 # ms (10 minutes)

	morale_decrease_interval = game_day_length / 4
	health_decrease_interval = game_day_length / 78

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

		self.game_day = 0
		self.game_time = 0

		# Time added to the game time from working or sleeping
		# since the game time is based on SDL_GetTicks()
		self.added_time = 0

		self.last_message = 0
		self.last_morale_decreased = 0
		self.last_health_decreased = 0

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

		self.close_stores(entities)

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

			if character.in_proximity(entities.player):
				character.handle_close_proximity(entities.player,
					self.messages)
			if entities.player.check_collision(character):
				character.handle_collision(entities.player)
				entities.player.add_nearby_character(character)
				self.interaction_text = character.name + ": "\
					+ character.interaction_message

		# Update player
		entities.player.adjust_velocity(
			self.player_x_change,
			self.player_y_change,
			self.player_running)

		# If player has a mask in their inventory, equip it
		if entities.player.backpack.get_quantity(SupplyType.MASK) > 0\
		   or entities.player.closet.get_quantity(SupplyType.MASK) > 0:
			if not entities.player.wearing_mask:
				self.messages.append('Equipped mask')
			entities.player.wearing_mask = True
		
		if self.player_interacted:
			entities.player.interact(self.messages, self.get_game_minutes())

		# TO DO: this is just a placeholder method to see what is in the
		# player's inventory
		if self.displayed_inventory	and 500\
		< sdl2.SDL_GetTicks() - self.last_message:
			self.messages.append('Closet contents: '
				+ str(entities.player.closet))

			self.messages.append('Backpack contents: '
				+ str(entities.player.backpack))

			self.last_message = sdl2.SDL_GetTicks()

		entities.player.maintain_within_map(entities.map_rectangle)
		entities.player.update()

		if entities.player.working:
			self.handle_player_working(entities.player)

		if entities.player.sleeping:
			self.handle_player_sleeping(entities.player)

		# Update game time
		self.update_game_time(entities.player)

		entities.player.reset_values()

		# Decrease player morale every interval
		if Controller.morale_decrease_interval < sdl2.SDL_GetTicks()\
			- self.last_morale_decreased:
			entities.player.morale -= 1
			self.last_morale_decreased = sdl2.SDL_GetTicks()

		# Decrease player health if infected
		if entities.player.infected and Controller.health_decrease_interval\
			< sdl2.SDL_GetTicks() - self.last_health_decreased:
			entities.player.health -= 1
			self.last_health_decreased = sdl2.SDL_GetTicks()

		self.current_money = entities.player.money
		self.current_health = entities.player.health
		self.current_morale = entities.player.morale

		self.reset_values()

	# Generates new NPCs
	def generate_NPCs(self, entities, textures):
		for location in entities.locations:
			if (location.type == LocationType.GROCERY_STORE\
			or location.type == LocationType.GAS_STATION)\
			and location.is_open(self.get_game_minutes()):
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
				'Shopper',
				textures)

			# Determine next time to generate shopper, within bounds
			store.time_before_next_npc_generation = random.randrange(
				3000, 18000) # ms
			store.last_npc_generated = sdl2.SDL_GetTicks()

	# Returns true if the player's meters are good
	# Returns false if the player lost the game
	def check_player_meters(self, entities):
		if entities.player.morale <= 0:
			print("GAME OVER: Player's morale is 0")
			return False

		elif entities.player.health <= 0:
			print("GAME OVER: Player's health is 0")
			return False

		return True

	# Skips the game time to the end of the work day and
	# decreases morale and pays player for each hour worked
	def handle_player_working(self, player):
		hours_worked = abs(Computer.end_time - self.get_game_minutes()) / 60.0
		player.paycheck += hours_worked * player.wage
		player.morale -= int(hours_worked)
		self.added_time += Computer.end_time - self.get_game_minutes()

	# Skips the game time to the end of the sleeping time
	# increases morale and health for each hour the player slept
	def handle_player_sleeping(self, player):
		hours_slept = abs(Bed.end_time - self.get_game_minutes()) / 60.0
		player.morale += int(hours_slept)
		player.health += int(hours_slept)
		self.added_time += (1440 - self.get_game_minutes()) + Bed.end_time

	# Locks or unlocks stores based on the game time and the store's
	# opening/closing times
	def close_stores(self, entities):
		for location in entities.locations:
			if not location.is_open(self.get_game_minutes()):
				location.set_door_locks(True)
			else:
				location.set_door_locks(False)

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
			self.current_morale,
			self.game_day,
			self.get_game_minutes())

	# Updates the game day and time
	# If day is over, subtracts supplies from player based on consumption
	def update_game_time(self, player):
		self.game_time = sdl2.SDL_GetTicks()\
			- self.game_day * Controller.game_day_length\
			+ (self.added_time / 1440.0 * Controller.game_day_length)
			
		# Consume daily supplies if day passed
		if self.game_time > Controller.game_day_length:
			self.game_day += 1

			# Do not consume anything on day 1 since the game starts then
			if self.game_day != 1:
				player.consumption.consume_supplies(player, self.messages)

		# Check if week passed
		if self.game_day != 0 and self.game_day % 7 == 0:
			# Deliver pay check money to player
			player.money += player.paycheck
			if player.paycheck != 0:
				self.messages.append('Paycheck received: $'
					+ str(int(player.paycheck)))
			player.paycheck = 0

	# Returns the in-game minutes based on the game day length
	def get_game_minutes(self):
		return (86400 / (Controller.game_day_length / 1000.0))\
			* (self.game_time / 60000.0)

	# Resets values that are only valid for each frame
	def reset_values(self):
		self.player_x_change = 0
		self.player_y_change = 0
		self.player_running = False
		self.player_interacted = False
		self.displayed_inventory = False

class WorldCreator:
	# Neighborhood dimensions
	neighborhood_length = 4000 # px
	neighborhood_height = 2000 # px

	# Spacing in between houses in a neighborhood
	neighborhood_house_x_spacing = 1000 # px
	neighborhood_house_y_spacing = 700 # px

	# Length of the middle road for each neighborhood in the world
	middle_road_length_per_neighborhood = 2400 # px

	store_distance_from_road = 400 # px

	def __init__(self, num_neighborhoods):
		self.num_neighborhoods = num_neighborhoods

		self.middle_road = None
		self.town_center_road = None
		self.neighborhood_roads = []

		self.player_house = None

	def create(self, entities, textures):
		self.create_road_system(entities, textures)

		for neighborhood_road in self.neighborhood_roads:
			self.create_neighborhood(entities, textures, neighborhood_road)

		self.create_town_center(entities, textures)

		self.player_house = self.pick_player_house(entities)
		self.create_player_house(entities, textures)
		self.create_vehicles(entities, textures)

		self.place_player_in_house(entities.player)

		# Returns the rectangle of the world map
		return (-WorldCreator.neighborhood_length\
			- WorldCreator.store_distance_from_road, 0,\
			self.town_center_road.width, self.middle_road.height\
			+ WorldCreator.neighborhood_height)

	def create_road_system(self, entities, textures):
		# Create road that leads to town center
		middle_road_length = (self.num_neighborhoods + 1)\
			* WorldCreator.middle_road_length_per_neighborhood

		# Vertical, medium road from (0, 0) to (0, middle_road_length)
		self.middle_road = self.create_road(entities, textures,	0, 0, 0,
			middle_road_length, RoadType.MEDIUM, True)

		# Create neighborhood roads
		for neighborhood_road in range(self.num_neighborhoods):
			# Horizontal, small road connecting to the middle road
			road = self.create_road(
				entities, textures,
				self.middle_road.x - WorldCreator.neighborhood_length,
				(neighborhood_road + 1) * WorldCreator.neighborhood_height,
				self.middle_road.x,
				(neighborhood_road + 1) * WorldCreator.neighborhood_height,
				RoadType.SMALL,	False)
			self.neighborhood_roads.append(road)

			# Create connecting sidewalk on the left end
			self.create_sidewalk(entities, textures,
				road.x - Sidewalk.default_width,
				road.y - Sidewalk.default_width,
				road.x,	road.y + road.height + Sidewalk.default_width, True)
		
		# Create town center road
		# Horizontal, large road at the bottom of middle road,
		# spanning the entire map
		self.town_center_road = self.create_road(
			entities, textures,
			self.middle_road.x - WorldCreator.neighborhood_length\
			- WorldCreator.store_distance_from_road,
			self.middle_road.y + self.middle_road.height,
			self.middle_road.x + WorldCreator.neighborhood_length,
			self.middle_road.y + self.middle_road.height,
			RoadType.LARGE,	False)

	def create_road(self, entities, textures, start_x, start_y, end_x, end_y,
		road_type, vertical):

		# Determine thickness based on road type
		if road_type == RoadType.SMALL:
			thickness = Road.small_thickness
		elif road_type == RoadType.MEDIUM:
			thickness = Road.medium_thickness
		elif road_type == RoadType.LARGE:
			thickness = Road.large_thickness

		if vertical:
			width = thickness
			height = abs(start_y - end_y)
		else:
			width = abs(start_x - end_x)
			height = thickness

		road = entities.add_map_element(MapElementType.ROAD, start_x, start_y,
			width, height, textures)

		# Create sidewalks on both sides of the road
		if vertical:
			self.create_sidewalk(entities, textures,
			road.x - Sidewalk.default_width,
			road.y,
			road.x - Sidewalk.default_width,
			road.y + road.height,
			True)
			self.create_sidewalk(entities, textures,
			road.x + road.width,
			road.y,
			road.x + road.width,
			road.y + road.height,
			True)
		else:
			self.create_sidewalk(entities, textures,
			road.x,
			road.y - Sidewalk.default_width,
			road.x + road.width,
			road.y - Sidewalk.default_width,
			False)
			self.create_sidewalk(entities, textures,
			road.x,
			road.y + road.height,
			road.x + road.width,
			road.y + road.height,
			False)

		return road

	def create_neighborhood(self, entities, textures, neighborhood_road):
		num_houses = int(neighborhood_road.width
			/ WorldCreator.neighborhood_house_x_spacing)

		# Create houses north of the road
		for house in range(num_houses):
			self.create_neighborhood_house(entities, textures,
			neighborhood_road.x
				+ (house * WorldCreator.neighborhood_house_x_spacing),
			neighborhood_road.y - WorldCreator.neighborhood_house_y_spacing,
			False, neighborhood_road)

		# Create houses south of the road
		for house in range(num_houses):
			self.create_neighborhood_house(entities, textures,
			neighborhood_road.x
				+ (house * WorldCreator.neighborhood_house_x_spacing),
			neighborhood_road.y + neighborhood_road.height
				+ WorldCreator.neighborhood_house_y_spacing
				- House.default_height,	True, neighborhood_road)

	def create_neighborhood_house(self, entities, textures, x, y, rear,
		neighborhood_road):

		# Building flipped vertically to face towards neighborhood road
		if rear:
			house = entities.add_location(LocationType.HOUSE_REAR,
				x, y, 1.0, textures)
			house.type = LocationType.HOUSE_REAR

			# Vertical sidewalk from the center of the house to the road
			self.create_sidewalk(entities, textures,
				house.x + house.width / 2 - Sidewalk.default_width / 2,
				neighborhood_road.y + neighborhood_road.height,
				house.x + house.width / 2 - Sidewalk.default_width / 2,
				house.y, True)

		else:
			house = entities.add_location(LocationType.HOUSE,
				x, y, 1.0, textures)

			# Vertical sidewalk from the center of the house to the road
			self.create_sidewalk(entities, textures,
				house.x + house.width / 2 - Sidewalk.default_width / 2,
				house.y + house.height,
				house.x + house.width / 2 - Sidewalk.default_width / 2,
				neighborhood_road.y, True)

	def create_vehicles(self, entities, textures):
		for location in entities.locations:
			if location.type == LocationType.HOUSE\
			and location != self.player_house:
				# 50% chance of the house having a car on the street:
				if random.randrange(0, 100) < 50:
					entities.add_item(ItemType.VEHICLE,	location.x
					+ location.width - Vehicle.default_width, location.y
					+ WorldCreator.neighborhood_house_y_spacing, textures)

	def create_sidewalk(self, entities, textures, start_x, start_y,
		end_x, end_y, vertical):
		
		if vertical:
			width = Sidewalk.default_width
			height = abs(start_y - end_y)
		else:
			width = abs(start_x - end_x)
			height = Sidewalk.default_width

		return entities.add_map_element(MapElementType.SIDEWALK,
			start_x, start_y, width, height, textures)

	def create_town_center(self, entities, textures):
		# Create gas station to the left of the intersection of the middle
		# road and the town center road
		self.create_gas_station(entities, textures,
			self.middle_road.x - GasStation.default_width
				- WorldCreator.store_distance_from_road,
			self.town_center_road.y - GasStation.default_height_with_dispensers
				- WorldCreator.store_distance_from_road)

		# Create grocery store to the right of the intersection of the middle
		# road and the town center road
		self.create_grocery_store(entities, textures,
			self.middle_road.x + self.middle_road.width
				+ WorldCreator.store_distance_from_road,
			self.town_center_road.y - GroceryStore.default_height
				- WorldCreator.store_distance_from_road)

	def create_park(self, entities, textures):
		pass

	def create_grocery_store(self, entities, textures, x, y):
		grocery_store = entities.add_location(LocationType.GROCERY_STORE, x, y,
			1.0, textures)

		# Entrances on the left and right
		entrance = self.create_double_door(entities, textures,
			grocery_store.x + Door.default_width,
			grocery_store.y + grocery_store.height, grocery_store)

		self.create_double_door(entities, textures,
			grocery_store.x + grocery_store.width - Door.default_width * 3,
			grocery_store.y + grocery_store.height, grocery_store)
		
		grocery_store.entrance_x = entrance.x + entrance.width / 2
		grocery_store.entrance_y = entrance.y

		# Parking lot on bottom that extends to the middle street
		self.create_parking_lot(entities, textures,
			grocery_store.x - WorldCreator.store_distance_from_road
				+ Sidewalk.default_width,
			grocery_store.y + grocery_store.height,
			grocery_store.x + grocery_store.width
				+ WorldCreator.store_distance_from_road
				- Sidewalk.default_width,
			self.town_center_road.y - Sidewalk.default_width)

		# Shopping carts near left entrance
		self.add_shopping_carts(entities, textures, grocery_store)

		# Self-checkout registers on the bottom center
		self.add_self_checkouts(entities, textures, grocery_store)

		self.add_aisles(entities, textures, grocery_store,
			GroceryStore.default_num_aisles, GroceryStore.aisle_length)

		# Add larger grocery aisle on right end
		self.generate_aisle(entities, textures,	grocery_store.x
			+ grocery_store.width - Supply.default_width, grocery_store.y
			+ GroceryStore.aisle_spacing, GroceryStore.aisle_length,
			AisleType.GROCERIES, 100, False)

		# Add stockroom supplies
		grocery_store.stockroom = self.create_stock(entities, textures)

		# Add stockers
		entities.add_character(CharacterType.STOCKER, grocery_store.entrance_x,
			grocery_store.y, 'Stocker', textures)
		entities.add_character(CharacterType.STOCKER, grocery_store.entrance_x,
			grocery_store.y, 'Stocker', textures)

	def add_shopping_carts(self, entities, textures, grocery_store):
		for cart in range(GroceryStore.default_num_carts):
			entities.add_item(
				ItemType.SHOPPING_CART,
				grocery_store.x + ShoppingCart.x_spacing,
				grocery_store.y + grocery_store.height
				- ShoppingCart.y_spacing * (cart + 1),
				textures).angle = 90.0

	def add_self_checkouts(self, entities, textures, store):
		if store.type == LocationType.GAS_STATION:
			entities.add_item(ItemType.SELF_CHECKOUT, store.x + store.width / 2,
				store.y + store.height - SelfCheckout.default_height, textures)
			return

		for checkout in range(GroceryStore.default_num_registers):
			entities.add_item(
				ItemType.SELF_CHECKOUT,
				store.x + store.width / 3
				+ checkout * SelfCheckout.x_spacing,
				store.y + store.height
				- SelfCheckout.y_spacing, textures)

	def add_aisles(self, entities, textures, store, num_aisles, length):
		aisle_x = store.x

		for aisle in range(num_aisles):
			aisle_type = self.get_aisle_type()
			aisle_density = random.randrange(0, 100)

			# Last aisle should always be a grocery aisle
			if aisle == num_aisles - 1:
				aisle_type = AisleType.GROCERIES

			self.generate_aisle(entities, textures,	aisle_x,
				store.y + GroceryStore.aisle_spacing, length, aisle_type,
				aisle_density, False)

			# Grocery stores have double aisles with larger center aisle
			if store.type == LocationType.GROCERY_STORE\
			and aisle != num_aisles - 1:
				self.generate_aisle(entities, textures,	aisle_x
					+ GroceryStore.aisle_spacing,
					store.y + GroceryStore.aisle_spacing,
					length, aisle_type, aisle_density, True)

				aisle_x += GroceryStore.aisle_spacing\
					+ Supply.default_width * 1.5

			# Gas stations only have one aisle
			elif store.type == LocationType.GAS_STATION:
				aisle_x += GroceryStore.aisle_spacing

	def get_aisle_type(self):
		random_aisle_type = random.randrange(0, 3)

		# Decrease probability for toiletry and pet supply aisles
		if random_aisle_type == AisleType.TOILETRIES:
			if random.randrange(0, 100) < 30:
				random_aisle_type -= 1
		if random_aisle_type == AisleType.PET_SUPPLIES:
			if random.randrange(0, 100) < 60:
				random_aisle_type -= 1

		return random_aisle_type

	def generate_aisle(self, entities, textures, x, y, length, type, density,
		center_aisle = False):

		# Types of supplies to place in aisle
		valid_supply_types = []

		# Determine valid supplies depending on aisle type
		if type == AisleType.GROCERIES:
			valid_supply_types.append(SupplyType.FOOD)
		elif type == AisleType.TOILETRIES:
			valid_supply_types.append(SupplyType.SOAP)
			valid_supply_types.append(SupplyType.HAND_SANITIZER)
			valid_supply_types.append(SupplyType.TOILET_PAPER)
			valid_supply_types.append(SupplyType.MASK)
		elif type == AisleType.PET_SUPPLIES:
			valid_supply_types.append(SupplyType.PET_SUPPLIES)

		# Center aisles are wider
		if center_aisle:
			width = Supply.default_width * 1.5
		else:
			width = Supply.default_width

		# Minimum spacing between supplies
		min_spacing = Supply.default_height * 1.5

		# Maximum number of supplies for the aisle
		max_num_supplies = int(length / (Supply.default_height + min_spacing))

		for supply in range(max_num_supplies):
			# Decide whether to add supply based on density
			if random.randrange(0, 100) > density:
				continue

			# Pick random supply from valid supplies
			supply_type = valid_supply_types[
				random.randrange(0, len(valid_supply_types))]

			entities.add_supply(supply_type, x, y + supply\
				* min_spacing, textures)

		aisle = entities.add_map_element(MapElementType.AISLE, x, y, width,
			length, textures)
		aisle.supplies = type

		return aisle
		
	# Randomly creates a list of supplies for the stockroom of a store
	def create_stock(self, entities, textures):
		stock = []

		for supply in range(GroceryStore.default_stockroom_size):
			stock.append(entities.add_supply(
				random.randrange(0, SupplyType.PET_SUPPLIES),
				-1000000, # out of map
				-1000000, # out of map
				textures))

		return stock

	def create_gas_station(self, entities, textures, x, y):
		gas_station = entities.add_location(LocationType.GAS_STATION, x, y,
			1.0, textures)

		# Entrance on the left
		entrance = self.create_double_door(entities, textures,
			gas_station.x + Door.default_width,
			gas_station.y + gas_station.height, gas_station)
		gas_station.entrance_x = entrance.x
		gas_station.entrance_y = entrance.y
		
		# Parking lot on the bottom that extends to the middle street
		self.create_parking_lot(entities, textures,
			gas_station.x - WorldCreator.store_distance_from_road
			+ Sidewalk.default_width,
			gas_station.y + gas_station.height,
			gas_station.x + gas_station.width
			+ WorldCreator.store_distance_from_road
			- Sidewalk.default_width,
			self.town_center_road.y - Sidewalk.default_width)

		# Fuel dispensers on the bottom
		for fuel_dispenser in range(GasStation.default_num_dispensers):
			entities.add_item(ItemType.FUEL_DISPENSER,
				gas_station.x + fuel_dispenser * GasStation.dispenser_x_spacing,
				gas_station.y + gas_station.height
				+ GasStation.dispenser_y_spacing, textures)

		# Self-checkout registers on the bottom center
		self.add_self_checkouts(entities, textures, gas_station)

		self.add_aisles(entities, textures, gas_station,
			GasStation.default_num_aisles, GasStation.aisle_length)

		# Add stockroom supplies
		gas_station.stockroom = self.create_stock(entities, textures)

		# Add stockers
		entities.add_character(CharacterType.STOCKER, gas_station.entrance_x,
			gas_station.y, 'Stocker', textures)

	def create_double_door(self, entities, textures, x, y, store):
		left_door = entities.add_item(ItemType.DOOR, x + Door.default_width,
			y - Door.default_height / 2, textures)
		right_door = entities.add_item(ItemType.DOOR, x,
			y - Door.default_height / 2, textures)

		store.doors.append(left_door)
		store.doors.append(right_door)
		return right_door
		
	def create_parking_lot(self, entities, textures, start_x, start_y,
		end_x, end_y):

		return entities.add_map_element(
			MapElementType.PARKING_LOT,
			start_x,
			start_y,
			abs(start_x - end_x),
			abs(start_y - end_y),
			textures)

	# Randomly picks a house for the player
	def pick_player_house(self, entities):
		houses = []

		for location in entities.locations:
			if location.type == LocationType.HOUSE:
				houses.append(location)

		random_index = random.randrange(0, len(houses) - 1)
		return houses[random_index]

	# Places player in the center of the player's house
	def place_player_in_house(self, player):
		player.x = self.player_house.x + self.player_house.width / 2
		player.y = self.player_house.y + self.player_house.height / 2
	
	# Populates the player's house with items
	def create_player_house(self, entities, textures):
		# Entrance at the bottom center
		entities.add_item(ItemType.DOOR,
			self.player_house.x + self.player_house.width / 2
			- Door.default_width / 2,
			self.player_house.y + self.player_house.height\
			- Door.default_height / 2, textures)

		# Vehicle parked on the street
		vehicle = entities.add_item(ItemType.VEHICLE,
			self.player_house.x, self.player_house.y
				+ WorldCreator.neighborhood_house_y_spacing, textures)
		vehicle.belongs_to_player = True

		# Kitchen with sink and counter on top left corner
		kitchen = entities.add_item(ItemType.KITCHEN,
			self.player_house.x, self.player_house.y, textures)
		sink = entities.add_item(ItemType.SINK, kitchen.x + kitchen.width,
			self.player_house.y, textures)
		entities.add_map_element(MapElementType.COUNTER, sink.x + sink.width,
			self.player_house.y, Counter.default_width, sink.height, textures)

		# Closet on right center
		entities.add_item(ItemType.CLOSET, self.player_house.x
			+ self.player_house.width - Closet.default_width,
			self.player_house.y + self.player_house.height / 2, textures)

		# Desk with computer on left center
		desk = entities.add_map_element(MapElementType.DESK,
			self.player_house.x, self.player_house.y + self.player_house.height
			/ 2, Desk.default_width, Desk.default_height, textures)
		entities.add_item(ItemType.COMPUTER, desk.x, desk.y, textures)

		# Bed on right corner
		entities.add_item(ItemType.BED, self.player_house.x
			- Bed.default_width * 2 + self.player_house.width,
			self.player_house.y, textures)

		# Dog nearby the desk
		entities.player.pet = entities.add_character(CharacterType.PET,
			self.player_house.x	+ self.player_house.width * 0.25,
			self.player_house.y + self.player_house.height * 0.75,
			'Dog', textures)