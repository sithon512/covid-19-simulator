import pygame, math

from enums import LocationType, ItemType

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

class Player(MovableEntity):
    # Default values:

    # Dimensions
    default_width = 50 # px
    default_height = 50 # px

    # Maximum speeds
    walking_speed = 100 # px / s
    running_speed = 250 # px / s

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

        # Items that the player is currently colliding with
        self.nearby_items = []

        # Vehicle the player is driving
        # None if the player is not currently driving
        self.vehicle = None

    # Moves the player based on their velocity
    def update(self):
        if self.vehicle != None:
            self.drive()

        self.update_position()

    # Handles interact action
    def interact(self):
        for item in self.nearby_items:
            item.handle_interaction(self)

        # Nearby items are updated every frame
        self.nearby_items.clear()

    # Adjusts vehicle to the player
    def drive(self):
        self.vehicle.x = self.x
        self.vehicle.y = self.y

    # Adjusts player's velocity based on the parameters
    # Caps each component to player's maximum speed
    # Toggles maximum speed based on whether the player is driving, running, or walking
    # Resets if there is no change
    def adjust_velocity(self, x_change, y_change, running):

        # Toggle maximum speed
        if self.vehicle != None and running: # Vehicle turbo
            self.speed = Vehicle.turbo_speed
        elif self.vehicle != None: # Vehicle regular
            self.speed = Vehicle.regular_speed
        elif running: # Running
            self.speed = Player.running_speed
        else: # Walking
            self.speed = Player.walking_speed

        self.x_velocity += x_change * 0.10 * self.speed
        self.y_velocity += y_change * 0.10 * self.speed

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

    # Does not render player if they are driving
    def render(self, window, camera_x, camera_y):
        if self.vehicle == None:
            MovableEntity.render(self, window, camera_x, camera_y)

    # Adds item to the player's nearby items list
    def add_nearby_item(self, item):
        self.nearby_items.append(item)

    # TO DO: add methods for adding and removing supplies

class Location(Entity):
    def __init__(self, x, y, width, height, texture, name, type):
        Entity.__init__(self, x, y, width, height, texture)

        self.name = name
        self.type = type

class House(Location):
    def __init__(self, x, y, width, height, texture):
        Location.__init__(self, x, y, width, height, texture,
            "House", LocationType.HOUSE)

class GroceryStore(Location):
    def __init__(self, x, y, width, height, texture):
        Location.__init__(self, x, y, width, height, texture,
            "Grocery Store", LocationType.GROCERY_STORE)

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
    interaction_message = 'open inventory (E)'

    def __init__(self, x, y, texture):
        Item.__init__(self, x, y, ShoppingCart.default_width, ShoppingCart.default_height,
            texture, ItemType.SHOPPING_CART, ShoppingCart.name, ShoppingCart.interaction_message)

        # Last time the player moved the cart
        self.last_moved = pygame.time.get_ticks()

    # Pushes the cart in the player's velocity direction
    def handle_collision(self, player):
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

# Contains all entities
class Entities:
    def __init__(self):
        self.player = Player()

        # TO DO: add lists locations, characters, pets, and supplies

        self.locations = []
        self.items = []

    # Add Methods:
    # TO DO: add methods for adding locations, characters, pets, and supplies

    # Creates and adds new location of type
    def add_location(self, type, x, y, width, height, texture):
        # TO DO: turn this into an abstract factory
        if type == LocationType.HOUSE:
            location = House(x, y, width, height,
                pygame.transform.scale(texture, (width, height)))
        elif type == LocationType.GROCERY_STORE:
            location = GroceryStore(x, y, width, height,
                pygame.transform.scale(texture, (width, height)))
        else:
            return

        self.locations.append(location)
        print("[Info] Created location " + str(type) + " at (" + str(x) + ", " + str(y) + ")")

    # Creates and add new item of type
    def add_item(self, type, x, y, texture):
        # TO DO: turn this into an abstract factory
        if type == ItemType.VEHICLE:
            item = Vehicle(x, y, pygame.transform.scale(texture, 
                (Vehicle.default_width, Vehicle.default_height)))
        elif type == ItemType.SINK:
            item = Sink(x, y, pygame.transform.scale(texture, 
                (Sink.default_width, Sink.default_height)))
        elif type == ItemType.SHOPPING_CART:
            item = ShoppingCart(x, y, pygame.transform.scale(texture, 
                (ShoppingCart.default_width, ShoppingCart.default_height)))
        else:
            return
        
        self.items.append(item)
        print("[Info] Created item " + str(type) + " at (" + str(x) + ", " + str(y) + ")")

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
        self.player_interacted = False

        # Text to be displayed in the user interface
        self.location_text = '' # located at the top
        self.interaction_text = '' # located at the bottom

        # Player's current meters
        self.current_money = 0
        self.current_health = 0
        self.current_morale = 0

    def update_entities(self, entities):
        # Handle location collisions
        self.location_text = ''
        for location in entities.locations:
            if location.check_collision(entities.player):
                self.location_text = location.name

        # Handle item collisions
        self.interaction_text = ''
        for item in entities.items:
            if item.check_collision(entities.player):
                item.handle_collision(entities.player)
                entities.player.add_nearby_item(item)
                self.interaction_text = item.name + ": " + item.interaction_message

        # Update player
        entities.player.adjust_velocity(
            self.player_x_change,
            self.player_y_change,
            self.player_running)
        
        if self.player_interacted:
            entities.player.interact()
        
        entities.player.update()
        self.current_money = entities.player.money
        self.current_health = entities.player.health
        self.current_morale = entities.player.morale

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

    # Interface between the controller and the user interface for player interaction
    def interact_player(self):
        self.player_interacted = True

    # Interface between the controller and the user interface for updating messages
    def update_messages(self, middle_text, info_text):
        # Update location and interaction messages
        middle_text.set_top(self.location_text)
        middle_text.set_bottom(self.interaction_text)

        # Update info display
        info_text.set(self.current_money, self.current_health, self.current_morale)

    # Resets values that are only valid for each frame
    def reset_values(self):
        self.player_x_change = 0
        self.player_y_change = 0
        self.player_running = False
        self.player_interacted = False
