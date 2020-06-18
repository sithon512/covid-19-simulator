import pygame

from enums import TextureType

class Renderer:
	# Initializes pygame, window, and camera
	def __init__(self):
		
		# Screen dimensions
		self.screen_width = 1280
		self.screen_height = 720

		pygame.init()

		self.window = pygame.display.set_mode(
			(self.screen_width, self.screen_height), pygame.RESIZABLE)
		pygame.display.set_caption("Covid Simulator")

		self.camera = Camera()

		# Background color
		self.background = (70, 89, 69)

	# NOTE: the order of the rendering is significant:
	# render calls later in the function are rendered on top of the previous calls
	def render(self, entities, user_interface, screen_dimensions):
		# Update screen dimensions if necessary
		if self.screen_width is not screen_dimensions[0]:
			self.screen_width = screen_dimensions[0]
			window = pygame.display.set_mode(
				(self.screen_width, self.screen_height), pygame.RESIZABLE)
		if self.screen_height is not screen_dimensions[1]:
			self.screen_height = screen_dimensions[1]
			window = pygame.display.set_mode(
				(self.screen_width, self.screen_height), pygame.RESIZABLE)

		# Clear screen
		self.window.fill(self.background)

		# Update camera position
		self.camera.scroll(
			self.screen_width,
			self.screen_height,
			entities.player.x,
			entities.player.y,
			entities.player.width,
			entities.player.height)

		# Render entities:

		for location in entities.locations:
			location.render(self.window, self.camera.x, self.camera.y)

		for map_element in entities.map_elements:
			map_element.render(self.window, self.camera.x, self.camera.y)

		for item in entities.items:
			item.render(self.window, self.camera.x, self.camera.y)

		for character in entities.characters:
			character.render(self.window, self.camera.x, self.camera.y)

		# Render player:
		entities.player.render(self.window, self.camera.x, self.camera.y)

		# Render user interface:
		user_interface.render(self.window)

		# Update the window
		pygame.display.update()

	# Quits pygame
	def close(self):
		pygame.quit()

class Camera:
	def __init__(self):
		# Position: px
		self.x = 0.0
		self.y = 0.0

	# Centers the camera's position on the player's location
	# based on the screen dimensions
	def scroll(self, screen_width, screen_height,
		x, y, width, height):
		player_center_x = x + width / 2
		player_center_y = y + height / 2

		self.x = player_center_x - screen_width / 2
		self.y = player_center_y - screen_height / 2

class Textures:
	def __init__(self):
		# Maps texture type to pygame texture
		# <int, pygame texture>
		self.textures = {}

	# Returns the texture corresponding to the texture type
	# TO DO: catch exception if texture type does not exist
	def get(self, texture_type):
		return self.textures.get(texture_type)

	# Creates pygame texture from PNG file
	def create(self, filename):
		return pygame.image.load(filename).convert_alpha()

	# Loads all textures into dictionary from files
	def load(self):
		# Player
		self.textures[TextureType.PLAYER] = self.create('textures/player.png')

		# Characters

		# Locations
		self.textures[TextureType.HOUSE] = self.create('textures/house.png')
		self.textures[TextureType.STORE] = self.create('textures/store.png')

		# Supplies
		self.textures[TextureType.FOOD] = self.create('textures/food.png')
		self.textures[TextureType.SOAP] = self.create('textures/soap.png')
		self.textures[TextureType.HAND_SANITIZER] = self.create('textures/hand_sanitizer.png')
		self.textures[TextureType.TOILET_PAPER] = self.create('textures/toilet_paper.png')
		self.textures[TextureType.MASK] = self.create('textures/mask.png')
		self.textures[TextureType.PET_SUPPLIES] = self.create('textures/pet_supplies.png')

		# Items
		self.textures[TextureType.VEHICLE] = self.create('textures/vehicle.png')
		self.textures[TextureType.SINK] = self.create('textures/sink.png')
		self.textures[TextureType.SHOPPING_CART] = self.create('textures/cart.png')

		# Pets
		self.textures[TextureType.DOG] = self.create('textures/dog.png')

		# Map Elements
		self.textures[TextureType.AISLE] = self.create('textures/aisle.png')