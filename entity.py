import sdl2, math

class Entity:
	def __init__(self, x = 0, y = 0, width = 0, height = 0, texture = None):
		self.x = x
		self.y = y
		self.width = width
		self.height = height
		self.texture = texture
		self.angle = 0.0

		# For proper collision detection when
		# the angle is not 0 or 180
		self.original_width = self.width
		self.original_height = self.height
	
	# Default render method
	# Draws texture to x and y position on window in relation to the camera
	def render(self, renderer, camera_x, camera_y):
		if self.angle != 0 and self.angle != 180:
			self.swap_dimensions(True)
		else:
			self.swap_dimensions(False)

		sdl2.SDL_RenderCopyEx(renderer, self.texture, None,
			sdl2.SDL_Rect(int(self.x - camera_x), int(self.y - camera_y),
			int(self.width), int(self.height)), 0, None, sdl2.SDL_FLIP_NONE)

	# Returns true if there is a rectangular collision with the other entity
	def check_collision(self, other):
		collision = True

		if self.y + self.height <= other.y:
			collision = False
		if self.y >= other.y + other.height:
			collision = False
		if self.x + self.width <= other.x:
			collision = False
		if self.x >= other.x + other.width:
			collision = False

		return collision

	# Same as method above but directly pass in coordinates and dimensions
	def check_collision_directly(self, x, y, width, height):
		collision = True

		if self.y + self.height <= y:
			collision = False
		if self.y >= y + height:
			collision = False
		if self.x + self.width <= x:
			collision = False
		if self.x >= x + width:
			collision = False

		return collision

	# Swaps width and height based on original values
	# If original is true, width and height will be original width and height
	# otherwise, they will be swapped
	def swap_dimensions(self, original):
		if original:
			self.width = self.original_height
			self.height = self.original_width
		else:
			self.width = self.original_width
			self.height = self.original_height

class MovableEntity(Entity):
	def __init__(self, x, y, width, height, texture, speed):
		Entity.__init__(self, x, y, width, height, texture)

		# Maximum movement speed: px / s
		self.speed = speed

		# Velocity components: px / s
		self.x_velocity = 0.0
		self.y_velocity = 0.0

		# Last moved - for frame independent movement: ms
		self.last_moved = sdl2.SDL_GetTicks()

		# Whether another entity is blocking the movement of this entity
		# e.g. colliding with another entity
		self.movement_blocked = False

	# Updates position based on velocity, independent of framerate
	# Returns magnitude of distance traveled
	def update_position(self):
		# Time since last move: ms
		time_elapsed = sdl2.SDL_GetTicks() - self.last_moved
		
		# Divide by 1000 because elapsed time is in ms,
		# but velocities are in px / s
		x_distance = self.x_velocity * time_elapsed / 1000.0
		y_distance = self.y_velocity * time_elapsed / 1000.0

		self.x += x_distance
		self.y += y_distance

		# Movement blocked by another entity, undo move
		if self.movement_blocked:
			self.x -= self.x_velocity * time_elapsed / 1000.0
			self.y -= self.y_velocity * time_elapsed / 1000.0

			# reset for next frame
			self.movement_blocked = False

		self.last_moved = sdl2.SDL_GetTicks()

		return math.sqrt(x_distance ** 2 + y_distance ** 2)

	# Draws texture to x and y position on window in relation to the camera,
	# facing the angle of its most recent velocity
	def render(self, renderer, camera_x, camera_y):
		# Calculate angle based on velocities
		if self.x_velocity > 0 and self.y_velocity == 0:
			self.angle = 0.0
		elif self.x_velocity < 0 and self.y_velocity == 0:
			self.angle = 180.0
		elif self.y_velocity > 0 and self.x_velocity == 0:
			self.angle = 90.0
		elif self.y_velocity < 0 and self.x_velocity == 0:
			self.angle = 270.0

		Entity.render(self, renderer, camera_x, camera_y)
	
	# Blocks movement for this frame
	def block_movement(self):
		self.movement_blocked = True
