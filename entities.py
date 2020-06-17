import pygame, math

from enums import TextureType, LocationType, ItemType, SupplyType, PetType
from locations import Location, House, GroceryStore
from player import Player
from items import Item, Vehicle, Sink, ShoppingCart
from npcs import Character, Pet

# Contains all entities
class Entities:
	def __init__(self):
		self.player = Player()

		# TO DO: add lists locations, characters, pets, and supplies

		self.locations = []
		self.items = []
		self.characters = []

	# Add Methods:

	# Creates and adds new location of parameter type
	def add_location(self, type, x, y, width, height, texture):
		# TO DO: turn this into an abstract factory
		if type == LocationType.HOUSE:
			location = House(x, y, width, height,
				pygame.transform.scale(texture, (width, height)))
		elif type == LocationType.GROCERY_STORE:
			location = GroceryStore(x, y, width, height,
				pygame.transform.scale(texture, (width, height)))
		else:
			return

		self.locations.append(location)
		print("[Info] Created location " + str(type) + " at (" + str(x) + ", " + str(y) + ")")

	# Creates and adds new item of parameter type
	def add_item(self, type, x, y, texture):
		# TO DO: turn this into an abstract factory
		if type == ItemType.VEHICLE:
			item = Vehicle(x, y, pygame.transform.scale(texture, 
				(Vehicle.default_width, Vehicle.default_height)))
		elif type == ItemType.SINK:
			item = Sink(x, y, pygame.transform.scale(texture, 
				(Sink.default_width, Sink.default_height)))
		elif type == ItemType.SHOPPING_CART:
			item = ShoppingCart(x, y, pygame.transform.scale(texture, 
				(ShoppingCart.default_width, ShoppingCart.default_height)))
		else:
			return
		
		self.items.append(item)
		print("[Info] Created item " + str(type) + " at (" + str(x) + ", " + str(y) + ")")

	# Creates and adds new supply of parameter type
	def add_supply(self, type, x, y, textures):
		# TO DO: turn this into an abstract factory
		if type == SupplyType.FOOD:
			supply = Supply(x, y, pygame.transform.scale(textures.get(TextureType.FOOD), 
					(Supply.default_width, Supply.default_height)))
		elif type == SupplyType.SOAP:
			supply = Supply(x, y, pygame.transform.scale(textures.get(TextureType.SOAP), 
					(Supply.default_width, Supply.default_height)))
		elif type == SupplyType.HAND_SANITIZER:
			supply = Supply(x, y, pygame.transform.scale(textures.get(TextureType.HAND_SANITIZER), 
					(Supply.default_width, Supply.default_height)))
		elif type == SupplyType.TOILET_PAPER:
			supply = Supply(x, y, pygame.transform.scale(textures.get(TextureType.TOILET_PAPER), 
					(Supply.default_width, Supply.default_height)))
		elif type == SupplyType.MASK:
			supply = Supply(x, y, pygame.transform.scale(textures.get(TextureType.MASKS), 
					(Supply.default_width, Supply.default_height)))
		elif type == SupplyType.PET_SUPPLIES:
			supply = Supply(x, y, pygame.transform.scale(textures.get(TextureType.PET_SUPPLIES), 
					(Supply.default_width, Supply.default_height)))
		else:
			return

		self.items.append(supply)
		print("[Info] Created supply " + str(type) + " at (" + str(x) + ", " + str(y) + ")")

	# Creates and adds new pet of parameter type
	def add_pet(self, type, x, y, texture):
		# TO DO: turn this into an abstract factory
		if type == PetType.DOG:
			pet = Pet(x, y, pygame.transform.scale(texture, 
				(Pet.default_width, Pet.default_height)))
			pet.name = "Dog"
		else:
			return

		self.characters.append(pet)
		print("[Info] Created pet " + str(type) + " at (" + str(x) + ", " + str(y) + ")")

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
		self.add_house(entities, textures)
		self.add_grocery_store(entities, textures)
		self.add_other_items(entities, textures)

	# Adds house with sink
	def add_house(self, entities, textures):
		house_width = 750
		house_height = 500
		house_x = -house_width / 2
		house_y = -house_height / 2
		entities.add_location(
			LocationType.HOUSE,
			house_x,
			house_y,
			house_width,
			house_height,
			textures.get(TextureType.HOUSE))

		# Add sink
		sink_x = house_x + house_width / 2
		sink_y = house_y + house_height - 40
		entities.add_item(
			ItemType.SINK,
			sink_x,
			sink_y,
			textures.get(TextureType.SINK))

		# Add pet
		pet_x = house_x + house_width / 2
		pet_y = house_y + house_height / 3
		entities.add_pet(
			PetType.DOG,
			pet_x,
			pet_y,
			textures.get(TextureType.DOG))
	
	# Adds grocery store with shopping cart
	def add_grocery_store(self, entities, textures):
		store_x = 3000
		store_y = 500
		store_width = 2000
		store_height = 2000
		entities.add_location(
			LocationType.GROCERY_STORE,
			store_x,
			store_y,
			store_width,
			store_height,
			textures.get(TextureType.STORE))
		
		# Add shopping carts
		entities.add_item(
			ItemType.SHOPPING_CART,
			store_x + store_width / 2,
			store_y + store_height / 2,
			textures.get(TextureType.SHOPPING_CART))

		# Add shopping cart near house for testing purposes
		entities.add_item(
			ItemType.SHOPPING_CART,
			250,
			400,
			textures.get(TextureType.SHOPPING_CART))

	# Adds vehicles
	def add_other_items(self, entities, textures):
		vehicle_x = 700
		vehicle_y = 100
		entities.add_item(
			ItemType.VEHICLE,
			vehicle_x,
			vehicle_y,
			textures.get(TextureType.VEHICLE))