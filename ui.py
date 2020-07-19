import sdl2
import sdl2.ext
import sdl2.sdlttf

from ctypes import c_int, pointer

from enums import TextureType, MapElementType

class UserInterface:
	# Initializes fonts and messages
	def __init__(self, textures):
		# TO DO: implement panels later
		self.panels = []

		# Fonts of various sizes
		self.small_text = sdl2.sdlttf.TTF_OpenFont(b'cour.ttf', 14)
		self.medium_text = sdl2.sdlttf.TTF_OpenFont(b'cour.ttf', 16)
		self.large_text = sdl2.sdlttf.TTF_OpenFont(b'cour.ttf', 18)

		# Initialize message systems
		self.middle_text = MiddleText()
		self.info_text = InfoText()
		self.message_stack = MessageStack()

		self.mini_map = MiniMap(textures.get(TextureType.MINI_MAP))

		self.last_interaction = sdl2.SDL_GetTicks()

	# Handles mouse and keyboard input
	# Returns false if the user quits the game
	def handle_input(self, controller, screen_dimensions):
		events = sdl2.ext.get_events()
		for event in events:
			# User pressed 'X' button
			if event.type == sdl2.SDL_QUIT:
				return False

			if event.type == sdl2.SDL_WINDOWEVENT:
				if event.window.event == sdl2.SDL_WINDOWEVENT_SIZE_CHANGED:
					screen_dimensions[0] = event.window.data1
					screen_dimensions[1] = event.window.data2

		self.handle_keyboard(controller)

		controller.update_messages(
			self.middle_text,
			self.info_text,
			self.message_stack)

		return True

	def handle_keyboard(self, controller):
		self.handle_player_movement(controller)

	# Handles player movement with W, A, S, D / arrow keys + Shift and
	# the interact action with E
	def handle_player_movement(self, controller):
		# Gets current keys pressed
		keystate = sdl2.SDL_GetKeyboardState(None)

		# Reset movement each frame
		up = False
		down = False
		left = False
		right = False
		running = False

		# W, A, S, D and arrow keys
		# move player up, left, down, and right, respectively
		if keystate[sdl2.SDL_SCANCODE_W] or keystate[sdl2.SDL_SCANCODE_UP]:
			up = True
		if keystate[sdl2.SDL_SCANCODE_A] or keystate[sdl2.SDL_SCANCODE_LEFT]:
			left = True
		if keystate[sdl2.SDL_SCANCODE_S] or keystate[sdl2.SDL_SCANCODE_DOWN]:
			down = True
		if keystate[sdl2.SDL_SCANCODE_D] or keystate[sdl2.SDL_SCANCODE_RIGHT]:
			right = True

		# Shift key to run
		if keystate[sdl2.SDL_SCANCODE_LSHIFT]\
		or keystate[sdl2.SDL_SCANCODE_RSHIFT]:
			running = True

		# E for player interact action
		if keystate[sdl2.SDL_SCANCODE_E]:
			controller.interact_player()

		# TAB for displaying player inventory
		if keystate[sdl2.SDL_SCANCODE_TAB]:
			controller.display_inventory()
		
		controller.move_player(up, down, left, right, running)
	
	# TO DO: create methods for handling mouse click and hover

	# Renders text and panels
	def render(self, renderer, screen_width, screen_height):
		self.middle_text.render(renderer, self.small_text, self.medium_text,
			screen_width, screen_height)
		self.info_text.render(renderer, self.medium_text, screen_width)
		self.message_stack.render(renderer, self.small_text, screen_height)

	def render_mini_map(self, renderer, screen_width, screen_height,
		entities, map_rectangle):

		self.mini_map.render(renderer, screen_width, screen_height,
		entities, map_rectangle)

