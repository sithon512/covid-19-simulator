import sdl2, random, math

from enums import (
	TextureType,
	LocationType,
	ItemType, SupplyType,
	PetType,
	CharacterType,
	AisleType,
	MapElementType
)
from entity import Entity, MovableEntity
from locations import GroceryStore
from items import Supply, Door

# Similar to Item, but also has abstract update function

class Character(MovableEntity):
	# Minimum time between interact actions
	action_interval = 500 # ms

	def __init__(self, x, y, width, height, texture, type, name, 
		interaction_message, speed):
		MovableEntity.__init__(self, x, y, width, height, texture, speed)
		self.type = type

		self.name = name
		self.interaction_message = interaction_message

		# Last time the player interacted with the character: ms
		self.last_interaction = sdl2.SDL_GetTicks()

		# If true, the controller will remove this entity from the game
		self.removed = False

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
		return sdl2.SDL_GetTicks() - self.last_interaction\
			> Character.action_interval

class Pet(Character):
	# Default values:

	# Dimensions
	default_width = 75 # px
	default_height = 50 # px

	# Maximum speed
	default_speed = 100 # px

	interaction_message = 'pet (E)'

	# Interval that the player can pet the animal
	pet_interval = 30000 # ms

	# Amount that player's morale increases after petting
	petting_morale_boost = 1

	def __init__(self, x, y, name, texture):
		Character.__init__(self, x, y, Pet.default_width, Pet.default_height,
			texture, CharacterType.PET, name, Pet.interaction_message,
			Pet.default_speed)

		# Last time the player pet the animal
		self.last_pet = -Pet.pet_interval

		# Pet's health
		self.health = 5

	def handle_collision(self, player):
		Character.handle_collision(self, player)

	def handle_interaction(self, player, messages):
		if not self.check_action_interval():
			return
		self.last_interaction = sdl2.SDL_GetTicks()

		if sdl2.SDL_GetTicks() - self.last_pet > Pet.pet_interval:
			player.morale += Pet.petting_morale_boost
			self.last_pet = sdl2.SDL_GetTicks()
			messages.append('Morale increased from petting '\
				+ self.name.lower())
		# Pet ability needs to cooldown
		else:
			messages.append('Already performed this action recently')
			return

	# TO DO: ???
	def update(self, entities):
		# Check if pet died
		if self.health <= 0:
			self.removed = True
			if self == entities.player.pet:
				entities.player.pet = None

		distance_traveled = self.update_position()
		entities.player.consumption.pet_walk_distance += distance_traveled

# Abstract class for civilian types
class Civilian(Character):
	# Default values:

	# Dimensions
	default_width = 50 # px
	default_height = 50 # px

	# Height to render the civilian
	render_height = 100 # px

	# Maximum speed
	default_speed = 100 # px

	interaction_message = 'interact (E)'
	
	# TO DO: implement personality later
	def __init__(self, x, y, name, texture, personality = None):
		Character.__init__(self, x, y, Civilian.default_width,
			Civilian.default_height, texture, CharacterType.PET, name,
			Civilian.interaction_message, Civilian.default_speed)

		# Randomly generate some attributes for variety
		
		# Dimensions +- 10%
		size = random.randrange(int(Civilian.default_width * 0.9),
			int(Civilian.default_width * 1.1))
		self.width = size
		self.height = size

		# Walking speed +- 50%
		self.speed = random.randrange(int(Civilian.default_speed * 0.5),
			int(Civilian.default_speed * 1.5))

	def handle_collision(self, player):
		Character.handle_collision(self, player)
		
	# Abstract method
	def handle_interaction(self, player, messages):
		pass

	# Abstract method
	def update(self, entities):
		pass

	# Returns the location that civilian is at
	def attach_location(self, entities):
		for location in entities.locations:
			if location.check_collision(self):
				return location
		return None

	# Renders the character at with render height
	def render(self, renderer, camera_x, camera_y):
		sdl2.SDL_RenderCopyEx(renderer, self.texture, None,
		sdl2.SDL_Rect(int(self.x - camera_x),
		int(self.y - camera_y - self.height), int(self.width),
		int(Civilian.render_height)), 0, None, sdl2.SDL_FLIP_NONE)

