import pygame, math

class Entity:
    # Default constructor
    def __init__(self):
        # Position: px
        self.x = 0.0
        self.y = 0.0

        # Dimensions: px
        self.width = 0
        self.height = 0

        # Pygame texture
        self.texture = None

        # Rendered angle
        self.angle = 0.0
    
    # Parameterized constructor
    def __init__(self, x, y, width, height, texture):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.texture = texture
        self.angle = 0.0
    
    # Default render method
    # Draws texture to x and y position on window in relation to the camera
    def render(self, window, camera_x, camera_y):
        window.blit(self.texture, (self.x - camera_x, self.y - camera_y))

    # Returns true if there is a rectangular collision with the other entity
    def check_collision(self, other):
        # Swap width and height if the entity is not perpendicular
        if self.angle != 0 and self.angle != 180:
            self.swap_dimensions()

        collision = True

        if self.y + self.height <= other.y:
            collision =  False
        if self.y >= other.y + other.height:
            collision =  False
        if self.x + self.width <= other.x:
            collision =  False
        if self.x >= other.x + other.width:
            collision =  False
        
        # Revert swap after checking dimensions
        if self.angle != 0 and self.angle != 180:
            self.swap_dimensions()

        return collision

    def swap_dimensions(self):
        self.width, self.height = self.height, self.width

class MovableEntity(Entity):
    def __init__(self, x, y, width, height, texture, speed):
        Entity.__init__(self, x, y, width, height, texture)

        # Maximum movement speed: px / s
        self.speed = speed

        # Velocity components: px / s
        self.x_velocity = 0.0
        self.y_velocity = 0.0

        # Last moved - for frame independent movement: ms
        self.last_moved = pygame.time.get_ticks()

        # Whether another entity is blocking the movement of this entity
        # e.g. colliding with another entity
        self.movement_blocked = False

    # Updates position based on velocity,
    # independent of framerate
    def update_position(self):
        # Time since last move: ms
        time_elapsed = pygame.time.get_ticks() - self.last_moved
        
        # Divide by 1000 because elapsed time is in ms,
        # but velocities are in px / s
        self.x += self.x_velocity * time_elapsed / 1000.0
        self.y += self.y_velocity * time_elapsed / 1000.0

        # Movement blocked by another entity, undo move
        if self.movement_blocked:
            self.x -= self.x_velocity * time_elapsed / 1000.0
            self.y -= self.y_velocity * time_elapsed / 1000.0

            # reset for next frame
            self.movement_blocked = False

        self.last_moved = pygame.time.get_ticks()

    # Draws texture to x and y position on window in relation to the camera,
    # facing the angle of its most recent velocity
    def render(self, window, camera_x, camera_y):
        # Calculate angle based on velocities
        if self.x_velocity != 0 and self.y_velocity > 0:
            self.angle = math.degrees(math.atan(self.y_velocity / self.x_velocity)) + 270.0
        elif self.x_velocity != 0 and self.y_velocity < 0:
            self.angle = math.degrees(math.atan(self.y_velocity / self.x_velocity)) + 90.0
        elif self.x_velocity > 0 and self.y_velocity == 0:
            self.angle = 0.0
        elif self.x_velocity < 0 and self.y_velocity == 0:
            self.angle = 180.0
        elif self.y_velocity > 0 and self.x_velocity == 0:
            self.angle = 270.0
        elif self.y_velocity < 0 and self.x_velocity == 0:
            self.angle = 90.0

        window.blit(pygame.transform.rotate(self.texture, self.angle),
            (self.x - camera_x, self.y - camera_y))
    
    # Blocks movement for this frame
    def block_movement(self):
        self.movement_blocked = True
