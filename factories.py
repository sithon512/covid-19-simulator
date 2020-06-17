import pygame

from enums import TextureType, LocationType, ItemType, SupplyType, PetType, CharacterType
from locations import Location, House, GroceryStore
from player import Player
from items import Item, Vehicle, Sink, ShoppingCart, Supply
from npcs import Character, Pet

# Abstract Factories:

class ICharacterFactory:
	def __init__(self):
		pass

	# Abstract create method - returns newly created character object
	def create(self, x, y, name, textures):
		pass

class CharacterFactory:
	def __init__(self):
		# Maps character type to factory
		# <CharacterType, ICharacterFactory>
		self.factories = {}

		self.factories[CharacterType.PET] = PetFactory()

	# Returns newly created character from corresponding factory
	def create(self, type, x, y, name, textures):
		return self.factories.get(type).create(x, y, name, textures)

class PetFactory(ICharacterFactory):
	def create(self, x, y, name, textures):
		return Pet(x, y, name, pygame.transform.scale(textures.get(TextureType.DOG),
			(Pet.default_width, Pet.default_height)))

class ILocationFactory:
	def __init__(self):
		pass
	
	# Abstract create method - returns newly created location object
	def create(self, x, y, textures):
		pass

class LocationFactory:
	def __init__(self):
		# Maps location type to factory
		# <LocationType, ILocationFactory>
		self.factories = {}

		self.factories[LocationType.HOUSE] = HouseFactory()
		self.factories[LocationType.GROCERY_STORE] = GroceryStoreFactory()

	# Returns newly created location from corresponding factory
	def create(self, type, x, y, textures):
		return self.factories.get(type).create(x, y, textures)
	
class HouseFactory(ILocationFactory):
	def create(self, x, y, textures):
		return House(x, y, House.default_width, House.default_height,
			pygame.transform.scale(textures.get(TextureType.HOUSE),
			(House.default_width, House.default_height)))
		
class GroceryStoreFactory(ILocationFactory):
	def create(self, x, y, textures):
		return GroceryStore(x, y, GroceryStore.default_width, GroceryStore.default_height,
			pygame.transform.scale(textures.get(TextureType.STORE),
			(GroceryStore.default_width, GroceryStore.default_height)))

class IItemFactory:
	def __init__(self):
		pass

	# Abstract create method - returns newly created item object
	def create(self, x, y, name, textures):
		pass

class ItemFactory:
	def __init__(self):
		# Maps item type to factory
		# <ItemType, IItemFactory>
		self.factories = {}

		self.factories[ItemType.VEHICLE] = VehicleFactory()
		self.factories[ItemType.SINK] = SinkFactory()
		self.factories[ItemType.SHOPPING_CART] = ShoppingCartFactory()

	# Returns newly created item from corresponding factory
	def create(self, type, x, y, textures):
		return self.factories.get(type).create(x, y, textures)
	
class VehicleFactory(IItemFactory):
	def create(self, x, y, textures):
		return Vehicle(x, y, pygame.transform.scale(textures.get(TextureType.VEHICLE),
			(Vehicle.default_width, Vehicle.default_height)))

class SinkFactory(IItemFactory):
	def create(self, x, y, textures):
		return Sink(x, y, pygame.transform.scale(textures.get(TextureType.SINK),
			(Sink.default_width, Sink.default_height)))
	
class ShoppingCartFactory(IItemFactory):
	def create(self, x, y, textures):
		return ShoppingCart(x, y, pygame.transform.scale(textures.get(TextureType.SHOPPING_CART),
			(ShoppingCart.default_width, ShoppingCart.default_height)))

class ISupplyFactory:
	def __init__(self):
		pass

	# Abstract create method - returns newly created supply object
	def create(self, x, y, name, textures):
		pass

class SupplyFactory:
	def __init__(self):
		# Maps supply type to factory
		# <SupplyType, ISupplyFactory>
		self.factories = {}

		self.factories[SupplyType.FOOD] = FoodFactory()
		self.factories[SupplyType.SOAP] = SoapFactory()
		self.factories[SupplyType.HAND_SANITIZER] = HandSanitizerFactory()
		self.factories[SupplyType.TOILET_PAPER] = ToiletPaperFactory()
		self.factories[SupplyType.MASK] = MaskFactory()
		self.factories[SupplyType.PET_SUPPLIES] = PetSuppliesFactory()

	# Returns newly created supply from corresponding factory
	def create(self, type, x, y, textures):
		return self.factories.get(type).create(x, y, textures)
	
class FoodFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Food(x, y, (Food.default_width, Food.default_height),
			pygame.transform.scale(textures.get(TextureType.FOOD)), 
			SupplyType.FOOD, "Food")

class SoapFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Soap(x, y, (Soap.default_width, Soap.default_height),
			pygame.transform.scale(textures.get(TextureType.SOAP)), 
			SupplyType.SOAP, "Soap")

class HandSanitizerFactory(ILocationFactory):
	def create(self, x, y, textures):
		return HandSanitizer(x, y, (HandSanitizer.default_width, HandSanitizer.default_height),
			pygame.transform.scale(textures.get(TextureType.HAND_SANITIZER)), 
			SupplyType.HAND_SANITIZER, "Hand Sanitizer")

class ToiletPaperFactory(ILocationFactory):
	def create(self, x, y, textures):
		return ToiletPaper(x, y, (ToiletPaper.default_width, ToiletPaper.default_height),
			pygame.transform.scale(textures.get(TextureType.TOILET_PAPER)), 
			SupplyType.TOILET_PAPER, "Toilet Paper")

class MaskFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Mask(x, y, (Mask.default_width, Mask.default_height),
			pygame.transform.scale(textures.get(TextureType.MASK)), 
			SupplyType.MASK, "Mask")

class PetSuppliesFactory(ILocationFactory):
	def create(self, x, y, textures):
		return PetSupplies(x, y, (PetSupplies.default_width, PetSupplies.default_height),
			pygame.transform.scale(textures.get(TextureType.PET_SUPPLIES)), 
			SupplyType.PET_SUPPLIES, "Pet Supplies")