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
				3000, 18000) # ms
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

class WorldCreator:
	neighborhood_length = 4000 # px
	neighborhood_height = 2000 # px
	neighborhood_house_x_spacing = 1000 # px
	neighborhood_house_y_spacing = 700 # px
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
			self.middle_road.x - WorldCreator.neighborhood_length,
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
			grocery_store.y + grocery_store.height)

		self.create_double_door(entities, textures,
			grocery_store.x + grocery_store.width - Door.default_width * 3,
			grocery_store.y + grocery_store.height)
		
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

		# Self-checkout registers on the bottom center
		self.add_self_checkouts(entities, textures, grocery_store)

	def add_shopping_carts(self, entities, textures, grocery_store):
		

	def add_self_checkouts(self, entities, textures, grocery_store):
		for checkout in range(GroceryStore.default_num_registers):
			entities.add_item(
				ItemType.SELF_CHECKOUT,
				grocery_store.x + grocery_store.width / 3
				+ checkout * SelfCheckout.x_spacing,
				grocery_store.y + grocery_store.height
				- SelfCheckout.y_spacing, textures)

	def create_gas_station(self, entities, textures, x, y):
		gas_station = entities.add_location(LocationType.GAS_STATION, x, y,
			1.0, textures)

		# Entrance on the left
		self.create_double_door(entities, textures,
			gas_station.x + Door.default_width,
			gas_station.y + gas_station.height)
		
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

	def create_double_door(self, entities, textures, x, y):
		entities.add_item(ItemType.DOOR, x + Door.default_width,
			y - Door.default_height / 2, textures)
		return entities.add_item(ItemType.DOOR, x,
			y - Door.default_height / 2, textures)
		
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
		entities.add_character(CharacterType.PET,
			self.player_house.x	+ self.player_house.width * 0.25,
			self.player_house.y + self.player_house.height * 0.75,
			'Dog', textures)