class Shopper(Civilian):
	# Interval that shopper may decide to do a random movement
	random_movement_interval = 20000 # ms

	# Proability that the shopper will pause or pace
	# when deciding to do a random movement
	pausing_probability = 5 # %
	pacing_probability = 25 # %

	# Maximum distance the shopper will pace
	max_pacing_distance = 1000 # px

	# Maximum amount of time the shopper will pause
	max_pausing_time = 10000 # ms

	def __init__(self, x, y, name, texture, personality = None):
		Civilian.__init__(self, x, y, name, texture, personality)

		# States:
		# Shopper is at the entrance of the store and just started shopping
		self.at_entrance = True

		# Shopper is at the center corridor of the store,
		# looking for the target aisle
		self.at_center = False

		# Shopper is at the end of the center corridor
		# and could not find the target aisle
		self.at_store_end = False

		# Shopper is the target aisle, looking for the target item
		self.at_aisle = False

		# Shopper is at the end of the aisle and could not find the target item
		self.at_aisle_end = False

		# Shopper found the target item and is picking it up
		self.at_item = False

		# Shopper found a door and is exiting the store
		self.at_exit = False

		# Shopper is standing ground
		self.pausing = False

		# Shopper is pacing
		self.pacing = False

		# Random events:

		# Time the shopper started a random movement
		# Initialized with a random value so that shopper
		# start their random events at different times
		self.random_movement_start = random.randrange(
			0, Shopper.random_movement_interval)

		# Total time the shopper is going to pause
		self.pausing_time = 0

		# Distance the shopper will pace
		self.pacing_distance = 0

		# Store:

		# Temporary variable for setting to the aisle center
		# so that the shopper can go back to it after picking up an item
		self.aisle_center = 0

		# Keeps track of the aisles the shopper has visited
		# when searching for the target item
		# so that the shopper does not visit the same aisle twice
		self.visited_aisles = []

		# Location reference that the shopper is at
		self.store = None

		# Targets:

		# Aisle the shopper is trying to find
		self.target_aisle = random.randrange(0, AisleType.PET_SUPPLIES + 1)
		
		# Item the shopper is trying to find
		self.target_item = self.pick_random_target_item()

		# Items:

		# Item the shopper is currently holding
		self.item_being_carried = None

		# Item the shopper found and is going to pick up
		self.item_to_pick_up = None

	def handle_collision(self, player):
		Character.handle_collision(self, player)
		
	# TO DO: implement later
	def handle_interaction(self, player, messages):
		pass

	# Performs actions based on the current state
	def update(self, entities):
		self.update_position()

		if self.item_being_carried != None:
			self.item_being_carried.carry(self)

		if self.store == None:
			self.store = self.attach_location(entities)

		self.random_movement()

		if self.pausing:
			self.pause()
			return
		elif self.pacing:
			self.pace(entities)
			return

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

	# Goes to the center of the store
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
			if not aisle.check_collision(self.store):
				continue

			# Shopper approaching center from the top of the store
			if self.at_aisle_end and self.y\
			> (aisle.y + aisle.height):
				self.at_entrance = False

				# Shopper has not found item yet
				if self.item_being_carried == None:
					self.at_center = True
				# Shopper is done shopping
				else:
					self.at_store_end = True
			# Shopper approaching center from the bottom of the store
			elif not self.at_aisle_end and self.y\
				< (aisle.y + aisle.height + self.height * 2):
				self.at_entrance = False
				self.at_center = True
			
	# Goes from the center of the store to the target aisle
	# and checks if the store does not have the target aisle
	def go_to_aisle(self, entities):
		self.x_velocity = self.speed
		self.y_velocity = 0

		past_all_aisles = True
		for aisle in entities.map_elements:
			if aisle.type != MapElementType.AISLE:
				continue

			# Only check aisles in this store
			if not aisle.check_collision(self.store):
				continue

			# Check if shopper found the target aisle
			if aisle.supplies == self.target_aisle:
				# Check if shopper already visited this aisle
				if aisle in self.visited_aisles:
					continue

				if self.x > aisle.x + GroceryStore.aisle_spacing / 2:
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

	# Once at the target aisle, searches for the target item
	# and checks if the aisle does not have the target item
	def go_to_item(self, entities):
		self.x_velocity = 0
		self.y_velocity = -self.speed

		past_all_items = True
		for item in entities.items:
			# Only check supplies
			if item.type != ItemType.SUPPLY:
				continue

			# Only check items in this store
			if not item.check_collision(self.store):
				continue

			# Only check items on shelves (not being carried by someone else)
			if item.being_carried:
				continue

			# Check if shopper past all items
			if item.y < self.y:
				past_all_items = False

			# Check if shopper found the target item
			if item.supply == self.target_item\
			and abs(self.x - item.x) < GroceryStore.aisle_spacing / 2:
				if item.y + item.height > self.y + self.width / 2:
					self.item_to_pick_up = item
					self.at_aisle = False
					self.at_item = True
					self.aisle_center = self.x

		if past_all_items:
			self.at_aisle = False
			self.at_aisle_end = True

	# Once at the target item, moves to the item and picks it up,
	# then moves back to the center of the aisle
	def pick_up_item(self, entities):
		if self.item_to_pick_up.x > self.x:
			self.x_velocity = self.speed
		else:
			self.x_velocity = -self.speed
		self.y_velocity = 0

		# Shopper picked up item and is back in the center of the aisle
		if self.item_being_carried != None\
			and abs(self.x - self.aisle_center) < self.width:
			self.at_item = False
			self.at_aisle_end = True
			return

		# Check if someone else picked up the item
		if self.item_being_carried == None\
		and self.item_to_pick_up.being_carried:
			self.at_item = False
			self.at_aisle_end = True
			self.item_to_pick_up = None
			return

		# Check if is touching the item
		if self.item_to_pick_up.check_collision(self):
			if self.aisle_center > self.x:
				self.x_velocity = self.speed
			else:
				self.x_velocity = -self.speed

			self.y_velocity = 0
			self.item_being_carried = self.item_to_pick_up
			self.item_being_carried.being_carried = True

	# Once at the center, searches for a door to exit the store
	def find_door(self, entities):
		# Grocery store exit door is on the right
		if self.store.type == LocationType.GROCERY_STORE:
			self.x_velocity = self.speed

		# Gas stations exit door is on the left
		elif self.store.type == LocationType.GAS_STATION:
			self.x_velocity = -self.speed

		# Shopper is at the store end, so they will have to go left regardless
		if self.at_store_end:
			self.x_velocity = -self.speed

		self.y_velocity = 0

		for door in entities.items:
			if door.type != ItemType.DOOR:
				continue

			# Only check doors in this store
			if not door.check_collision(self.store):
				continue

			# Check if shopper arrived at a door
			if abs(door.x - door.width - self.x) < self.width:
				self.at_store_end = False
				self.at_exit = True

	# Once aligned with the door on the x-axis,
	# moves down until the shopper is out of the store, then gets removed
	def go_to_door(self, entities):
		self.x_velocity = 0
		self.y_velocity = self.speed

		if self.y + self.height > self.store.y + self.store.height:
			self.removed = True

			if self.item_being_carried != None:
				self.item_being_carried.removed = True

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

	# Halts the shopper until the pausing time has passed
	def pause(self):
		if self.pausing_time < sdl2.SDL_GetTicks()\
		- self.random_movement_start:
			self.pausing = False
		else:
			self.x_velocity = 0
			self.y_velocity = 0
			self.look_to_side()
			self.last_moved = sdl2.SDL_GetTicks()

	# Make the shopper look to the left or right while holding an item
	def look_to_side(self):
		# Only makes a difference if the shopper is carrying an item
		if self.item_being_carried == None:
			return

		if self.pausing_time < Shopper.max_pausing_time / 2:
			self.x_velocity = -self.speed
			self.item_being_carried.carry(self)
			self.x_velocity = 0
		elif self.pausing_time > Shopper.max_pausing_time / 2:
			self.x_velocity = self.speed
			self.item_being_carried.carry(self)
			self.x_velocity = 0

	# Checks if the shopper is done pacing
	# and makes sure they do not pass any store boundaries
	def pace(self, entities):
		# Pacing distance has been satisfied
		if self.pacing_distance <= 0:
			self.pacing = False
			return

		# Make sure the shopper does not go to the left boundary of the store
		if self.x - self.width * 3 < self.store.x:
			self.pacing = False
			return

		# Make sure the shopper does not go to the top boundary of the store
		if self.y_velocity < 0 and self.y > self.store.y + self.width * 3:
			self.pacing = False
			return

		# Make sure the shopper does not go past the center of the store
		# by checking its distance from the store's checkout registers
		if self.at_aisle:
			for checkout in entities.items:
				if checkout.type != ItemType.SELF_CHECKOUT:
					continue

				if not checkout.check_collision(self.store):
					continue

				if self.y + self.height * 3 > checkout.y:
					self.pacing = False
					return

	# Randomly decides whether the shopper should do a random movement
	# such as pausing or pacing
	def random_movement(self):
		# Shopper is already doing a random movement
		if self.pacing or self.pausing:
			return

		# Only decide every random movement interval
		if Shopper.random_movement_interval > sdl2.SDL_GetTicks()\
		- self.random_movement_start:
			return

		# Randomly generate probability
		# Do not pause if picking up item from shelf or if at entrance/exit
		random_int = random.randrange(0, 100)
		if random_int < Shopper.pausing_probability and not self.at_item\
		and not self.at_entrance and not self.at_exit:
			self.pausing = True
			self.random_movement_start = sdl2.SDL_GetTicks()

			# Randomly generate pausing time
			self.pausing_time = random.randrange(Shopper.max_pausing_time / 4, 
				Shopper.max_pausing_time)

		# Only pace if the shopper is at an aislse or in the center
		elif random_int < Shopper.pacing_probability\
		and (self.at_aisle or self.at_center):
			self.pacing = True
			self.random_movement_start = sdl2.SDL_GetTicks()

			# Randomly generate pacing distance
			self.pacing_distance = random.randrange(
				0, Shopper.max_pacing_distance)
			self.reverse_velocity()

	# Reverses the direction of the shoppers velocity
	def reverse_velocity(self):
		if self.x_velocity > 0:
			self.x_velocity = -self.speed
		elif self.x_velocity < 0:
			self.x_velocity = self.speed
		elif self.y_velocity > 0:
			self.y_velocity = -self.speed
		elif self.y_velocity < 0:
			self.y_velocity = self.speed
		else:
			self.pacing_distance = 0

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

	# Same as MovableEntity.update_position()
	# but also updates pacing distance
	def update_position(self):
		time_elapsed = sdl2.SDL_GetTicks() - self.last_moved
		self.x += self.x_velocity * time_elapsed / 1000.0
		self.y += self.y_velocity * time_elapsed / 1000.0

		# Update pacing
		self.pacing_distance -= abs(self.x_velocity * time_elapsed / 1000.0)
		self.pacing_distance -= abs(self.y_velocity * time_elapsed / 1000.0)

		if self.movement_blocked:
			self.x -= self.x_velocity * time_elapsed / 1000.0
			self.y -= self.y_velocity * time_elapsed / 1000.0
			self.movement_blocked = False

		self.last_moved = sdl2.SDL_GetTicks()

