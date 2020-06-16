import pygame

from enums import TextureType

class Renderer:
    # Initializes pygame, window, and camera
    def __init__(self):
        
        # Screen dimensions
        self.screen_width = 1280
        self.screen_height = 720

        pygame.init()

        self.window = pygame.display.set_mode(
            (self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("Covid Simulator")

        self.camera = Camera()

        # Background color
        self.background = (70, 89, 69)

    def render(self, entities):
        # Clear screen
        self.window.fill(self.background)

        # Update camera position
        self.camera.scroll(
            self.screen_width,
            self.screen_height,
            entities.player.x,
            entities.player.y,
            entities.player.width,
            entities.player.height)

        # Render entities:

        for location in entities.locations:
            location.render(self.window, self.camera.x, self.camera.y)

        for item in entities.items:
            item.render(self.window, self.camera.x, self.camera.y)

        # Render player:
        entities.player.render(self.window, self.camera.x, self.camera.y)

        # Update the window
        pygame.display.update()

    # TO DO: implement later
    def resize_window(self, new_width, new_height):
        pass

    # Quits pygame
    def close(self):
        pygame.quit()

class Camera:
    def __init__(self):
        # Position: px
        self.x = 0.0
        self.y = 0.0

    # Centers the camera's position on the player's location
    # based on the screen dimensions
    def scroll(self, screen_width, screen_height,
        x, y, width, height):
        player_center_x = x + width / 2
        player_center_y = y + height / 2

        self.x = player_center_x - screen_width / 2
        self.y = player_center_y - screen_height / 2

class Textures:
    def __init__(self):
        # Maps texture type to pygame texture
        # <int, pygame texture>
        self.textures = {}

    # Returns the texture corresponding to the texture type
    # TO DO: catch exception if texture type does not exist
    def get(self, texture_type):
        return self.textures.get(texture_type)

    # Creates pygame texture from PNG file
    def create(self, filename):
        return pygame.image.load(filename).convert_alpha()

    # Loads all textures into dictionary from files
    def load(self):
        # Player
        self.textures[TextureType.PLAYER] = self.create('textures/player.png')

        # Characters

        # Locations
        self.textures[TextureType.HOUSE] = self.create('textures/house.png')
        self.textures[TextureType.STORE] = self.create('textures/store.png')

        # Supplies

        # Items

        # Vehicles
        self.textures[TextureType.VEHICLE] = self.create('textures/vehicle.png')

