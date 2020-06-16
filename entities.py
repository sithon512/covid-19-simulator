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
    
    # Parameterized constructor
    def __init__(self, x, y, width, height, texture):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.texture = texture
    
    # Default render method
    # Draws texture to x and y position on window in relation to the camera
    def render(self, window, camera_x, camera_y):
        window.blit(self.texture, (self.x - camera_x, self.y - camera_y))

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

        # Rendered angle
        self.angle = 0.0

    # Updates position based on velocity,
    # independent of framerate
    def update_position(self):
        # Time since last move: ms
        time_elapsed = pygame.time.get_ticks() - self.last_moved
        
        # Divide by 1000 because elapsed time is in ms,
        # but velocities are in px / s
        self.x += self.x_velocity * time_elapsed / 1000.0
        self.y += self.y_velocity * time_elapsed / 1000.0

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

        window.blit(pygame.transform.rotozoom(self.texture, self.angle, 1.0),
            (self.x - camera_x, self.y - camera_y))

class Player(MovableEntity):
    # Default values:

    # Dimensions
    default_width = 50 # px
    default_height = 50 # px

    # Maximum speeds
    walking_speed = 100 # px / s
    running_speed = 300 # px / s

    # Default constructor
    def __init__(self):
        # Set starting position and texture later
        MovableEntity.__init__(self, 0.0, 0.0, 
            Player.default_width, Player.default_height, None, Player.walking_speed)

        self.money = 0
        self.health = 0
        self.morale = 0

        # Maps supply type to supply quantity
        # <SupplyType, int>
        self.supplies = {}

    def update(self):
        self.update_position()

    # Adjusts player's velocity based on the parameters
    # Caps each component to player's maximum speed
    # Toggles maximum speed based on whether the player is running
    # Resets if there is no change
    def adjust_velocity(self, x_change, y_change, running):
        self.x_velocity += x_change
        self.y_velocity += y_change

        # Toggle maximum speed
        if running:
            self.speed = Player.running_speed
        else:
            self.speed = Player.walking_speed

        # Cap to maximum speed
        if self.x_velocity >= self.speed:
            self.x_velocity = self.speed

        if self.x_velocity <= -self.speed:
            self.x_velocity = -self.speed

        if self.y_velocity >= self.speed:
            self.y_velocity = self.speed

        if self.y_velocity <= -self.speed:
            self.y_velocity = -self.speed

        # No change, reset
        if x_change == 0:
            self.x_velocity = 0
        
        if y_change == 0:
            self.y_velocity = 0


    # TO DO: add methods for adding and removing supplies

# Contains all entities
class Entities:
    def __init__(self):
        self.player = Player()

        # TO DO: add lists locations, characters, pets, and supplies

    # Add Methods:
    # TO DO: add methods for adding locations, characters, pets, and supplies

    # Remove Methods:
    # TO DO: add method for removing pets and supplies

    # Various Methods:

    # Initialize player's starting position/meters and set texture
    def init_player(self, x, y, texture, money, health, morale):
        self.player.x = x
        self.player.y = y

        self.player.texture = texture

        self.player.money = money
        self.player.health = health
        self.player.morale = morale

# Performs operations on entities
class Controller:
    def __init__(self):

        # Changes in the player's x and y velocities each frame
        self.player_x_change = 0
        self.player_y_change = 0
        self.player_running = False

    def update_entities(self, entities):
        # Update player
        entities.player.adjust_velocity(
            self.player_x_change,
            self.player_y_change,
            self.player_running)
        entities.player.update()

        self.reset_values()
    
    # Interface between the controller and the user interface for player movement input
    # Adds/subtracts to player up, down, left, and right changes based on parameters
    # and sets whether the player is running
    def move_player(self, up, down, left, right, running):
        if up:
            self.player_y_change -= 1
        if down:
            self.player_y_change += 1
        if left:
            self.player_x_change -= 1
        if right:
            self.player_x_change += 1
        if running:
            self.player_running = True

    # Resets values that are only valid for each frame
    def reset_values(self):
        self.player_x_change = 0
        self.player_y_change = 0
        self.player_running = False