class Stocker(Civilian):
	def __init__(self, x, y, name, texture, personality = None):
		Civilian.__init__(self, x, y, name, texture, personality)

		# States:

		# Stocker is at the entrance of the stock room
		self.at_stockroom = True

		# Stocker is at the center corridor of the store,
		# looking for the target aisle
		self.at_center = False

		# Stocker is at the end of the center corridor
		# and could not find the target aisle
		self.at_store_end = False

		# Stocker is at the target, looking for a spot to place the item
		self.at_aisle = False

		# Stocker is at the end of the aisle and could not find a spot,
		# or placed an item and is going back to the center
		self.at_aisle_end = False

		# Stocker found a spot and is placing the item
		self.at_shelf = False

		# Whether the stocker is placing the item to the left or right shelf
		self.placing_item_right = False

		# Location reference that the stocker is at
		self.store = None

		# Aisle the stocker is trying to find
		self.target_aisle = 0

		# Item the stocker is currently holding
		self.item_being_carried = None

		# Temporary variable for setting to the aisle center
		# so that the stocker can go back to it after placing an item
		self.aisle_center = 0

		# Keeps track of the aisles the stocker has visited
		# when searching for a spot so that the they do not 
		# visit the same aisle twice
		self.visited_aisles = []

	# Performs actions based on the current state
	def update(self, entities):
		self.update_position()

		if self.item_being_carried != None:
			self.item_being_carried.carry(self)

		if self.store == None:
			self.store = self.attach_location(entities)

		if self.at_store_end:
			self.go_to_stockroom(entities)
			return
		if self.at_stockroom:
			if self.item_being_carried == None:
				self.item_being_carried = self.get_item()
			self.go_to_center(entities)
		elif self.at_center:
			self.go_to_aisle(entities)
		elif self.at_aisle:
			self.at_aisle_end = False
			self.go_to_spot(entities)
		elif self.at_aisle_end:
			self.go_to_center(entities)
		elif self.at_shelf:
			self.place_item(entities)

	# 
	def go_to_center(self, entities):
		self.x_velocity = 0

		# Stocker just placed an item and needs to grab a new one
		if self.at_aisle_end:
			self.y_velocity = -self.speed
		else:
			self.y_velocity = self.speed

		# Check if stocker arrived at center
		for aisle in entities.map_elements:
			if aisle.type != MapElementType.AISLE:
				continue

			# Only check aisles in this store
			if not aisle.check_collision(self.store):
				continue

			if not self.at_aisle_end\
			and self.y + self.height * 1.5 > aisle.y:
				self.at_stockroom = False
				self.at_center = True
				return
			elif self.at_aisle_end\
			and self.y - self.height / 2 < self.store.y\
			+ GroceryStore.aisle_spacing / 2:
				self.at_stockroom = False
				self.at_center = True
				return

	#
	def go_to_aisle(self, entities):
		# If the stocker is done placing an item, go back
		# to the stockroom to get a new item
		if self.item_being_carried == None:
			self.go_to_stockroom(entities)
			return

		self.x_velocity = self.speed
		self.y_velocity = 0

		past_all_aisles = True
		for aisle in entities.map_elements:
			if aisle.type != MapElementType.AISLE:
				continue

			# Do not check middle aisles
			if aisle.width > Supply.default_width:
				continue

			# Check if the stocker already visited this aisle
			if aisle in self.visited_aisles:
				continue

			# Only check aisles in this store
			if not aisle.check_collision(self.store):
				continue

			# Check if stocker found the target aisle
			if aisle.supplies == self.target_aisle\
			and self.x > aisle.x + GroceryStore.aisle_spacing / 2:
					self.at_center = False
					self.at_aisle = True
					self.visited_aisles.append(aisle)

			# Check if stocker past all aisles
			if aisle.x > self.x:
				past_all_aisles = False

		if past_all_aisles:
			self.at_center = False
			self.at_store_end = True

	#
	def go_to_spot(self, entities):
		self.x_velocity = 0
		self.y_velocity = self.speed

		for aisle in entities.map_elements:
			if aisle.type != MapElementType.AISLE:
				continue

			# Only check aisles in this store
			if not aisle.check_collision(self.store):
				continue

			# Check if stocker past the aisle
			if self.y > aisle.y + aisle.height - self.height * 2:
				self.at_aisle = False
				self.at_aisle_end = True
				return
			else:
				break

		for item in entities.items:
			# Only check supplies
			if item.type != ItemType.SUPPLY:
				continue

			# Do not check items being carried
			if item.being_carried:
				continue

			# Only check items in this store
			if not item.check_collision(self.store):
				continue

			# Check if there is an empty spot in the aisle to place supply
			if self.y > self.store.y + GroceryStore.aisle_spacing * 1.5:
				distance = math.sqrt(abs(self.x - item.x) ** 2
					+ abs(self.y - item.y) ** 2)
				if distance < GroceryStore.aisle_spacing * 0.615:
					return
			else:
				return

		self.at_aisle = False
		self.at_shelf = True
		self.aisle_center = self.x

		# Randomly decide if placing the item on the right or left shelf
		self.placing_item_right = random.randrange(0, 2) == 1

	#
	def place_item(self, entities):
		if (self.item_being_carried != None and self.placing_item_right)\
		or (self.item_being_carried == None and not self.placing_item_right):
			self.x_velocity = self.speed
		else:
			self.x_velocity = -self.speed

		self.y_velocity = 0

		# Check if stocker placed item and is back at the center of the aisle
		if self.item_being_carried == None\
		and abs(self.x - self.aisle_center) < self.width / 2:
			self.at_shelf = False
			self.at_aisle_end = True
			return

		# Prevent stocker from placing item on top of another item
		for item in entities.items:
			if self.item_being_carried == None:
				break

			if item.type != ItemType.SUPPLY:
				continue

			if item == self.item_being_carried:
				continue

			if item.check_collision(self.item_being_carried):
				self.at_shelf = False
				self.at_aisle_end = True
				return

		for aisle in entities.map_elements:
			if aisle.type != MapElementType.AISLE:
				continue

			# Only check aisles in this store
			if not aisle.check_collision(self.store):
				continue

			# Check if stocker has reached the aisle
			if aisle.check_collision(self)\
			and self.item_being_carried != None:
				self.item_being_carried.being_carried = False
				self.item_being_carried = None

	#
	def go_to_stockroom(self, entities):
		self.x_velocity = -self.speed
		self.y_velocity = 0

		# Place item at the beginning of the stockroom list
		# so the stocker can try placing it later
		if self.at_store_end:
			self.store.stockroom.insert(0, self.item_being_carried)

			# Teleport item out of the map
			self.item_being_carried.x = -10000
			self.item_being_carried.y = -10000

			self.item_being_carried.being_carried = False
			self.item_being_carried = None
			self.at_store_end = False

		if self.item_being_carried == None\
		and self.x < self.store.x + Door.default_width * 2:
			self.item_being_carried = self.get_item()

			# No more items in the stockroom
			if self.item_being_carried == None:
				self.removed = True

			self.at_center = True
			self.at_aisle_end = False

	#
	def get_item(self):
		if len(self.store.stockroom) == 0:
			return None

		item = self.store.stockroom.pop()
		item.being_carried = True
		self.visited_aisles.clear()

		if item.supply == SupplyType.FOOD:
			self.target_aisle = AisleType.GROCERIES
		elif item.supply == SupplyType.SOAP\
		or item.supply == SupplyType.HAND_SANITIZER\
		or item.supply == SupplyType.TOILET_PAPER:
			self.target_aisle = AisleType.TOILETRIES
		elif item.supply == SupplyType.PET_SUPPLIES:
			self.target_aisle = AisleType.PET_SUPPLIES

		return item

	# Returns str of the stocker's current state for debugging
	def get_state(self):
		if self.at_stockroom:
			return 'At stockroom'
		elif self.at_center:
			return 'At center'
		elif self.at_store_end:
			return 'At store end'
		elif self.at_aisle:
			return 'At aisle'
		elif self.at_aisle_end:
			return 'At aisle end'
		elif self.at_shelf:
			return 'At shelf'