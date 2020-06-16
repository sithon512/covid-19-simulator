import pygame

class UserInterface:
    # Initializes fonts and messages
    def __init__(self):
        pygame.font.init()
        
        # Fonts of various sizes
        self.small_text = pygame.font.SysFont('Courier New', 11)
        self.medium_text = pygame.font.SysFont('Courier New', 12)
        self.large_text = pygame.font.SysFont('Courier New', 14)

        # 
        self.middle_text = MiddleText()

        self.last_interaction = pygame.time.get_ticks()

    # Handles mouse and keyboard input
    # Returns false if the user quits the game
    def handle_input(self, controller):
        for event in pygame.event.get():
            # User pressed 'X' button
            if event.type == pygame.QUIT:
                print("[Info] User closed the game window")
                return False

        self.handle_keyboard(controller)

        controller.update_messages(self.middle_text)

        return True

    def handle_keyboard(self, controller):
        self.handle_player_movement(controller)

    # Handles player movement with W, A, S, D / arrow keys + Shift and
    # the interact action with E
    def handle_player_movement(self, controller):
        # Gets current keys pressed
        keystate = pygame.key.get_pressed()

        # Reset movement each frame
        up = False
        down = False
        left = False
        right = False
        running = False

        # W, A, S, D and arrow keys
        # move player up, left, down, and right, respectively
        if keystate[pygame.K_w] or keystate[pygame.K_UP]:
            up = True
        if keystate[pygame.K_a] or keystate[pygame.K_LEFT]:
            left = True
        if keystate[pygame.K_s] or keystate[pygame.K_DOWN]:
            down = True
        if keystate[pygame.K_d] or keystate[pygame.K_RIGHT]:
            right = True

        # Shift key to run
        if keystate[pygame.K_LSHIFT] or keystate[pygame.K_RSHIFT]:
            running = True

        # E for player interact action
        if keystate[pygame.K_e]:
            controller.interact_player()
        
        controller.move_player(up, down, left, right, running)
    
    # TO DO: create methods for handling mouse click and hover

    def render(self, window):
        self.middle_text.render(window, self.medium_text, self.large_text)

class MiddleText:
    # Y-distance between top/bottom of screen
    y_offset = 15

    def __init__(self):
        self.top_text = ''
        self.bottom_text = ''

        self.text_color = (0, 0, 0)

    # Creates texture from the text and renders centered on the screen
    def render(self, window, medium_text, large_text):
        top_text_surface = large_text.render(self.top_text, False, self.text_color)
        bottom_text_surface = medium_text.render(self.bottom_text, False, self.text_color)

        top_text_x = self.center_text(window.get_width(), self.top_text)
        bottom_text_x = self.center_text(window.get_width(), self.bottom_text)

        # Render the created surfaces
        window.blit(top_text_surface, (top_text_x, MiddleText.y_offset))

        window.blit(bottom_text_surface, (bottom_text_x, 
            window.get_height() - MiddleText.y_offset - bottom_text_surface.get_height()))

    # Returns x-position for text to be centered within the screen width
    def center_text(self, screen_width, text):
        return screen_width / 2.0

    # Sets the top text
    def set_top_text(self, new_text):
        self.top_text = new_text

    # Sets the bottom text
    def set_bottom_text(self, new_text):
        self.bottom_text = new_text