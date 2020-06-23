import sys
import sdl2
import sdl2.sdlimage
import sdl2.sdlttf

from enums import TextureType
from tkinter import Tk

class Renderer:
	splash_screen_display_time = 2000 # ms

	# Initializes SDL2, window, and camera
	def __init__(self):
		
		# Auto size window for screen
		root = Tk()
		self.screen_width = root.winfo_screenwidth() - 10
		self.screen_height = root.winfo_screenheight() - 100

		sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO)
		sdl2.sdlttf.TTF_Init()

		self.window = sdl2.SDL_CreateWindow(b'COVID Simulator',
			sdl2.SDL_WINDOWPOS_UNDEFINED, sdl2.SDL_WINDOWPOS_UNDEFINED,
			self.screen_width, self.screen_height, sdl2.SDL_WINDOW_SHOWN)
		sdl2.SDL_SetWindowResizable(self.window, sdl2.SDL_TRUE)

		self.sdl_renderer = sdl2.SDL_CreateRenderer(
			self.window, -1, sdl2.SDL_RENDERER_ACCELERATED)
		sdl2.SDL_RenderSetIntegerScale(self.sdl_renderer, sdl2.SDL_FALSE)
		sdl2.SDL_SetHint(sdl2.SDL_HINT_RENDER_SCALE_QUALITY, b'0')

		self.camera = Camera()

	def render(self, entities, textures, user_interface, screen_dimensions):
		# Update screen dimensions if necessary
		if self.screen_width != screen_dimensions[0]:
			self.screen_width = screen_dimensions[0]
			sdl2.SDL_SetWindowSize(self.window,
				self.screen_width, self.screen_height)
		if self.screen_height != screen_dimensions[1]:
			self.screen_height = screen_dimensions[1]
			sdl2.SDL_SetWindowSize(self.window,
				self.screen_width, self.screen_height)
			
		sdl2.SDL_RenderClear(self.sdl_renderer)
		sdl2.SDL_SetRenderDrawColor(self.sdl_renderer, 53, 69, 52, 255)
		
		# Update camera position
		self.camera.scroll(
			self.screen_width,
			self.screen_height,
			entities.player.x,
			entities.player.y,
			entities.player.width,
			entities.player.height)

		self.render_background(entities, textures)

		# Render entities:

		for location in entities.locations:
			if self.camera.within_view(location,\
			self.screen_width, self.screen_height):
				location.render(
					self.sdl_renderer,
					self.camera.x,
					self.camera.y)

		for map_element in entities.map_elements:
			if self.camera.within_view(map_element,\
			self.screen_width, self.screen_height):
				map_element.render(
					self.sdl_renderer,
					self.camera.x,
					self.camera.y)

		for character in entities.characters:
			if self.camera.within_view(character,\
			self.screen_width, self.screen_height):
				character.render(
					self.sdl_renderer,
					self.camera.x,
					self.camera.y)

		for item in entities.items:
			if self.camera.within_view(item,\
			self.screen_width, self.screen_height):
				item.render(
					self.sdl_renderer,
					self.camera.x,
					self.camera.y)

		# Render facades
		for location in entities.locations:
			if self.camera.within_view(location,\
			self.screen_width, self.screen_height):
				location.facade.render(
					self.sdl_renderer,
					self.camera.x,
					self.camera.y)

		# Render player:
		entities.player.render(self.sdl_renderer, self.camera.x, self.camera.y)

		# Render item player is carrying if applicable
		if entities.player.item_being_carried != None:
			entities.player.item_being_carried.render(
				self.sdl_renderer,
				self.camera.x,
				self.camera.y)

		# Render user interface:
		user_interface.render(self.sdl_renderer,
			self.screen_width, self.screen_height)

		# Update the window
		sdl2.SDL_RenderPresent(self.sdl_renderer)

	def render_background(self, entities, textures):
		sdl2.SDL_RenderCopy(self.sdl_renderer, textures.get(TextureType.GRASS),
			None, sdl2.SDL_Rect(
			int(entities.map_rectangle[0] - self.camera.x),
			int(entities.map_rectangle[1] - self.camera.y),
			entities.map_rectangle[2],
			entities.map_rectangle[3]))

	def render_splash_screen(self, textures):
		sdl2.SDL_RenderClear(self.sdl_renderer)
		sdl2.SDL_RenderCopy(self.sdl_renderer,
			textures.get(TextureType.SPLASH_SCREEN), None, None)
		sdl2.SDL_RenderPresent(self.sdl_renderer)

	# Quits SDL subsystems
	def close(self):
		sdl2.SDL_DestroyWindow(self.window)
		sdl2.SDL_DestroyRenderer(self.sdl_renderer)
		sdl2.sdlttf.TTF_Quit()
		sdl2.SDL_Quit()

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

	# Returns true if the entity is within the view
	# of the camera, false otherwise
	def within_view(self, entity, screen_width, screen_height):
		if self.y + screen_height <= entity.y:
			return False
		if self.y >= entity.y + entity.height:
			return False
		if self.x + screen_width <= entity.x:
			return False
		if self.x >= entity.x + entity.width:
			return False
		return True

