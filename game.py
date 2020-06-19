import pygame

from renderer import Renderer, Camera, Textures
from entities import Entities, Controller
from ui import UserInterface
from enums import TextureType

class Game:
	# Parameters: starting values for money, health, and morale
	def __init__(self, money, health, morale):
		# Initialize renderer first because it starts pygame
		self.renderer = Renderer()

		self.textures = Textures()
		self.textures.load()

		self.user_interface = UserInterface()
		self.controller = Controller()
		self.entities = Entities()

		self.entities.init_player(0, 0, self.textures.get(TextureType.PLAYER), 
			money, health, morale)

		self.controller.init_map(self.entities, self.textures)

	def run(self):
		running = True

		# For average FPS calculation
		frames = 0
		last_frame = pygame.time.get_ticks()

		# Game loop:
		while running:
			# 1. Handle input from the user interface
			screen_dimensions = [self.renderer.screen_width, self.renderer.screen_height]
			running = self.user_interface.handle_input(self.controller, screen_dimensions)

			# 2. Update entities from the controller
			self.controller.update_entities(self.entities)
			self.controller.generate_NPCs(self.entities, self.textures)	

			# 3. Update screen from the renderer
			self.renderer.render(self.entities, self.user_interface, screen_dimensions)

			# Average FPS for performance profiling, prints every 10 seconds
			frames += 1
			if pygame.time.get_ticks() - last_frame > 10000:
				print("[Debug] Average FPS: " + str(frames / 10.0))
				frames = 0
				last_frame = pygame.time.get_ticks()

		self.close()

	# Closes the game renderer
	def close(self):
		self.renderer.close()

# Testing:
starting_money = 1000
starting_health = 100
starting_morale = 70

game = Game(starting_money, starting_health, starting_morale)
game.run()
