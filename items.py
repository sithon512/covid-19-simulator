import pygame, math

from entity import Entity
from enums import ItemType, PetType

class Item(Entity):
    # Minimum time between interact actions
    action_interval = 500 # ms

    def __init__(self, x, y, width, height, texture, type, name, interaction_message):
        Entity.__init__(self, x, y, width, height, texture)
        self.type = type

        self.name = name
        self.interaction_message = interaction_message

        # Last time the player interacted with the item: ms
        self.last_interaction = pygame.time.get_ticks()

    # Default method:
    # Block player movement if moving towards the item
    def handle_collision(self, player):
        if (player.x > self.x and player.x_velocity < 0):
            player.block_movement()
        if (player.x < self.x and player.x_velocity > 0):
            player.block_movement()
        if (player.y > self.y and player.y_velocity < 0):
            player.block_movement()
        if (player.y < self.y and player.y_velocity > 0):
            player.block_movement()

    # Abstract method:
    # What happens when the player interacts with this item
    def handle_interaction(self, player):
        pass

    # Returns true if the action interval has passed since the last interact action
    # Interact action must be limited because so that the player only interacts once
    # because pressing the interact button lasts more than one frame
    def check_action_interval(self):
        return pygame.time.get_ticks() - self.last_interaction > Item.action_interval

class Vehicle(Item):
    # Default values:

    # Dimensions
    default_width = 200 # px
    default_height = 110 # px

    # Maximum speed
    regular_speed = 500 # px / s
    turbo_speed = 1000 # px / s

    name = 'Vehicle'
    interaction_message = 'enter/exit (E)'

    def __init__(self, x, y, texture):
        Item.__init__(self, x, y, Vehicle.default_width, Vehicle.default_height,
            texture, ItemType.VEHICLE, Vehicle.name, Vehicle.interaction_message)

        # Whether the vehicle is attached to the player
        self.attached = False

    # Attaches vehicle to the player
    def handle_collision(self, player):
        if not self.attached:
            Item.handle_collision(self, player)
        else:
           # Calculate vehicle angle based on the player's velocity
            if player.x_velocity != 0 and player.y_velocity > 0:
                self.angle = math.degrees(math.atan(player.y_velocity / 
                player.x_velocity)) + 270.0
            elif player.x_velocity != 0 and player.y_velocity < 0:
                self.angle = math.degrees(math.atan(player.y_velocity / 
                player.x_velocity)) + 90.0
            elif player.x_velocity > 0 and player.y_velocity == 0:
                self.angle = 0.0
            elif player.x_velocity < 0 and player.y_velocity == 0:
                self.angle = 180.0
            elif player.y_velocity > 0 and player.x_velocity == 0:
                self.angle = 270.0
            elif player.y_velocity < 0 and player.x_velocity == 0:
                self.angle = 90.0

    # Attaches or detaches vehicle to the player
    def handle_interaction(self, player):
        if not self.check_action_interval():
            return

        if not self.attached:
            player.vehicle = self
            player.x = self.x
            player.y = self.y
            self.attached = True
        else:
            player.vehicle = None
            player.x = self.x - player.width
            self.attached = False

        self.last_interaction = pygame.time.get_ticks()

    # Draws texture to x and y position on window in relation to the camera,
    # facing the angle calculated from the player
    def render(self, window, camera_x, camera_y):
        window.blit(pygame.transform.rotate(pygame.transform.scale(self.texture, 
        (self.width, self.height)), self.angle), (self.x - camera_x, self.y - camera_y))

class Sink(Item):
    # Default values:

    # Dimensions
    default_width = 60 # px
    default_height = 40 # px

    name = 'Sink'
    interaction_message = 'wash hands (E)'

    def __init__(self, x, y, texture):
        Item.__init__(self, x, y, Sink.default_width, Sink.default_height,
            texture, ItemType.SINK, Sink.name, Sink.interaction_message)

    def handle_collision(self, player):
        Item.handle_collision(self, player)

    # TO DO: add washing hands
    def handle_interaction(self, player):
        pass

class ShoppingCart(Item):
    # Default values:

    # Dimensions
    default_width = 100 # px
    default_height = 60 # px

    name = 'Shopping Cart'
    interaction_message = 'open inventory (E) / push (Shift)'

    def __init__(self, x, y, texture):
        Item.__init__(self, x, y, ShoppingCart.default_width, ShoppingCart.default_height,
            texture, ItemType.SHOPPING_CART, ShoppingCart.name, ShoppingCart.interaction_message)

        # Last time the player moved the cart
        self.last_moved = pygame.time.get_ticks()

    # Pushes the cart in the player's velocity direction if the player is running
    def handle_collision(self, player):
        # If player is not running, do not push cart
        if not player.running:
            Item.handle_collision(self, player)
            return

        # Time since last move: ms
        time_elapsed = pygame.time.get_ticks() - self.last_moved

        # Reset time elapsed if the player has not touched the shopping cart recently
        if time_elapsed > 250:
            time_elapsed = 0
            not_touched_recently = True
        else:
            not_touched_recently = False
            
        # Calculate shopping cart angle based on the player's velocity
        # Align with player's location if the player player has not touched the cart recently
        if player.x_velocity > 0 and player.y_velocity == 0: # going right
            self.angle = 0.0

            if not_touched_recently:
                self.x = player.x + player.width
                self.y = player.y
        elif player.x_velocity < 0 and player.y_velocity == 0: # going left
            self.angle = 180.0

            if not_touched_recently:
                self.x = player.x - self.width
                self.y = player.y
        elif player.y_velocity > 0 and player.x_velocity == 0: # going down
            self.angle = 270.0

            if not_touched_recently:
                self.x = player.x
                self.y = player.y + player.height
        elif player.y_velocity < 0 and player.x_velocity == 0: # going up
            self.angle = 90.0

            if not_touched_recently:
                self.x = player.x
                self.y = player.y - self.height - player.height * 0.75
        
        # Similar to MovableEntity.update_position()
        self.x += player.x_velocity * time_elapsed / 1000.0
        self.y += player.y_velocity * time_elapsed / 1000.0

        self.last_moved = pygame.time.get_ticks()
        
    # TO DO: open inventory menu
    def handle_interaction(self, player):
        pass

    # Draws texture to x and y position on window in relation to the camera,
    # facing the angle calculated from the player
    def render(self, window, camera_x, camera_y):
        window.blit(pygame.transform.rotate(pygame.transform.scale(self.texture, 
            (self.width, self.height)), self.angle), (self.x - camera_x, self.y - camera_y))


class Pet(Item):
    # Default values:

    # Dimensions
    default_width = 75 # px
    default_height = 25 # px

    interaction_message = 'pet (E)'

    def __init__(self, x, y, texture):
        # Set name later
        Item.__init__(self, x, y, Pet.default_width, Pet.default_height,
            texture, ItemType.PET, '', Pet.interaction_message)

    def handle_collision(self, player):
        Item.handle_collision(self, player)

    # TO DO: add petting
    def handle_interaction(self, player):
        pass