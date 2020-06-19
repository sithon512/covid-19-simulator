import pygame, random

from entity import Entity, MovableEntity
from locations import GroceryStore
from enums import CharacterType, MapElementType, LocationType, ItemType, SupplyType, AisleType

# Similar to Item, but also has abstract update function

class Character(MovableEntity):
	# Minimum time between interact actions
	action_interval = 500 # ms

	def __init__(self, x, y, width, height, texture, type, name, interaction_message, speed):
		MovableEntity.__init__(self, x, y, width, height, texture, speed)
		self.type = type

		self.name = name
		self.interaction_message = interaction_message

		# Last time the player interacted with the character: ms
		self.last_interaction = pygame.time.get_ticks()

	# Default method:
	# Block player movement if moving towards the character
	def handle_collision(self, player):
		if (player.x > self.x and player.x_velocity < 0):
			player.block_movement()
		if (player.x < self.x and player.x_velocity > 0):
			player.block_movement()
		if (player.y > self.y and player.y_velocity < 0):
			player.block_movement()
		if (player.y < self.y and player.y_velocity > 0):
			player.block_movement()

	# Abstract method:
	# What happens when the player interacts with this character
	def handle_interaction(self, player, messages):
		pass

	# Abstract method:
	# What the character does each frame
	def update(self, entities):
		pass

	# Same as Item.check_action_interval()
	def check_action_interval(self):
		return pygame.time.get_ticks() - self.last_interaction > Character.action_interval

class Pet(Character):
	# Default values:

	# Dimensions
	default_width = 75 # px
	default_height = 25 # px

	# Maximum speed
	default_speed = 100 # px

	interaction_message = 'pet (E)'

	# Interval that the player can pet the animal
	pet_interval = 5000 # ms

	# Amount that player's morale increases after petting
	petting_morale_boost = 1

	def __init__(self, x, y, name, texture):
		Character.__init__(self, x, y, Pet.default_width, Pet.default_height,
			texture, CharacterType.PET, name, Pet.interaction_message, Pet.default_speed)

		# Last time the player pet the animal
		self.last_pet = 0

	def handle_collision(self, player):
		Character.handle_collision(self, player)

	# TO DO: add petting
	def handle_interaction(self, player, messages):
		if not self.check_action_interval():
			return
		self.last_interaction = pygame.time.get_ticks()

		if pygame.time.get_ticks() - self.last_pet > Pet.pet_interval:
			player.morale += Pet.petting_morale_boost
			self.last_pet = pygame.time.get_ticks()
			messages.append('Morale increased from petting ' + self.name.lower())
		# Pet ability needs to cooldown
		else:
			messages.append('Already performed this action recently')
			return

	# TO DO: ???
	def update(self, entities):
		pass

# Abstract class for civilian types
class Civilian(Character):
	# Default values:

	# Dimensions
	default_width = 50 # px
	default_height = 50 # px

	# Maximum speed
	default_speed = 100 # px

	interaction_message = 'interact (E)'
	
	# TO DO: implement personality later
	def __init__(self, x, y, name, texture, personality = None):
		Character.__init__(self, x, y, Civilian.default_width, Civilian.default_height,
			texture, CharacterType.PET, name, Civilian.interaction_message, Civilian.default_speed)

	def handle_collision(self, player):
		Character.handle_collision(self, player)
		
	# Abstract method
	def handle_interaction(self, player, messages):
		pass

	# Abstract method
	def update(self, entities):
		pass

