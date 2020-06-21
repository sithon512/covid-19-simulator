#from mixer.backend.sqlalchemy import Mixer

import unittest

#mixer = Mixer(session=session, commit=True)

from entity import Entity, MovableEntity
from player import Player
from items import Item, Vehicle, Sink, ShoppingCart, Supply

class ItemTests(unittest.TestCase):
    # Initializes player at position (0, 0) and
    # item at position (0, 0) and 50x50 dimensions
    player = Player()
    item = Item(0, 0, 50, 50)

    # Tests that player movement is blocked or not blocked properly
    # when the player is moving towards or away from the item
    def check_handle_collision(self):
        # Player moving towards item from the top
        self.player.y = self.item.y - self.item.height / 2
        self.player.y_velocity = self.player.speed

        self.item.handle_collision(self.player)
        self.assertTrue(self.player.movement_blocked)

        # Player moving away from the item from the top
        self.player.y = self.item.y - self.item.height / 2
        self.player.y_velocity = -self.player.speed

        self.item.handle_collision(self.player)
        self.assertFalse(self.player.movement_blocked)

        # Player moving away from the item from the left
        self.player.x = self.item.x + self.item.height / 2
        self.player.x_velocity = -self.player.speed

        self.item.handle_collision(self.player)
        self.assertFalse(self.player.movement_blocked)

        # Player moving away towards the item from the right
        self.player.x = self.item.x - self.item.height / 2
        self.player.x_velocity = -self.player.speed

        self.item.handle_collision(self.player)
        self.assertTrue(self.player.movement_blocked)

class VehicleTests(unittest.TestCase):
    # Initializes player and vehicle at position (0, 0)
    player = Player()
    vehicle = Vehicle(0, 0, None)

    # Tests that vehicle adjusts to player and vehicle undergoes
    # proper fuel depletion
    def test_drive(self):
        # Test that vehicle adjusts to player's new position
        self.player.x = 500
        self.player.y = 500

        self.vehicle.drive(self.player)

        self.assertIs(self.player.x, self.vehicle.x)
        self.assertIs(self.player.y, self.vehicle.y)

        # Test that vehicle's fuel decreased
        self.assertTrue(self.vehicle.current_fuel < self.vehicle.max_fuel)

        # Test that vehicle's fuel gets depleted
        self.player.x = 10000000
        self.player.y = 10000000

        # Deplete fuel
        self.vehicle.drive(self.player)
        vehicle_x_after_depleted_gas = self.vehicle.x
        vehicle_y_after_depleted_gas = self.vehicle.y

        # Move player to a different location
        self.player.x = 15000000
        self.player.y = 15000000

        # Check that vehicle did not move since fuel is empty
        self.vehicle.drive(self.player)
        self.assertEqual(self.vehicle.x, vehicle_x_after_depleted_gas)
        self.assertEqual(self.vehicle.y, vehicle_y_after_depleted_gas)

    # Tests player entering and exiting vehicle
    def test_handle_interaction(self):
        # Test that vehicle is attached to player and that
        # message is added when player attaches to vehicle
        self.vehicle.attached = False
        self.vehicle.last_interaction = -1000

        messages = []
        self.vehicle.handle_interaction(self.player, messages)
        
        self.assertEqual(self.vehicle, self.player.vehicle)
        self.assertTrue(len(messages) > 0)

        # Test that vehicle is detached from the player
        self.vehicle.last_interaction = -1000
        self.vehicle.handle_interaction(self.player, messages)
        
        self.assertFalse(self.vehicle.attached)
        self.assertIsNone(self.player.vehicle)

class SinkTests(unittest.TestCase):
    pass

