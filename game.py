import pygame

from renderer import Renderer, Camera, Textures
from entities import Entities, Controller
from ui import UserInterface
from enums import TextureType, LocationType

class Game:
    # Parameters: starting values for money, health, and morale
    def __init__(self, money, health, morale):
        # Initialize renderer first because it starts pygame
        self.renderer = Renderer()

        self.textures = Textures()
        self.textures.load()

        self.user_interface = UserInterface()
        self.controller = Controller()
        self.entities = Entities()

        self.entities.init_player(50, 50, 
            self.textures.get(TextureType.PLAYER), money, health, morale)

        self.init_map()

    def run(self):
        running = True

        # Game loop:
        while running:
            # 1. Handle input from the user interface
            running = self.user_interface.handle_input(self.controller)

            # 2. Update entities from the controller
            self.controller.update_entities(self.entities)

            # 3. Update screen from the renderer
            self.renderer.render(self.entities)

        self.close()

    # Closes the game renderer
    def close(self):
        self.renderer.close()

    # Initializes the locations
    def init_map(self):
        # Add house
        house_width = 1000
        house_height = 750
        house_x = -house_width / 2
        house_y = -house_height / 2
        self.entities.add_location(
            LocationType.HOUSE,
            house_x,
            house_y,
            house_width,
            house_height,
            self.textures.get(TextureType.HOUSE))

        # Add grocery store(s)
        store_x = house_x + 2000
        store_y = house_y + 500
        store_width = 2000
        store_height = 2000
        self.entities.add_location(
            LocationType.GROCERY_STORE,
            store_x,
            store_y,
            store_width,
            store_height,
            self.textures.get(TextureType.STORE))
        

# Testing:
starting_money = 1000
starting_health = 100
starting_morale = 100

game = Game(starting_money, starting_health, starting_morale)
game.run()