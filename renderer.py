import pygame

from enums import TextureType

class Renderer:
    # Initializes pygame and window
    def __init__(self):
        
        # Screen dimensions
        self.screen_width = 1280
        self.screen_height = 720

        pygame.init()

        # Initialize window
        self.window = pygame.display.set_mode(
            (self.screen_width, self.screen_height))

        # Window name
        pygame.display.set_caption("Covid Simulator")



    def render(self, entities):
        # Clear screen
        self.window.fill((255, 255, 255))

        # Render entities:

        # Render player
        entities.player.render(self.window)

        # Update the window
        pygame.display.update()

    # Quits pygame
    def close(self):
        pygame.quit()

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
        return pygame.image.load(filename)

    # Loads all textures into dictionary from files
    def load(self):
        # Player
        self.textures[TextureType.PLAYER] = self.create('textures/player.png')

        # Characters

        # Locations

        # Supplies

        # Items
