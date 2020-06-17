import pygame
import pygame.freetype

class UserInterface:
	# Initializes fonts and messages
	def __init__(self):
		pygame.font.init()

		# TO DO: implement panels later
		self.panels = []
		
		# Fonts of various sizes
		self.small_text = pygame.freetype.SysFont('Courier New', 12)
		self.medium_text = pygame.freetype.SysFont('Courier New', 14)
		self.large_text = pygame.freetype.SysFont('Courier New', 16)

		# Initialize message systems
		self.middle_text = MiddleText()
		self.info_text = InfoText()
		self.message_stack = MessageStack()

		self.last_interaction = pygame.time.get_ticks()

	# Handles mouse and keyboard input
	# Returns false if the user quits the game
	def handle_input(self, controller, screen_dimensions):
		for event in pygame.event.get():
			# User pressed 'X' button
			if event.type == pygame.QUIT:
				print("[Info] User closed the game window")
				return False

			# User resized window
			if event.type == pygame.VIDEORESIZE:
				screen_dimensions[0] = event.w
				screen_dimensions[1] = event.h

		self.handle_keyboard(controller)

		controller.update_messages(self.middle_text, self.info_text, self.message_stack)

		return True

	def handle_keyboard(self, controller):
		self.handle_player_movement(controller)

	# Handles player movement with W, A, S, D / arrow keys + Shift and
	# the interact action with E
	def handle_player_movement(self, controller):
		# Gets current keys pressed
		keystate = pygame.key.get_pressed()

		# Reset movement each frame
		up = False
		down = False
		left = False
		right = False
		running = False

		# W, A, S, D and arrow keys
		# move player up, left, down, and right, respectively
		if keystate[pygame.K_w] or keystate[pygame.K_UP]:
			up = True
		if keystate[pygame.K_a] or keystate[pygame.K_LEFT]:
			left = True
		if keystate[pygame.K_s] or keystate[pygame.K_DOWN]:
			down = True
		if keystate[pygame.K_d] or keystate[pygame.K_RIGHT]:
			right = True

		# Shift key to run
		if keystate[pygame.K_LSHIFT] or keystate[pygame.K_RSHIFT]:
			running = True

		# E for player interact action
		if keystate[pygame.K_e]:
			controller.interact_player()
		
		controller.move_player(up, down, left, right, running)
	
	# TO DO: create methods for handling mouse click and hover

	# Renders text and panels
	def render(self, window):
		self.middle_text.render(window, self.small_text, self.medium_text)
		self.info_text.render(window, self.medium_text)
		self.message_stack.render(window, self.small_text)

# Text displays for locations on the top of the screen and interactions on the bottom
class MiddleText:
	# Y-distance between top/bottom of screen
	y_offset = 15

	def __init__(self):
		self.top_text = ''
		self.bottom_text = ''
		self.text_color = (0, 0, 0) # black

	# Creates texture from the text and renders centered on the screen
	# TO DO: increase efficiency by only creating texture if text is different
	def render(self, window, small_text, medium_text):
		top_text_surface, rect = medium_text.render(self.top_text, self.text_color)
		bottom_text_surface, rect = small_text.render(self.bottom_text, self.text_color)

		top_text_x = self.center_text(window.get_width(), top_text_surface)
		bottom_text_x = self.center_text(window.get_width(), bottom_text_surface)

		# Render the created surfaces
		window.blit(top_text_surface, (top_text_x, MiddleText.y_offset))

		window.blit(bottom_text_surface, (bottom_text_x, 
			window.get_height() - MiddleText.y_offset - bottom_text_surface.get_height()))

	# Returns x-position for text to be centered within the screen width
	def center_text(self, screen_width, text):
		return screen_width / 2 - text.get_width() / 2

	# Sets the top text
	def set_top(self, new_text):
		self.top_text = new_text

	# Sets the bottom text
	def set_bottom(self, new_text):
		self.bottom_text = new_text

# Text displays for player's meters
class InfoText:
	# X and Y distance between top of screen
	offset = 15

	def __init__(self):
		self.text = ''
		self.text_color = (0, 0, 0) # black

	# Creates texture from the text and renders on the screen
	# TO DO: increase efficiency by only creating texture if text is different
	def render(self, window, medium_text):
		text_surface, rect = medium_text.render(self.text, self.text_color)
		window.blit(text_surface, (InfoText.offset, InfoText.offset))

	# Text format:
	# $money - health / 100 - morale / 100
	def set(self, money, health, morale):
		self.text = "$" + str(money) + " - Health: "
		self.text += str(health) + " / 100 - Morale: " + str(morale) + " / 100"

class TimeStampedMessage:
	def __init__(self, text):
		self.text = text
		self.time = pygame.time.get_ticks()

class MessageStack:
	# Time the message stays in the stack
	message_duration = 2500 # ms

	# X-offset from edge of screen
	x_offset = 15

	# Y-spacing in between messages
	spacing = 25 # px

	def __init__(self):
		self.messages = []

		self.text_color = (0, 0, 0) # black

	# Renders messages by rows, with the new message on the top
	def render(self, window, small_text):
		self.remove_expired_messages()

		row = 1
		for message in self.messages:
			text_surface, rect = small_text.render(message.text, self.text_color)
			window.blit(text_surface, (MessageStack.x_offset, 
				window.get_height() - row * MessageStack.spacing))
			row += 1

	# Removes messages that have been displayed for the duration
	def remove_expired_messages(self):
		for message in self.messages:
			if MessageStack.message_duration < pygame.time.get_ticks() - message.time:
				self.messages.remove(message)
				# Only removes one message each frame
				return

	# Adds messages from list to the stack with the current time
	def insert(self, list):
		for message in list:
			self.messages.append(TimeStampedMessage(message))