class Shopper(Civilian):
	def __init__(self, x, y, name, texture, personality = None):
		Civilian.__init__(self, x, y, name, texture, personality)

		# States:
		# Shopper is at the entrance of the store and just started shopping
		self.at_entrance = True

		# Shopper is at the center corridor of the store, looking for the target aisle
		self.at_center = False

		# Shopper is at the end of the center corridor and could not find the target aisle
		self.at_store_end = False

		# Shopper is the target aisle, looking for the target item
		self.at_aisle = False

		# Shopper is at the end of the aisle and could not find the target item
		self.at_aisle_end = False

		# Shopper found the target item and is picking it up
		self.at_item = False

		# Shopper found a door and is exiting the store
		self.at_exit = False

		# Item the shopper is currently holding
		self.item_being_carried = None

		self.aisle_center = 0

		self.visited_aisles = []

		# Location reference that the shopper is at
		self.grocery_store = None

		# Aisle the shopper is trying find
		self.target_aisle = random.randrange(0, AisleType.PET_SUPPLIES)
		
		# Item the shopper is trying to find
		self.target_item = self.pick_random_target_item()

	def handle_collision(self, player):
		Character.handle_collision(self, player)
		
	# Abstract method
	def handle_interaction(self, player, messages):
		pass

	def update(self, entities):
		if self.grocery_store == None:
			self.grocery_store = self.attach_grocery_store(entities)

		if self.at_entrance:
			self.visited_aisles.clear()
			self.go_to_center(entities)
		elif self.at_exit:
			self.go_to_door(entities)
		elif self.at_center:
			self.go_to_aisle(entities)
		elif self.at_store_end:
			self.find_door(entities)
		elif self.at_aisle:
			self.go_to_item(entities)
		elif self.at_aisle_end:
			self.go_to_center(entities)
		elif self.at_item:
			self.pick_up_item(entities)

		if self.item_being_carried != None:
			self.item_being_carried.carry(self)

		self.update_position()

	def go_to_center(self, entities):
		self.x_velocity = 0

		if self.at_aisle_end:
			self.y_velocity = self.speed
		else:
			self.y_velocity = -self.speed

		# Check if shopper arrived at the center
		for aisle in entities.map_elements:
			if aisle.type != MapElementType.AISLE:
				continue

			# Only check aisles in this store
			if not aisle.check_collision(self.grocery_store):
				continue

			# Shopper approaching center from the top of the store
			if self.at_aisle_end and self.y > (aisle.y + aisle.height + self.height):
				self.at_entrance = False
				self.at_store_end = True
			# Shopper approaching center from the bottom of the store
			elif not self.at_aisle_end and self.y < (aisle.y + aisle.height + self.height):
				self.at_entrance = False
				self.at_center = True
			
	def go_to_aisle(self, entities):
		self.x_velocity = self.speed
		self.y_velocity = 0

		past_all_aisles = True
		for aisle in entities.map_elements:
			if aisle.type != MapElementType.AISLE:
				continue

			# Only check aisles in this store
			if not aisle.check_collision(self.grocery_store):
				continue

			# Check if shopper found the target aisle
			if aisle.supplies == self.target_aisle:
				# Check if shopper already visited this aisle
				if aisle in self.visited_aisles:
					continue

				if self.x > aisle.x + GroceryStore.min_aisle_spacing / 2:
					# Keep track of the aisles the shopper has visited
					self.visited_aisles.append(aisle)

					self.at_center = False
					self.at_aisle = True

			# Check if shopper past all aisles
			if aisle.x > self.x:
				past_all_aisles = False

		if past_all_aisles:
			self.at_center = False
			self.at_store_end = True

	def go_to_item(self, entities):
		self.x_velocity = 0
		self.y_velocity = -self.speed

		past_all_items = True
		for item in entities.items:
			# Only check supplies
			if item.type != ItemType.SUPPLY:
				continue

			# Only check items in this store
			if not item.check_collision(self.grocery_store):
				continue

			# Check if shopper past all items
			if item.y < self.y:
				past_all_items = False

			# Check if shopper found the target item
			if item.supply == self.target_item and item.x < self.x:
				if item.y + item.height > self.y + self.width / 2:
					self.at_aisle = False
					self.at_item = True
					self.aisle_center = self.x

		if past_all_items:
			self.at_aisle = False
			self.at_aisle_end = True

	def pick_up_item(self, entities):
		self.x_velocity = -self.speed
		self.y_velocity = 0

		# Shopper picked up item and is back in the center of the aisle
		if self.item_being_carried != None and self.x > self.aisle_center:
			self.at_item = False
			self.at_aisle_end = True
			return

		for item in entities.items:
			# Only check supplies
			if item.type != ItemType.SUPPLY:
				continue

			# Only check items in this store
			if not item.check_collision(self.grocery_store):
				continue

			# Check if is touching the item
			if item.check_collision(self):
				self.x_velocity = self.speed
				self.y_velocity = 0
				self.item_being_carried = item
				self.item_being_carried.being_carried = True

	def find_door(self, entities):
		self.x_velocity = -self.speed
		self.y_velocity = 0

		# Check if shopper arrived at a door
		for door in entities.items:
			if door.type != ItemType.DOOR:
				continue

			# Only check doors in this store
			if not door.check_collision(self.grocery_store):
				continue

			if abs(door.x - self.x) < door.width / 4:
				self.at_store_end = False
				self.at_exit = True

	def go_to_door(self, entities):
		self.x_velocity = 0
		self.y_velocity = self.speed

	# Sets grocery store reference to the grocery store the shopper is at
	def attach_grocery_store(self, entities):
		for store in entities.locations:
			if store.type != LocationType.GROCERY_STORE:
				continue
			if store.check_collision(self):
				return store
		return None

	# Picks a random target item depending on their target aisle type
	def pick_random_target_item(self):
		valid_supply_types = []
		
		# Determine valid supplies depending on target aisle type
		if self.target_aisle == AisleType.GROCERIES:
			valid_supply_types.append(SupplyType.FOOD)
		elif self.target_aisle == AisleType.TOILETRIES:
			valid_supply_types.append(SupplyType.SOAP)
			valid_supply_types.append(SupplyType.HAND_SANITIZER)
			valid_supply_types.append(SupplyType.TOILET_PAPER)
		elif self.target_aisle == AisleType.PET_SUPPLIES:
			valid_supply_types.append(SupplyType.PET_SUPPLIES)

		# Pick random item from valid items
		random_int = random.randrange(0, len(valid_supply_types))
		return valid_supply_types[random_int]

	# Returns str of the shopper's current state for debugging
	def get_state(self):
		if self.at_entrance:
			return 'At entrance'
		elif self.at_center:
			return 'At center'
		elif self.at_store_end:
			return 'At store end'
		elif self.at_aisle:
			return 'At aisle'
		elif self.at_aisle_end:
			return 'At aisle end'
		elif self.at_item:
			return 'At item'
		elif self.at_exit:
			return 'At exit'