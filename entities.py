import pygame, math

from enums import LocationType, ItemType, PetType

from locations import Location, House, GroceryStore
from player import Player
from items import Item, Vehicle, Sink, ShoppingCart
from npcs import Character, Pet

# Contains all entities
class Entities:
    def __init__(self):
        self.player = Player()

        # TO DO: add lists locations, characters, pets, and supplies

        self.locations = []
        self.items = []
        self.characters = []

    # Add Methods:

    # Creates and adds new location of parameter type
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

    # Creates and adds new item of parameter type
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

    # Creates and adds new pet of parameter type
    def add_pet(self, type, x, y, texture):
        # TO DO: turn this into an abstract factory
        if type == PetType.DOG:
            pet = Pet(x, y, pygame.transform.scale(texture, 
                (Pet.default_width, Pet.default_height)))
            pet.name = "Dog"
        else:
            return

        self.characters.append(pet)
        print("[Info] Created pet " + str(type) + " at (" + str(x) + ", " + str(y) + ")")

    # Remove Methods:

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
        self.messages = [] # message stack

        # Player's current meters
        self.current_money = 0
        self.current_health = 0
        self.current_morale = 0

    def update_entities(self, entities):
        # Handle location collisions
        for location in entities.locations:
            if location.check_collision(entities.player):
                self.location_text = location.name

        # Handle item collisions/interactions
        for item in entities.items:
            if item.check_collision(entities.player):
                item.handle_collision(entities.player)
                entities.player.add_nearby_item(item)
                self.interaction_text = item.name + ": " + item.interaction_message

        # Handle character collisions/interactions
        for character in entities.characters:
            if character.check_collision(entities.player):
                # TO DO: add close proximity instead of just collision
                character.handle_collision(entities.player)
                entities.player.add_nearby_character(character)
                self.interaction_text = character.name + ": " + character.interaction_message

        # Update player
        entities.player.adjust_velocity(
            self.player_x_change,
            self.player_y_change,
            self.player_running)
        
        if self.player_interacted:
            entities.player.interact(self.messages)
        
        entities.player.update()
        
        # Nearby items and characters are updated every frame
        entities.player.reset_nearby_lists()

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
    def update_messages(self, middle_text, info_text, message_stack):
        # Update location and interaction messages
        middle_text.set_top(self.location_text)
        self.location_text = ''

        middle_text.set_bottom(self.interaction_text)
        self.interaction_text = ''

        # Update message stack
        message_stack.insert(self.messages)
        self.messages.clear()

        # Update info display
        info_text.set(self.current_money, self.current_health, self.current_morale)

    # Resets values that are only valid for each frame
    def reset_values(self):
        self.player_x_change = 0
        self.player_y_change = 0
        self.player_running = False
        self.player_interacted = False