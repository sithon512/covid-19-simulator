import sdl2, math

from entity import Entity
from enums import ItemType, PetType, InventoryType, SupplyType

class Item(Entity):
	# Minimum time between interact actions
	action_interval = 250 # ms

	def __init__(self, x = 0, y = 0, width = 0, height = 0, texture = None,
		type = 0, name = '', interaction_message = ''):

		Entity.__init__(self, x, y, width, height, texture)
		self.type = type

		self.name = name
		self.interaction_message = interaction_message

		# Last time the player interacted with the item: ms
		self.last_interaction = sdl2.SDL_GetTicks()

		# If true, the controller will remove this entity from the game
		self.removed = False

	# Default method:
	# Block player movement if moving towards the item
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
	# What happens when the player interacts with this item
	def handle_interaction(self, player, messages):
		pass

	# Returns true if the action interval has passed since the last interaction
	# Interaction must be limited because so that the player only interacts once
	# because pressing the interact button lasts more than one frame
	def check_action_interval(self):
		return sdl2.SDL_GetTicks() - self.last_interaction\
			> Item.action_interval

class Vehicle(Item):
	# Default values:

	# Dimensions
	default_width = 200 # px
	default_height = 110 # px

	# Maximum speed
	regular_speed = 500 # px / s
	turbo_speed = 1000 # px / s

	name = 'Vehicle'
	interaction_message = 'enter/exit (E)'

	# Amount of fuel the vehicle starts with
	default_fuel = 50000 # total px traveled

	def __init__(self, x, y, texture):
		Item.__init__(self, x, y, Vehicle.default_width, Vehicle.default_height,
			texture, ItemType.VEHICLE, Vehicle.name,
			Vehicle.interaction_message)

		# Whether the vehicle is attached to the player
		self.attached = False

		# Amount of distance the vehicle can travel before running out of fuel
		self.current_fuel = Vehicle.default_fuel # px

		# Gas tank capacity
		self.max_fuel = self.current_fuel

	# Adjusts vehicle to player and decreases fuel
	def drive(self, player):
		# Check fuel
		if self.current_fuel <= 0:
			self.detach(player)
			return

		x_distance = abs(self.x - player.x)
		y_distance = abs(self.y - player.y)
		self.current_fuel -= math.sqrt(x_distance ** 2 + y_distance ** 2)

		self.x = player.x
		self.y = player.y

	# Attaches vehicle to the player
	def handle_collision(self, player):
		if not self.attached:
			Item.handle_collision(self, player)
		else:
		   # Calculate vehicle angle based on the player's velocity
			if player.x_velocity > 0 and player.y_velocity == 0:
				self.angle = 0.0
			elif player.x_velocity < 0 and player.y_velocity == 0:
				self.angle = 180.0
			elif player.y_velocity > 0 and player.x_velocity == 0:
				self.angle = 90.0
			elif player.y_velocity < 0 and player.x_velocity == 0:
				self.angle = 270.0

	# Attaches or detaches vehicle to the player
	def handle_interaction(self, player, messages):
		if not self.check_action_interval():
			return
		self.last_interaction = sdl2.SDL_GetTicks()

		if not self.attached:
			self.attach(player)
			messages.append("Vehicle Fuel: "
				+ str(int(self.fuel_percentage())) + "%")
		else:
			# Do not detach player if they are interacting with a fuel dispenser
			for item in player.nearby_items:
				if item.type == ItemType.FUEL_DISPENSER:
					return
			self.detach(player)

	# Attaches player to the vehicle
	def attach(self, player):
		player.vehicle = self
		player.x = self.x
		player.y = self.y
		self.attached = True

	# Detaches player to the vehicle
	def detach(self, player):
		player.vehicle = None
		player.x = self.x - player.width
		self.attached = False

	# Returns the percentage of the fuel tank
	def fuel_percentage(self):
		return (self.current_fuel / self.max_fuel) * 100

class Sink(Item):
	# Default values:

	# Dimensions
	default_width = 60 # px
	default_height = 40 # px

	name = 'Sink'
	interaction_message = 'wash hands (E)'

	def __init__(self, x, y, texture):
		Item.__init__(self, x, y, Sink.default_width, Sink.default_height,
			texture, ItemType.SINK, Sink.name, Sink.interaction_message)

	def handle_collision(self, player):
		Item.handle_collision(self, player)

	# TO DO: add washing hands
	def handle_interaction(self, player, messages):
		if not self.check_action_interval():
			return
		self.last_interaction = sdl2.SDL_GetTicks()
		
		if player.use_supply(SupplyType.SOAP, 1):
			messages.append("Washed hands with soap")
		else:
			messages.append("No soap to wash hands with")

