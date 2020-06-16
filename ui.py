import pygame

class UserInterface:
    def __init__(self):
        self.last_interaction = pygame.time.get_ticks()

    # Handles mouse and keyboard input
    # Returns false if the user quits the game
    def handle_input(self, controller):
        for event in pygame.event.get():
            # User pressed 'X' button
            if event.type == pygame.QUIT:
                print("User closed the game window")
                return False

        self.handle_keyboard(controller)

        return True

    def handle_keyboard(self, controller):
        self.handle_player_movement(controller)

    def handle_player_movement(self, controller):
        # Gets current keys pressed
        keystate = pygame.key.get_pressed()

        # Reset movement each frame
        up = False
        left = False
        down = False
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