class MiniMap:
	# Size proportion to screen width
	proportional_to_screen_width = 0.125
	proportional_to_container = 0.95

	player_dot_size = 5
	character_dot_size = 2

	def __init__(self, texture):
		self.texture = texture
		self.size = 0
		self.x_scale = 0.0
		self.y_scale = 0.0

	def render(self, renderer, screen_width, screen_height,
		entities, map_rectangle):

		self.size = screen_width * MiniMap.proportional_to_screen_width
		self.x_scale = self.size * MiniMap.proportional_to_container\
			/ map_rectangle[2]
		self.y_scale =  self.size * MiniMap.proportional_to_container\
			/ map_rectangle[3]

		self.render_background(renderer, screen_width, screen_height)
		self.render_roads(renderer, screen_width, screen_height, entities)
		self.render_locations(renderer, screen_width, screen_height, entities)
		self.render_npcs(renderer, screen_width, screen_height, entities)
		self.render_player(renderer, screen_width, screen_height, entities)

	def render_background(self, renderer, screen_width, screen_height):
		sdl2.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255)
		sdl2.SDL_RenderCopy(renderer, self.texture, None, sdl2.SDL_Rect(
			int(screen_width - self.size),
			int(screen_height - self.size),
			int(self.size),
			int(self.size)))

	def render_roads(self, renderer, screen_width, screen_height, entities):
		sdl2.SDL_SetRenderDrawColor(renderer, 48, 48, 48, 255)
		for road in entities.map_elements:
			if road.type != MapElementType.ROAD:
				continue

			sdl2.SDL_RenderFillRect(renderer, sdl2.SDL_Rect(
				self.get_adjusted_x(road, screen_width),
				self.get_adjusted_y(road, screen_height),
				int(road.width * self.x_scale),
				int(road.height * self.y_scale)))

	def render_locations(self, renderer, screen_width, screen_height, entities):
		sdl2.SDL_SetRenderDrawColor(renderer, 80, 80, 80, 255)
		for location in entities.locations:
			sdl2.SDL_RenderFillRect(renderer, sdl2.SDL_Rect(
				self.get_adjusted_x(location, screen_width),
				self.get_adjusted_y(location, screen_height),
				int(location.width * self.x_scale),
				int(location.height * self.y_scale)))

	def render_npcs(self, renderer, screen_width, screen_height, entities):
		sdl2.SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255)
		for character in entities.characters:
			sdl2.SDL_RenderFillRect(renderer, sdl2.SDL_Rect(
				self.get_adjusted_x(character, screen_width),
				self.get_adjusted_y(character, screen_height),
				MiniMap.character_dot_size,
				MiniMap.character_dot_size))

	def render_player(self, renderer, screen_width, screen_height, entities):
		sdl2.SDL_SetRenderDrawColor(renderer, 0, 0, 255, 255)
		sdl2.SDL_RenderFillRect(renderer, sdl2.SDL_Rect(
			int(self.get_adjusted_x(entities.player, screen_width)
			- MiniMap.player_dot_size / 2),
			int(self.get_adjusted_y(entities.player, screen_height)
			- MiniMap.player_dot_size / 2),
			MiniMap.player_dot_size,
			MiniMap.player_dot_size))

	def get_adjusted_x(self, entity, screen_width):
		return int(screen_width - self.size / 2\
			* MiniMap.proportional_to_container + entity.x * self.x_scale)

	def get_adjusted_y(self, entity, screen_height):
		return int(screen_height - self.size + self.size\
			* (1 - MiniMap.proportional_to_container) + entity.y * self.y_scale)

class TextDisplayer:
	# Returns the dimensions of the text
	def text_dimensions(self, texture):
		width = pointer(c_int(0))
		height = pointer(c_int(0))
		sdl2.SDL_QueryTexture(texture, None, None, width, height)
		return width.contents.value, height.contents.value