class ShoppingCart(Item):
	# Default values:

	# Dimensions
	default_width = 70 # px
	default_height = 40 # px

	name = 'Shopping Cart'
	interaction_message = 'place item (E) / push (Shift)'

	# Maximum number of supplies that the player
	# can place in the cart
	default_capacity = 5

	def __init__(self, x, y, texture):
		Item.__init__(self, x, y, ShoppingCart.default_width,
			ShoppingCart.default_height, texture, ItemType.SHOPPING_CART,
			ShoppingCart.name, ShoppingCart.interaction_message)

		self.items = Inventory(InventoryType.SHOPPING_CART,
			ShoppingCart.default_capacity)

		# Total cost of all items in the cart
		self.total_cost = 0.0

		# Last time the player moved the cart
		self.last_moved = sdl2.SDL_GetTicks()

	# Pushes the cart with the player's velocity if the player is running
	def handle_collision(self, player):
		# Set player's most recent shopping cart
		player.shopping_cart = self

		# If player is not running, do not push cart
		if not player.running:
			Item.handle_collision(self, player)
			return

		# Time since last move: ms
		time_elapsed = sdl2.SDL_GetTicks() - self.last_moved

		# Reset time elapsed if the player has not touched the
		# shopping cart recently
		if time_elapsed > 250:
			time_elapsed = 0
			not_touched_recently = True
		else:
			not_touched_recently = False
			
		# Calculate shopping cart angle based on the player's velocity
		# Align with player's location if the player player has not
		# touched the cart recently
		if player.x_velocity > 0 and player.y_velocity == 0: # going right
			self.angle = 0.0

			if not_touched_recently:
				self.x = player.x + player.width
				self.y = player.y
		elif player.x_velocity < 0 and player.y_velocity == 0: # going left
			self.angle = 180.0

			if not_touched_recently:
				self.x = player.x - self.width
				self.y = player.y
		elif player.y_velocity > 0 and player.x_velocity == 0: # going down
			self.angle = 90.0

			if not_touched_recently:
				self.x = player.x
				self.y = player.y + player.height
		elif player.y_velocity < 0 and player.x_velocity == 0: # going up
			self.angle = 270.0

			if not_touched_recently:
				self.x = player.x
				self.y = player.y - self.height
		
		# Similar to MovableEntity.update_position()
		self.x += player.x_velocity * time_elapsed / 1000.0
		self.y += player.y_velocity * time_elapsed / 1000.0

		self.last_moved = sdl2.SDL_GetTicks()
		
	# Place item inside
	def handle_interaction(self, player, messages):
		if not self.check_action_interval():
			return
		self.last_interaction = sdl2.SDL_GetTicks()

		if player.item_being_carried != None:
			if not self.items.add_supply(player.item_being_carried.supply):
				messages.append('Shopping cart is full')
				return
			
			self.total_cost += player.item_being_carried.price
			player.item_being_carried.removed = True
			player.item_being_carried = None
			messages.append('Item added to shopping cart')
			messages.append('Shopping cart contents: ' + str(self.items))
		else:
			messages.append('Not carrying any items')

