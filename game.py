import pygame

from renderer import Renderer, Camera, Textures
from entities import Entities, Controller
from ui import UserInterface
from enums import TextureType, LocationType, ItemType, PetType

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

        # For average FPS calculation
        frames = 0
        last_frame = pygame.time.get_ticks()

        # Game loop:
        while running:
            # 1. Handle input from the user interface
            screen_dimensions = [self.renderer.screen_width, self.renderer.screen_height]
            running = self.user_interface.handle_input(self.controller, screen_dimensions)

            # 2. Update entities from the controller
            self.controller.update_entities(self.entities)

            # 3. Update screen from the renderer
            self.renderer.render(self.entities, self.user_interface, screen_dimensions)

            # Average FPS for performance profiling, prints every 10 seconds
            frames += 1
            if pygame.time.get_ticks() - last_frame > 10000:
                print("[Debug] Average FPS: " + str(frames / 10.0))
                frames = 0
                last_frame = pygame.time.get_ticks()

        self.close()

    # Closes the game renderer
    def close(self):
        self.renderer.close()

    # Initializes the locations
    def init_map(self):
        self.add_house()
        self.add_grocery_store()
        self.add_other_items()

    # Adds house with sink
    def add_house(self):
        house_width = 750
        house_height = 500
        house_x = -house_width / 2
        house_y = -house_height / 2
        self.entities.add_location(
            LocationType.HOUSE,
            house_x,
            house_y,
            house_width,
            house_height,
            self.textures.get(TextureType.HOUSE))

        # Add sink
        sink_x = house_x + house_width / 2
        sink_y = house_y + house_height - 40
        self.entities.add_item(
            ItemType.SINK,
            sink_x,
            sink_y,
            self.textures.get(TextureType.SINK))

        # Add pet
        pet_x = house_x + house_width / 2
        pet_y = house_y + house_height / 3
        self.entities.add_pet(
            PetType.DOG,
            pet_x,
            pet_y,
            self.textures.get(TextureType.DOG))
    
    # Adds grocery store with shopping cart
    def add_grocery_store(self):
        store_x = 3000
        store_y = 500
        store_width = 2000
        store_height = 2000
        self.entities.add_location(
            LocationType.GROCERY_STORE,
            store_x,
            store_y,
            store_width,
            store_height,
            self.textures.get(TextureType.STORE))
        
        # Add shopping carts
        self.entities.add_item(
            ItemType.SHOPPING_CART,
            store_x + store_width / 2,
            store_y + store_height / 2,
            self.textures.get(TextureType.SHOPPING_CART))

        # Add shopping cart near house for testing purposes
        self.entities.add_item(
            ItemType.SHOPPING_CART,
            250,
            400,
            self.textures.get(TextureType.SHOPPING_CART))

    # Adds vehicles
    def add_other_items(self):
        vehicle_x = 700
        vehicle_y = 100
        self.entities.add_item(
            ItemType.VEHICLE,
            vehicle_x,
            vehicle_y,
            self.textures.get(TextureType.VEHICLE))


# Testing:
starting_money = 1000
starting_health = 100
starting_morale = 70

game = Game(starting_money, starting_health, starting_morale)
game.run()