class Textures:
	def __init__(self):
		# Maps texture type to SDL texture
		# <int, SDL texture>
		self.textures = {}

	# Returns the texture corresponding to the texture type
	# TO DO: catch exception if texture type does not exist
	def get(self, texture_type):
		return self.textures.get(texture_type)

	# Creates SDL texture from PNG file
	def create(self, renderer, filename):
		return sdl2.sdlimage.IMG_LoadTexture(renderer, filename)

	# Loads all textures into dictionary from files
	def load(self, renderer):
		# Player
		self.textures[TextureType.PLAYER] = self.create(
			renderer, b'textures/player.png')

		# Characters
		self.textures[TextureType.CIVILIAN] = self.create(
			renderer, b'textures/civilian.png')
		self.textures[TextureType.STOCKER] = self.create(
			renderer, b'textures/stocker.png')

		# Locations
		self.textures[TextureType.HOUSE_INTERIOR] = self.create(
			renderer, b'textures/house_interior.png')
		self.textures[TextureType.GROCERY_STORE_INTERIOR] = self.create(
			renderer, b'textures/grocery_store_interior.png')
		self.textures[TextureType.GAS_STATION_INTERIOR] = self.create(
			renderer, b'textures/gas_station_interior.png')
		self.textures[TextureType.HOUSE_EXTERIOR] = self.create(
			renderer, b'textures/house_exterior.png')
		self.textures[TextureType.HOUSE_EXTERIOR_REAR] = self.create(
			renderer, b'textures/house_exterior_rear.png')
		self.textures[TextureType.GROCERY_STORE_EXTERIOR] = self.create(
			renderer, b'textures/grocery_store_exterior.png')
		self.textures[TextureType.GAS_STATION_EXTERIOR] = self.create(
			renderer, b'textures/gas_station_exterior.png')

		# Supplies
		self.textures[TextureType.FOOD] = self.create(
			renderer, b'textures/food.png')
		self.textures[TextureType.SOAP] = self.create(
			renderer, b'textures/soap.png')
		self.textures[TextureType.HAND_SANITIZER] = self.create(
			renderer, b'textures/hand_sanitizer.png')
		self.textures[TextureType.TOILET_PAPER] = self.create(
			renderer, b'textures/toilet_paper.png')
		self.textures[TextureType.MASK] = self.create(
			renderer, b'textures/mask.png')
		self.textures[TextureType.PET_SUPPLIES] = self.create(
			renderer, b'textures/pet_supplies.png')

		# Items
		self.textures[TextureType.VEHICLE] = self.create(
			renderer, b'textures/vehicle.png')
		self.textures[TextureType.SINK] = self.create(
			renderer, b'textures/sink.png')
		self.textures[TextureType.KITCHEN] = self.create(
			renderer, b'textures/kitchen.png')
		self.textures[TextureType.BED] = self.create(
			renderer, b'textures/bed.png')
		self.textures[TextureType.COMPUTER] = self.create(
			renderer, b'textures/computer.png')
		self.textures[TextureType.SHOPPING_CART] = self.create(
			renderer, b'textures/cart.png')
		self.textures[TextureType.DOOR] = self.create(
			renderer, b'textures/door.png')
		self.textures[TextureType.SELF_CHECKOUT] = self.create(
			renderer, b'textures/self_checkout.png')
		self.textures[TextureType.CLOSET] = self.create(
			renderer, b'textures/closet.png')
		self.textures[TextureType.FUEL_DISPENSER] = self.create(
			renderer, b'textures/fuel_dispenser.png')

		# Pets
		self.textures[TextureType.DOG] = self.create(
			renderer, b'textures/dog.png')

		# Map Elements
		self.textures[TextureType.AISLE] = self.create(
			renderer, b'textures/aisle.png')
		self.textures[TextureType.ROAD] = self.create(
			renderer, b'textures/road.png')
		self.textures[TextureType.SIDEWALK] = self.create(
			renderer, b'textures/sidewalk.png')
		self.textures[TextureType.DRIVEWAY] = self.create(
			renderer, b'textures/driveway.png')
		self.textures[TextureType.PARKING_LOT] = self.create(
			renderer, b'textures/parking_lot.png')
		self.textures[TextureType.COUNTER] = self.create(
			renderer, b'textures/counter.png')
		self.textures[TextureType.DESK] = self.create(
			renderer, b'textures/desk.png')

		# World
		self.textures[TextureType.GRASS] = self.create(
			renderer, b'textures/grass.png')

		# User Interface
		self.textures[TextureType.SPLASH_SCREEN] = self.create(
			renderer, b'textures/splash_screen.jpg')

	# Frees textures
	def unload(self):
		for texture in self.textures:
			sdl2.SDL_DestroyTexture(self.textures[texture])