class Supply(Item):
	# Default values:

	# Dimensions
	default_width = 30 # px
	default_height = 40 # px

	interaction_message = 'pick up / drop (E)'

	def __init__(self, x, y, width, height, texture, type, name):
		Item.__init__(self, x, y, Supply.default_width, Supply.default_height,
			texture, ItemType.SUPPLY, name, Supply.interaction_message)

		# SupplyType
		self.supply = type

		# How much money the supply costs
		self.price = 0.0

		# Whether the player is carrying the supply
		self.being_carried = False

	# TO DO: implement later
	# Generates a price based on the supply type and difficulty
	def generate_price(self, difficulty):
		self.price = 5
		self.interaction_message = Supply.interaction_message\
			+ ' - $' + str(self.price)

	# Adjusts supply to the player
	def carry(self, player):
		# Going down diagonally
		if player.x_velocity != 0 and player.y_velocity > 0:
			self.angle = math.degrees(math.atan(player.y_velocity / 
			player.x_velocity))
			self.x = player.x + player.width / 2 - self.width / 2
			self.y = player.y + player.height
		# Going up diagonally
		elif player.x_velocity != 0 and player.y_velocity < 0:
			self.angle = math.degrees(math.atan(player.y_velocity / 
			player.x_velocity))
			self.x = player.x + player.width / 2 - self.width / 2
			self.y = player.y - self.height
		# Going right
		elif player.x_velocity > 0 and player.y_velocity == 0:
			self.angle = 0.0
			self.x = player.x + player.width
			self.y = player.y - player.height / 2 + self.height / 2
		# Going left
		elif player.x_velocity < 0 and player.y_velocity == 0:
			self.angle = 180.0
			self.x = player.x - self.width
			self.y = player.y - player.height / 2 + self.height / 2
		# Going down
		elif player.y_velocity > 0 and player.x_velocity == 0:
			self.angle = 270.0
			self.x = player.x + player.width / 2 - self.width / 2
			self.y = player.y + player.height
		# Going up
		elif player.y_velocity < 0 and player.x_velocity == 0:
			self.angle = 90.0
			self.x = player.x + player.width / 2 - self.width / 2
			self.y = player.y - self.height

	def handle_collision(self, player):
		if not self.being_carried:
			Item.handle_collision(self, player)

	# Toggles whether the player is carrying the supply
	# and attaches to the player
	def handle_interaction(self, player, messages):
		if not self.check_action_interval():
			return

		if self.being_carried:
			player.item_being_carried = None
			self.being_carried = False
		else:
			player.item_being_carried = self
			self.being_carried = True

		self.last_interaction = sdl2.SDL_GetTicks()

	# Transfers supply to player's backpack if the player
	# has enough room and money for it
	def purchase_single_item(self, player, messages):
		item_cost = player.item_being_carried.price

		if player.money < item_cost:
			messages.append('Not enough money to purchase item')
			return

		if player.backpack.size + 1 > player.backpack.capacity:
			messages.append('Not enough space in backpack to transport item')
			return

		player.money -= item_cost
		player.backpack.add_supply(player.item_being_carried.supply)
		player.item_being_carried.removed = True
		player.item_being_carried = None
		messages.append('Checked out item: -$' + str(int(item_cost)))
		messages.append('Backpack contents: ' + str(player.backpack))

class Door(Item):
	# Default values:

	# Dimensions
	default_width = 80 # px
	default_height = 10 # px

	name = 'Entrance'
	interaction_message = 'enter/exit (E)'

	def __init__(self, x, y, texture):
		Item.__init__(self, x, y, Door.default_width, Door.default_height,
			texture, ItemType.DOOR, Door.name, Door.interaction_message)

	def handle_collision(self, player):
		Item.handle_collision(self, player)

	# Teleports player up or down to bypass the location's collision detection
	def handle_interaction(self, player, messages):
		if not self.check_action_interval():
			return

		# Player is below the door
		if player.y > self.y:
			player.y -= (player.height + self.height * 2)
		# Player is above the door
		elif player.y < self.y:
			player.y += (player.height + self.height * 2)

		self.last_interaction = sdl2.SDL_GetTicks()

class SelfCheckout(Item):
	# Default values:

	# Dimensions
	default_width = 100 # px
	default_height = 50 # px

	name = 'Self-checkout'
	interaction_message = 'checkout items (E)'

	def __init__(self, x, y, texture):
		Item.__init__(self, x, y, SelfCheckout.default_width,
		SelfCheckout.default_height, texture, ItemType.SELF_CHECKOUT,
		SelfCheckout.name, SelfCheckout.interaction_message)

	def handle_collision(self, player):
		Item.handle_collision(self, player)

		# Determine total price of all items in the user's cart
		if player.shopping_cart != None:
			total_cost = player.shopping_cart.total_cost
			self.interaction_message = SelfCheckout.interaction_message\
				+ ' - total cost: $' + str(int(total_cost))

	# Transfers contents of the shopping cart to the player's backpack
	# if the player has enough room and money for all items
	def handle_interaction(self, player, messages):
		if not self.check_action_interval():
			return
		self.last_interaction = sdl2.SDL_GetTicks()
		
		# Allow the player to checkout just one item if they are holding it
		if player.shopping_cart == None or player.shopping_cart.items.size == 0:
			if player.item_being_carried == None:
				messages.append('No items to check out')
				return
			else:
				player.item_being_carried.purchase_single_item(player, messages)
				return

		# Player checking out shopping cart
		total_cost = player.shopping_cart.total_cost
		if player.money < total_cost:
			messages.append('Not enough money to purchase items')
			return

		if player.backpack.size + player.shopping_cart.items.size\
		> player.backpack.capacity:
			messages.append('Not enough space in backpack to transport items')
			return

		# Transfer shopping cart items to player's backpack
		player.money -= total_cost
		player.shopping_cart.items.transfer(player.backpack)
		player.shopping_cart.total_cost = 0

		messages.append('Checked out cart: -$' + str(int(total_cost)))
		messages.append('Backpack contents: ' + str(player.backpack))