class MainMenu:
	"""Creates the main menu object that can be instantiated to execute the
	main menu loop that, when executed, returns the game settings to pass to
	the instantiation of the game loop.
	"""

	def __init__(self):
		"""Initialize the main menu class.

		:param texture: The texture that should be used as the basis for the
		main menu.
		:type texture: int (via `enums.py`)
		:param renderer: The rendering engine that is shared among all
		instantiated classes in the application.
		:type renderer: `renderer.Renderer` instance
		"""

		self.win_w = 1280 # window width
		self.win_h = 720 # window height
		self.bg_color = (140, 198, 62) # color of the background
		# a lighter shade of the background
		self.bg_color_light = (179, 217, 129)
		self.sel_diff_margin = 2
		self.game_settings = { # initialize default game settings
			'difficulty': 1, # low: 0, med: 1, hi: 2
			'game_name': 'New Game',
		}

		# build window
		self.window = sdl2.ext.Window('Settings',
			size=(self.win_w, self.win_h))

		# define renderer
		self.renderer = sdl2.ext.Renderer(
			self.window,
			flags=sdl2.render.SDL_RENDERER_ACCELERATED,
		)

		# define fonts
		# this is required for text rendering on screen via SpriteFactory
		self.fontmanager = sdl2.ext.FontManager(
			'cour.ttf',
			alias='title',
			size=40,
			color=sdl2.ext.Color(0,0,0), # black
		)

	def onclick(self, button, event):
		"""Defines the logic for when a button element is clicked.
		"""

		print('Button clicked.')

	def quit_menu(self, button, event):
		"""Defines the logic for when a button element is clicked that should
		trigger exiting the menu without starting the game.
		"""

		self.running = False
		self.game_settings = None

	def settings_save(self, button, event):
		"""Defines the logic for when a button element is clicked that should
		trigger exiting the menu and starting the game.
		"""

		self.running = False

	def change_diff(self, button, event):
		"""Defines the logic for when a button being clicked changes the
		indicator for difficulty.
		"""

		self.sel_diff.position = (
			button.position[0] - self.sel_diff_margin,
			button.position[1] - self.sel_diff_margin,
		)

	def sel_diff_low(self, button, event):
		"""Defines the logic for when a button being clicked triggers a change
		of selected difficulty to low.
		"""

		self.game_settings['difficulty'] = 0

	def sel_diff_med(self, button, event):
		"""Defines the logic for when a button being clicked triggers a change
		of selected difficulty to med.
		"""

		self.game_settings['difficulty'] = 1

	def sel_diff_hi(self, button, event):
		"""Defines the logic for when a button being clicked triggers a change
		of selected difficulty to hi.
		"""

		self.game_settings['difficulty'] = 2

	def run(self):
		"""Starts the loop for the main menu that allows designating of game
		settings.

		Returns a dictionary where the keys are names of game configuration
		settings and the values are the values of those settings.
		"""

		# initialize state variables
		self.running = True

		# open the window
		self.window.open()

		# construct sprite factory
		factory = sdl2.ext.SpriteFactory(
			renderer=self.renderer,
			fontmanager=self.fontmanager
		)
		# construct the UI factory (for buttons and such)
		uifactory = sdl2.ext.UIFactory(factory)
		# define uiprocessor which handles UI events
		uiprocessor = sdl2.ext.UIProcessor()
		# let the factory render elements automatically
		spriterenderer = factory.create_sprite_render_system(self.window)
		
		# define what the background looks like
		background = factory.from_color(
			self.bg_color, # color
			(self.win_w, self.win_h), # dimensions
		)

		# add the title
		title = factory.from_text('Main Menu')
		title.position = (
			int(self.win_w / 2 - title.size[0] / 2),
			int(self.win_h / 10 - title.size[1] / 2),
		)

		# add the quit button
		quit_btn = uifactory.from_color(sdl2.ext.BUTTON, (0,0,0), (70,30))
		quit_btn.position = (
			int(self.win_w * 1 / 4 - quit_btn.size[0] / 2),
			int(self.win_h * 8 / 10 + 10),
		)
		quit_lbl = factory.from_text('Quit', size=20, color=(255,255,255))
		quit_lbl.position = (
			int(self.win_w * 1 / 4 - quit_lbl.size[0] / 2),
			int(self.win_h * 8 / 10 + 3 + quit_lbl.size[1] / 2),
		)
		quit_btn.click += self.quit_menu

		# add the start button
		start_btn = uifactory.from_color(sdl2.ext.BUTTON, (0,0,0), (70,30))
		start_btn.position = (
			int(self.win_w * 3 / 4 - start_btn.size[0] / 2),
			int(self.win_h * 8 / 10 + 10),
		)
		start_lbl = factory.from_text('Start', size=20, color=(255,255,255))
		start_lbl.position = (
			int(self.win_w * 3 / 4 - start_lbl.size[0] / 2),
			int(self.win_h * 8 / 10 + 3 + start_lbl.size[1] / 2),
		)
		start_btn.click += self.settings_save

		# to add the game options, we need to partition off the area of the
		# screen. We have 7/10 of the screen area, between the main menu and
		# the quit/start buttons, so we can use that
		sec_top = int(self.win_h * 2 / 10) # pixel position
		sec_h = int(self.win_h * 6 / 10) # height in pixels
		sec_left = int(self.win_w * 1 / 10) # pixel position
		sec_w = int(self.win_w * 8 / 10) # width in pixels

		std_margin_w = int(sec_w * .02)
		std_margin_h = int(sec_h * .05)

		# background cannon for options so that I can see the area
		test = factory.from_color(self.bg_color_light, (sec_w, sec_h))
		test.position = (
			sec_left,
			sec_top,
		)

		# label for naming the save game
		game_name_label = factory.from_text(
			'Game Name:',
			size=30,
			color=(0,0,0),
		)
		game_name_label.position = (
			sec_left + std_margin_w,
			sec_top + std_margin_h,
		)

		# label for difficulty selection
		difficulty = factory.from_text('Difficulty:', size=30, color=(0,0,0))
		difficulty.position = (
			game_name_label.position[0],
			game_name_label.position[0] + game_name_label.size[1]\
				+ std_margin_h,
		)

		# button for low difficulty
		diff_btn_low = uifactory.from_surface(
			sdl2.ext.BUTTON, # type of ui element
			self.fontmanager.render(
				'Low',
				size=25,
				color=(0,255,0),
				bg_color=(0,0,0),
			),
			free=True,
		)
		diff_btn_low.position = (
			sec_left + int(sec_w / 2) + std_margin_w, # doesn't need to be rel
			difficulty.position[1], # relative to difficulty
		)
		diff_btn_low.click += self.sel_diff_low
		diff_btn_low.click += self.change_diff

		# button for med difficulty
		diff_btn_mid = uifactory.from_surface(
			sdl2.ext.BUTTON,
			self.fontmanager.render(
				'Med',
				size=25,
				color=(255,255,0),
				bg_color=(0,0,0),
			),
			free=True,
		)
		diff_btn_mid.position = (
			diff_btn_low.position[0] + diff_btn_low.size[0] + std_margin_w,
			diff_btn_low.position[1],
		)
		diff_btn_mid.click += self.sel_diff_med
		diff_btn_mid.click += self.change_diff

		# button for high difficulty
		diff_btn_hi = uifactory.from_surface(
			sdl2.ext.BUTTON,
			self.fontmanager.render(
				'Hi ',
				size=25,
				color=(255,0,0),
				bg_color=(0,0,0),
			),
			free=True,
		)
		diff_btn_hi.position = (
			diff_btn_mid.position[0] + diff_btn_mid.size[0] + std_margin_w,
			diff_btn_mid.position[1],
		)
		diff_btn_hi.click += self.sel_diff_hi
		diff_btn_hi.click += self.change_diff

		# texture used to indicate which difficulty is selected
		self.sel_diff = factory.from_color(
			(255,255,255), # selection color
			(
				diff_btn_mid.size[0] + self.sel_diff_margin * 2,
				diff_btn_mid.size[1] + self.sel_diff_margin * 2,
			),
		)
		self.sel_diff.position = (
			diff_btn_mid.position[0] - self.sel_diff_margin,
			diff_btn_mid.position[1] - self.sel_diff_margin,
		)


		# used for debug purposes
		temp = factory.from_color((255,0,0), (5,5))
		temp.position = (
			sec_left,
			sec_top,
		)

		while self.running:
			events = sdl2.ext.get_events()
			for event in events:
				if event.type == sdl2.SDL_QUIT:
					# if we quit, we don't want to start the game
					self.running = False
					# game_settings == None will stop the game from starting
					self.game_settings = None
					break
				# dispatch events to their corresponding UI components
				uiprocessor.dispatch(
					[	# the list of ui components that can receive events
						quit_btn,
						start_btn,
						diff_btn_low,
						diff_btn_mid,
						diff_btn_hi,
					],
					event,
				)

			self.renderer.clear(0)
			# render all of the visual components
			spriterenderer.render((
				background,
				title,
				quit_btn,
				quit_lbl,
				start_btn,
				start_lbl,

				# the actual settings' components
				# test,
				self.sel_diff,
				game_name_label,
				difficulty,
				diff_btn_low,
				diff_btn_mid,
				diff_btn_hi,

				# temp,
			))

		self.window.close()

		return self.game_settings