class ShoppingCartTests(unittest.TestCase):
    # Initializes player, item, and shopping cart as positions (0, 0)
    player = Player()
    supply = Supply(0, 0, 0, 0, None, 0, '')
    shopping_cart = ShoppingCart(0, 0, None)

    def test_handle_collision(self):
        # Check that cart is not pushed if player is not running
        self.player.running = False
        self.shopping_cart.handle_collision(self.player)
        self.assertEqual(self.shopping_cart.x, 0)
        self.assertEqual(self.shopping_cart.y, 0)

        # Check that player pushes cart from the x-axis
        self.player.running = True
        self.player.x_velocity = Player.running_speed
        self.shopping_cart.x = 0
        self.shopping_cart.last_moved = 200
        self.shopping_cart.handle_collision(self.player)
        self.assertTrue(abs(self.shopping_cart.x) > 0)

        # Check that player pushes cart from the y-axis
        self.player.running = True
        self.player.y_velocity = Player.running_speed
        self.shopping_cart.x = 0
        self.shopping_cart.last_moved = 200
        self.shopping_cart.handle_collision(self.player)
        self.assertTrue(abs(self.shopping_cart.y) > 0)

        # Check that shopping cart is angled correctly
        # when player is coming from the left
        self.player.x_velocity = self.player.speed
        self.player.y_velocity = 0
        self.shopping_cart.x = 0
        self.shopping_cart.last_moved = 200
        self.shopping_cart.handle_collision(self.player)
        self.assertEqual(self.shopping_cart.angle, 0)

        # Check that shopping cart is angled correctly
        # when player is coming from the bottom
        self.player.x_velocity = 0
        self.player.y_velocity = self.player.speed
        self.shopping_cart.x = 0
        self.shopping_cart.last_moved = 200
        self.shopping_cart.handle_collision(self.player)
        self.assertEqual(self.shopping_cart.angle, 90)

    # Tests player adding items to cart
    def test_handle_interaction(self):
        # Test placing item in cart
        messages = []
        self.player.item_being_carried = self.supply
        self.shopping_cart.last_interaction = -1000
        self.shopping_cart.handle_interaction(self.player, messages)

        self.assertEqual(messages[0], 'Item added to shopping cart')
        self.assertIsNone(self.player.item_being_carried)
        self.assertEqual(self.shopping_cart.items.size, 1)

        # Test that the quantity is now 1
        self.assertEqual(self.shopping_cart.items.supplies[0], 1)

        # Test that the quantity is now 2
        self.player.item_being_carried = self.supply
        self.shopping_cart.last_interaction = -1000
        self.shopping_cart.handle_interaction(self.player, messages)
        self.assertEqual(self.shopping_cart.items.supplies[0], 2)

        # Test total cost after one priced item
        self.supply.price = 5
        self.player.item_being_carried = self.supply
        self.shopping_cart.last_interaction = -1000
        self.shopping_cart.handle_interaction(self.player, messages)
        self.assertEqual(self.shopping_cart.total_cost, 5)

        # Test total cast after two priced items
        self.player.item_being_carried = self.supply
        self.shopping_cart.last_interaction = -1000
        self.shopping_cart.handle_interaction(self.player, messages)
        self.assertEqual(self.shopping_cart.total_cost, 10)

        # Test full shopping cart
        messages = []
        self.shopping_cart.items.size = self.shopping_cart.items.capacity
        self.player.item_being_carried = self.supply
        self.shopping_cart.last_interaction = -1000
        self.shopping_cart.handle_interaction(self.player, messages)
        
        self.assertEqual(messages[0], 'Shopping cart is full')

        # Test that player is still carrying the supply
        self.assertEqual(self.player.item_being_carried, self.supply)

        # Test no items message
        messages = []
        self.player.item_being_carried = None
        self.shopping_cart.last_interaction = -1000
        self.shopping_cart.handle_interaction(self.player, messages)
        self.assertEqual(messages[0], 'Not carrying any items')

class SupplyTests(unittest.TestCase):
    # Initializes player and item as positions (0, 0)
    player = Player()
    supply = Supply(0, 0, 0, 0, None, 0, '')

    def test_carry(self):
        # Test adjustment to player moving up
        self.player.x_velocity = 0
        self.player.y_velocity = -self.player.speed
        self.supply.carry(self.player)

        self.assertEqual(self.supply.x, 
            self.player.x + self.player.width / 2 - self.supply.width / 2)

        self.assertEqual(int(self.supply.y),
            int(self.player.y - self.supply.height * 0.75))

        self.assertEqual(self.supply.angle, 90)

        # Test adjustment to player moving left
        self.reset_supply_position()
        self.player.x_velocity = -self.player.speed
        self.player.y_velocity = 0
        self.supply.carry(self.player)

        self.assertEqual(self.supply.x, 
            self.player.x - self.supply.width)

        self.assertEqual(self.supply.angle, 180)

        # Test adjustment to player moving down diagonally
        self.reset_supply_position()
        self.player.x_velocity = self.player.speed
        self.player.y_velocity = self.player.speed
        self.player.last_moved = -1000
        self.player.update_position()
        self.supply.carry(self.player)

        self.assertEqual(self.supply.x, 
            self.player.x + self.player.width / 2 - self.supply.width / 2)

    # Resets the supply's position to (0, 0)
    def reset_supply_position(self):
        self.supply.x = 0
        self.supply.y = 0

class DoorTests(unittest.TestCase):
    pass

class SelfCheckoutTests(unittest.TestCase):
    pass

class ClosetTests(unittest.TestCase):
    pass