class Closet(Item):
	# Default values:

	# Dimensions
	default_width = 120 # px
	default_height = 40 # px

	name = 'Closet'
	interaction_message = 'empty out backpack (E)'

	def __init__(self, x, y, texture):
		Item.__init__(self, x, y, Closet.default_width, Closet.default_height,
			texture, ItemType.CLOSET, Closet.name, Closet.interaction_message)

	def handle_collision(self, player):
		Item.handle_collision(self, player)

	# Transfers the contents of the player's backpack to the player's
	# closet inventory
	def handle_interaction(self, player, messages):
		if not self.check_action_interval():
			return
		self.last_interaction = sdl2.SDL_GetTicks()

		if player.backpack.size == 0:
			messages.append('No items in backpack')
			messages.append('Closet contents: ' + str(player.closet))
			return
		
		if not player.backpack.transfer(player.closet):
			messages.append('Not enough room in closet')
			messages.append('Closet contents: ' + str(player.closet))
			return

		messages.append('Emptied backpack items into closet')
		messages.append('Closet contents: ' + str(player.closet))

class FuelDispenser(Item):
	# Default values:

	# Dimensions
	default_width = 100 # px
	default_height = 40 # px

	name = 'Fuel Dispenser'
	interaction_message = 'fill up car (E)'

	def __init__(self, x, y, texture):
		Item.__init__(self, x, y, FuelDispenser.default_width,
			FuelDispenser.default_height, texture, ItemType.FUEL_DISPENSER,
			FuelDispenser.name, FuelDispenser.interaction_message)
		
		self.price = 0

	def handle_collision(self, player):
		Item.handle_collision(self, player)

	# Fills up player's vehicle and subtracts money from the player accordingly
	def handle_interaction(self, player, messages):
		if not self.check_action_interval():
			return
		self.last_interaction = sdl2.SDL_GetTicks()

		if player.vehicle == None:
			messages.append('Vehicle required to fill up')
		else:
			total_cost = (player.vehicle.max_fuel - 
				player.vehicle.current_fuel) * self.price / 5000.0

			if total_cost > player.money:
				messages.append('Not enough money to fill up vehicle')
				return

			player.vehicle.current_fuel = player.vehicle.max_fuel
			messages.append('Vehicle fuel filled up: $' + str(int(total_cost)))
		
	# Sets the price of the fuel and updates interaction message
	def set_price(self, new_price):
		self.price = new_price
		self.interaction_message = FuelDispenser.interaction_message + ' - $'
		self.interaction_message += str(self.price) + ' per gallon'

class Inventory:
	# Default values:

	default_backpack_capacity = 10 # supplies
	default_closet_capacity = 100 # supplies

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

		self.supplies[supply_type] = self.supplies.get(supply_type, 0) + 1
		self.size += 1

		return True

	# Decreases quantity for the supply type
	def remove_supply(self, supply_type):
		if supply_type in self.supplies:
			self.supplies[supply_type] = self.supplies.get(supply_type) - 1
			self.size -= 1
			return True	
		else:
			return False

	# Transfers contents from inventory to another
	# Returns false if there is not enough space in the other inventory
	# Returns true if the transfer is successful
	def transfer(self, other):
		for supply in self.supplies:
			quantity = 0
			while quantity < self.supplies[supply]:
				if not other.add_supply(supply):
					return False
				quantity += 1

		# Reset supplies and cost
		self.supplies.clear()
		self.size = 0
		return True

	# Returns contents of the inventory as a str
	# Format: { supply: quantity, ... } (size / capacity)
	def __str__(self):
		if self.size == 0:
			return "empty" + ' - ' + str(self.size) + ' / ' + str(self.capacity)

		contents = '['
		for supply in self.supplies:
			contents += ' ' + SupplyType.supply_strs[supply] + ': '
			contents += str(self.supplies[supply]) + ','
		contents = contents[:-1] + ' ]'
		contents += ' - ' + str(self.size) + ' / ' + str(self.capacity)
		return contents