# Text displays for locations and interactions
class MiddleText(TextDisplayer):
	# Y-distance between top/bottom of screen
	y_offset = 15

	def __init__(self):
		self.top_text = ''
		self.bottom_text = ''
		self.text_color = sdl2.SDL_Color(0, 0, 0) # black

		# Maps text to texture
		# <str, SDL texture>
		# Keeps track of textures that have already been created
		# so that rendering does not require creating that texture again
		self.texture_cache = {}

	# Creates texture from the text and renders centered on the screen
	# TO DO: increase efficiency by only creating texture if text is different
	def render(self, renderer, small_text, medium_text,
		screen_width, screen_height):
		if self.top_text != None:
			self.render_text(renderer, medium_text, screen_width,
				self.top_text, MiddleText.y_offset)
		if self.bottom_text != None:
			self.render_text(renderer, medium_text, screen_width,
				self.bottom_text, screen_height - MiddleText.y_offset * 2)

	def render_text(self, renderer, font, screen_width, text, y_position):
		if text in self.texture_cache:
			text_texture = self.texture_cache.get(text)
		else:	
			# Create font surface
			text_surface = sdl2.sdlttf.TTF_RenderText_Solid(
				font, str.encode(text), self.text_color)
			# Create texture from surface
			text_texture = sdl2.SDL_CreateTextureFromSurface(
				renderer, text_surface)
			# Free surface
			sdl2.SDL_FreeSurface(text_surface)

			# Add to cache for future use
			self.texture_cache[text] = text_texture

		# Query dimensions
		width, height = self.text_dimensions(text_texture)
		# Center text
		text_x = self.center_text(screen_width, width)
		# Render to window
		sdl2.SDL_RenderCopyEx(renderer,	text_texture, None,
			sdl2.SDL_Rect(text_x, y_position, width, height), 0.0,
			None, sdl2.SDL_FLIP_NONE)

	# Returns x-position for text to be centered within the screen width
	def center_text(self, screen_width, text_width):
		return int(screen_width / 2 - text_width / 2)

	# Sets the top text
	def set_top(self, new_text):
		self.top_text = new_text

	# Sets the bottom text
	def set_bottom(self, new_text):
		self.bottom_text = new_text

