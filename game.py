import sdl2

from renderer import Renderer, Camera, Textures
from entities import Entities, Controller, WorldCreator
from ui import UserInterface, MainMenu
from enums import TextureType

class Game:
	# Parameters: starting values for money, health, and morale
	def __init__(self, money, health, morale):
		# Initialize renderer first because it starts SDL
		self.renderer = Renderer()

		self.textures = Textures()
		self.textures.load(self.renderer.sdl_renderer)

		self.user_interface = UserInterface(self.textures)
		self.controller = Controller()
		self.entities = Entities()

		self.entities.init_player(0, 0, self.textures.get(TextureType.PLAYER),
			money, health, morale)

		world_creator = WorldCreator(2)
		self.entities.map_rectangle = world_creator.create(
			self.entities, self.textures)

	def run(self):
		running = True

		# For average FPS calculation
		frames = 0
		last_frame = sdl2.SDL_GetTicks()

		# Display splash screen
		while sdl2.SDL_GetTicks() < last_frame\
		+ Renderer.splash_screen_display_time:
			self.renderer.render_splash_screen(self.textures)

		# Game loop:
		while running:
			# 1. Handle input from the user interface
			screen_dimensions = [
				self.renderer.screen_width,
				self.renderer.screen_height]
			running = self.user_interface.handle_input(
				self.controller,
				screen_dimensions)

			# 2. Update entities from the controller
			self.controller.update_entities(self.entities)
			self.controller.generate_NPCs(self.entities, self.textures)
			#if not self.controller.check_player_meters(self.entities):
			#	running = False

			# 3. Update screen from the renderer
			self.renderer.render(self.entities,	self.textures,
				self.user_interface, screen_dimensions)

			# For debugging:
			# Average FPS for performance profiling, prints every 5 seconds
			frames += 1
			if sdl2.SDL_GetTicks() - last_frame > 5000:
				print('Average FPS: ' + str(frames / 5.0))
				frames = 0
				last_frame = sdl2.SDL_GetTicks()

		self.close()

	def get_renderer(self):
		"""Returns the game renderer that was instantiated by the game class
		so that it can be used in other components that need to borrow from it.
		"""

		return self.renderer

	def get_textures(self):
		"""Returns the game textures that were instantiated by the game class
		so that they can be used by other components.
		"""
		
		return self.textures

	# Closes the game renderer
	def close(self):
		self.textures.unload()
		self.renderer.close()

# Testing:
if __name__ == '__main__':
	starting_money = 1000
	starting_health = 100
	starting_morale = 70

	# define main menu logic
	main_menu = MainMenu()
	# run the main menu, the return will be the game settings
	game_settings = main_menu.run()
	print('Selected Settings:', game_settings) # debug
	if game_settings is None:
		# if we don't have game settings, the user quit the game from the menu
		exit()

	game = Game(starting_money, starting_health, starting_morale)
	game.run()