class EntityTests(unittest.TestCase):
    # Initialize entity objects at position (0, 0) with 50x50 dimensions
    first_entity = Entity(0, 0, 50, 50)
    second_entity = Entity(0, 0, 50, 50)

    def test_check_collision(self):
        # Entities right over top each other
        self.assertTrue(self.first_entity.check_collision(self.second_entity))

        # Entities collision from the top
        self.second_entity.y = self.first_entity.y\
            - self.first_entity.height / 2
        self.assertTrue(self.first_entity.check_collision(self.second_entity))

        # Entities collision from the bottom
        self.second_entity.y = self.first_entity.y\
            + self.first_entity.height / 2
        self.assertTrue(self.first_entity.check_collision(self.second_entity))
        
        # Entities collision from the left
        self.second_entity.y = 0
        self.second_entity.x = self.first_entity.x\
            - self.first_entity.height / 2
        self.assertTrue(self.first_entity.check_collision(self.second_entity))

        # Entities collision from the right
        self.second_entity.x = self.first_entity.x\
            + self.first_entity.height / 2
        self.assertTrue(self.first_entity.check_collision(self.second_entity))

        # Entities away from each other on the x axis
        self.second_entity.x = 100
        self.assertFalse(self.first_entity.check_collision(self.second_entity))

        # Entities away from each other on the y axis
        self.second_entity.x = 0
        self.second_entity.y = 100
        self.assertFalse(self.first_entity.check_collision(self.second_entity))

        # Entities away from each other on both axies
        self.second_entity.x = 100
        self.second_entity.y = 100
        self.assertFalse(self.first_entity.check_collision(self.second_entity))

        # Entities right next to each other, but not touching
        self.second_entity.x = self.first_entity.x + self.first_entity.width
        self.assertFalse(self.first_entity.check_collision(self.second_entity))

    def test_swap_dimensions(self):
        # Swap to opposite values
        width = self.first_entity.width
        height = self.first_entity.height

        self.first_entity.swap_dimensions(False)

        self.assertEqual(self.first_entity.width, height)
        self.assertEqual(self.first_entity.height, width)

        # Swap to original values
        self.first_entity.swap_dimensions(True)
        self.assertEqual(self.first_entity.width, width)
        self.assertEqual(self.first_entity.height, height)

class MovableEntityTests(unittest.TestCase):
    # Initialize moveable entity at position (0, 0) with 50x50 dimensions,
    # and speed of 50
    movable_entity = MovableEntity(0, 0, 50, 50, None, 50)
    
    def test_update_position(self):
        # Test movement on the x axis
        self.reset_entity_position()
        self.movable_entity.x_velocity = self.movable_entity.speed
        self.movable_entity.y_velocity = 0

        self.movable_entity.last_moved = -1000
        self.movable_entity.update_position()

        # Entity should have moved for one second at a speed of 50 px / s,
        # so entity x-position should be 50
        self.assertIs(int(self.movable_entity.x), 50)

        # Test movement on the y axis
        self.reset_entity_position()
        self.movable_entity.x_velocity = 0
        self.movable_entity.y_velocity = self.movable_entity.speed

        self.movable_entity.last_moved = -1000
        self.movable_entity.update_position()

        self.assertIs(int(self.movable_entity.y), 50)

        # Test movement on both the x and y axis simultaneously
        self.reset_entity_position()
        self.movable_entity.x_velocity = self.movable_entity.speed
        self.movable_entity.y_velocity = self.movable_entity.speed

        self.movable_entity.last_moved = -1000
        self.movable_entity.update_position()

        self.assertIs(int(self.movable_entity.x), 50)
        self.assertIs(int(self.movable_entity.y), 50)

    # Tests that entity does not move if movement is blocked
    def test_block_movement(self):
        self.movable_entity.x_velocity = self.movable_entity.speed
        self.movable_entity.y_velocity = self.movable_entity.speed

        self.movable_entity.block_movement()
        self.movable_entity.last_moved = -1000

        self.movable_entity.update_position()

        self.assertIs(int(self.movable_entity.x), 0)
        self.assertIs(int(self.movable_entity.y), 0)

    # Tests that entity collides with another entity after moving
    # to the latter's location
    def test_check_collision(self):
        other_entity = Entity(40, 0, 50, 50)

        self.reset_entity_position()
        self.movable_entity.x_velocity = self.movable_entity.speed
        self.movable_entity.y_velocity = 0

        self.movable_entity.last_moved = -1000
        self.movable_entity.update_position()

        self.assertTrue(self.movable_entity.check_collision(other_entity))

    # Resets the entity's position to (0, 0)
    def reset_entity_position(self):
        self.movable_entity.x = 0
        self.movable_entity.y = 0

class LocationTests(unittest.TestCase):
    pass

class PetTests(unittest.TestCase):
    pass

class ShopperTests(unittest.TestCase):
    pass

class PlayerTests(unittest.TestCase):
    pass

class InventoryTests(unittest.TestCase):
    pass

if __name__ == '__main__':
    unittest.main()