# Text displays for player's meters and game day/time
class InfoText(TextDisplayer):
	# X and Y distance between top of screen
	offset = 15

	def __init__(self):
		self.meters_text = ''
		self.time_text = ''

		self.text_color = sdl2.SDL_Color(0, 0, 0) # black

		# Keep track of values so that
		# a new texture is only created when the values change
		self.current_money = 0
		self.current_health = 0
		self.current_morale = 0

		self.current_day = 0
		self.current_time = 0

		# SDL textures for rendering
		self.meters_texture = None
		self.time_texture = None

		# Whether to recreate the texture for the next frame
		self.recreate_texture = False

	# Renders text texture to the screen
	def render(self, renderer, font, screen_width):
		if self.recreate_texture:
			self.create_text(renderer, font)

		self.render_text(renderer, screen_width)
	
	def create_text(self, renderer, font):
		# Create font surface
		meters_surface = sdl2.sdlttf.TTF_RenderText_Solid(
			font, str.encode(self.meters_text), self.text_color)
		time_surface = sdl2.sdlttf.TTF_RenderText_Solid(
			font, str.encode(self.time_text), self.text_color)

		# Create texture from surface
		self.meters_texture = sdl2.SDL_CreateTextureFromSurface(
			renderer, meters_surface)
		self.time_texture = sdl2.SDL_CreateTextureFromSurface(
			renderer, time_surface)

		# Free surface
		sdl2.SDL_FreeSurface(meters_surface)
		sdl2.SDL_FreeSurface(time_surface)

	def render_text(self, renderer, screen_width):
		# Meters
		width, height = self.text_dimensions(self.meters_texture)
		sdl2.SDL_RenderCopyEx(renderer,	self.meters_texture, None,
			sdl2.SDL_Rect(InfoText.offset, InfoText.offset, width, height),
			0.0, None, sdl2.SDL_FLIP_NONE)

		# Time
		width, height = self.text_dimensions(self.time_texture)
		sdl2.SDL_RenderCopyEx(renderer,	self.time_texture, None,
			sdl2.SDL_Rect(screen_width - width - InfoText.offset,
			InfoText.offset, width, height), 0.0, None, sdl2.SDL_FLIP_NONE)

	# Left text format: $money - health / 100 - morale / 100
	# Right text format: 00:00
	# Checks if the meters are different the currently displayed meters
	# and if the game time is different than the current time
	# If so, renderer will create a new texture on the next frame,
	# otherwise, renderer will use the same texture
	def set(self, money, health, morale, day, time):
		if self.different_values(money, health, morale, day, time):
			self.recreate_texture = True
			
			self.meters_text = "$" + str(money) + " - Health: "\
				+ str(int(health)) + " / 100 - Morale: "\
				+ str(int(morale)) + " / 100"

			self.time_text = 'Day: ' + str(day) + ' - Time: '\
				+ self.get_formatted_time(time)

			# Free texture
			sdl2.SDL_DestroyTexture(self.meters_texture)
			sdl2.SDL_DestroyTexture(self.time_texture)

			# Update current values
			self.current_money = money
			self.current_health = health
			self.current_morale = morale
			self.current_time = time
		else:
			self.recreate_texture = False

	# Returns true if the money, health, morale, and time values are different
	# than those currently displaced, returns false otherwise
	def different_values(self, money, health, morale, day, time):
		if money != self.current_money:
			return True
		
		if health != self.current_health:
			return True
		
		if morale != self.current_morale:
			return True

		if day != self.current_day:
			return True

		if time != self.current_time:
			return True

		return False

	def get_formatted_time(self, time):
		hours = int(time / 60)

		remaining_minutes = str(int(time % 60)).zfill(2)

		if hours >= 12:
			hours -= 12
			if hours == 0:
				return '12:' + remaining_minutes + ' PM'
			else:
				return str(hours) + ':' + remaining_minutes + ' PM'
		else:
			if hours == 0:
				hours = 12
			return str(hours) + ':' + remaining_minutes + ' AM'

