import sdl2
import sdl2.ext
import sdl2.sdlttf

from ctypes import c_int, pointer

class UserInterface:
	# Initializes fonts and messages
	def __init__(self):
		# TO DO: implement panels later
		self.panels = []

		# Fonts of various sizes
		self.small_text = sdl2.sdlttf.TTF_OpenFont(b'cour.ttf', 12)
		self.medium_text = sdl2.sdlttf.TTF_OpenFont(b'cour.ttf', 14)
		self.large_text = sdl2.sdlttf.TTF_OpenFont(b'cour.ttf', 16)

		# Initialize message systems
		self.middle_text = MiddleText()
		self.info_text = InfoText()
		self.message_stack = MessageStack()

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
		
		controller.move_player(up, down, left, right, running)
	
	# TO DO: create methods for handling mouse click and hover

	# Renders text and panels
	def render(self, renderer, screen_width, screen_height):
		self.middle_text.render(renderer, self.small_text, self.medium_text,
			screen_width, screen_height)
		self.info_text.render(renderer, self.medium_text)
		self.message_stack.render(renderer, self.small_text, screen_height)

class TextDisplayer:
	# Returns the dimensions of the text
	def text_dimensions(self, texture):
		width = pointer(c_int(0))
		height = pointer(c_int(0))
		sdl2.SDL_QueryTexture(texture, None, None, width, height)
		return width.contents.value, height.contents.value
	
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

# Text displays for player's meters
class InfoText(TextDisplayer):
	# X and Y distance between top of screen
	offset = 15

	def __init__(self):
		self.text = ''
		self.text_color = sdl2.SDL_Color(0, 0, 0) # black

		# Keep track of values so that
		# a new texture is only created when the values change
		self.current_money = 0
		self.current_health = 0
		self.current_morale = 0

		# SDL texture for rendering
		self.texture = None

		# Whether to recreate the texture for the next frame
		self.recreate_texture = False

	# Creates texture from the text and renders on the screen
	def render(self, renderer, font):
		if self.recreate_texture:
			self.create_text(renderer, font)

		self.render_text(renderer)
	
	def create_text(self, renderer, font):
		# Create font surface
		text_surface = sdl2.sdlttf.TTF_RenderText_Solid(
			font, str.encode(self.text), self.text_color)
		# Create texture from surface
		self.texture = sdl2.SDL_CreateTextureFromSurface(renderer, text_surface)
		# Free surface
		sdl2.SDL_FreeSurface(text_surface)

	def render_text(self, renderer):
		# Query dimensions
		width, height = self.text_dimensions(self.texture)
		# Render to window
		sdl2.SDL_RenderCopyEx(renderer,	self.texture, None,
			sdl2.SDL_Rect(InfoText.offset, InfoText.offset, width, height),
			0.0, None, sdl2.SDL_FLIP_NONE)

	# Text format:
	# $money - health / 100 - morale / 100
	# Checks if the meters are different the currently displayed meters,
	# if so, renderer will create a new texture on the next frame,
	# otherwise, renderer will use the same texture
	def set(self, money, health, morale):
		if self.different_values(money, health, morale):
			self.recreate_texture = True
			
			self.text = "$" + str(money) + " - Health: "
			self.text += str(int(health)) + " / 100 - Morale: "\
			+ str(int(morale)) + " / 100"

			# Free texture
			sdl2.SDL_DestroyTexture(self.texture)

			# Update current values
			self.current_money = money
			self.current_health = health
			self.current_morale = morale
		else:
			self.recreate_texture = False

	# Returns true if the money, health, and morale values are different than 
	# those currently displaced, returns false otherwise
	def different_values(self, money, health, morale):
		if money != self.current_money:
			return True
		
		if health != self.current_health:
			return True
		
		if morale != self.current_morale:
			return True

		return False

class TimeStampedMessage:
	def __init__(self, text):
		self.text = text
		self.time = sdl2.SDL_GetTicks()

class MessageStack(TextDisplayer):
	# Time the message stays in the stack
	message_duration = 4000 # ms

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
