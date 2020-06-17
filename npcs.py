import pygame

from entity import Entity, MovableEntity
from enums import CharacterType

# Similar to Item, but also has abstract update function

class Character(Entity):
	# Minimum time between interact actions
	action_interval = 500 # ms

	def __init__(self, x, y, width, height, texture, type, name, interaction_message):
		Entity.__init__(self, x, y, width, height, texture)
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
	def update(self):
		pass

	# Same as Item.check_action_interval()
	def check_action_interval(self):
		return pygame.time.get_ticks() - self.last_interaction > Character.action_interval

class Pet(Character):
	# Default values:

	# Dimensions
	default_width = 75 # px
	default_height = 25 # px

	interaction_message = 'pet (E)'

	# Interval that the player can pet the animal
	pet_interval = 5000 # ms

	# Amount that player's morale increases after petting
	petting_morale_boost = 1

	def __init__(self, x, y, name, texture):
		# Set name later
		Character.__init__(self, x, y, Pet.default_width, Pet.default_height,
			texture, CharacterType.PET, name, Pet.interaction_message)

		# Last time the player pet the animal
		self.last_pet = pygame.time.get_ticks()

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
	def update(self):
		pass