class TimeStampedMessage:
	def __init__(self, text):
		self.text = text
		self.time = sdl2.SDL_GetTicks()

class MessageStack(TextDisplayer):
	# Time the message stays in the stack
	message_duration = 5000 # ms

	# X-offset from edge of screen
	x_offset = 15

	# Y-spacing in between messages
	spacing = 25 # px

	def __init__(self):
		self.messages = []
		self.text_color = sdl2.SDL_Color(0, 0, 0) # black

	# Renders messages by rows, with the new message on the top
	def render(self, renderer, font, screen_height):
		self.remove_expired_messages()

		row = 1
		for message in self.messages:
			# Create font surface
			text_surface = sdl2.sdlttf.TTF_RenderText_Solid(
				font, str.encode(message.text), self.text_color)
			# Create texture from surface
			text_texture = sdl2.SDL_CreateTextureFromSurface(
				renderer, text_surface)
			# Free surface
			sdl2.SDL_FreeSurface(text_surface)
			# Query dimensions
			width, height = self.text_dimensions(text_texture)
			# Render to window
			sdl2.SDL_RenderCopyEx(renderer,	text_texture, None, sdl2.SDL_Rect(
				MessageStack.x_offset, screen_height - 
				MessageStack.spacing * row,	width, height), 0.0, None,
				sdl2.SDL_FLIP_NONE)
			# Free texture
			sdl2.SDL_DestroyTexture(text_texture)
			row += 1

	# Removes messages that have been displayed for the duration
	def remove_expired_messages(self):
		for message in self.messages:
			if MessageStack.message_duration < sdl2.SDL_GetTicks()\
			- message.time:
				self.messages.remove(message)
				# Only removes one message each frame
				return

	# Adds messages from list to the stack with the current time
	def insert(self, list):
		for message in list:
			self.messages.append(TimeStampedMessage(message))
