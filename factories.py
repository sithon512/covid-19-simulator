import pygame

from enums import TextureType, LocationType, ItemType, SupplyType, PetType, CharacterType, MapElementType
from locations import Location, House, GroceryStore, Aisle
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
	def create(self, type, x, y, size, textures):
		return self.factories.get(type).create(x, y, size, textures)
	
class HouseFactory(ILocationFactory):
	def create(self, x, y, size, textures):
		return House(x, y, House.default_width, House.default_height,
			pygame.transform.scale(textures.get(TextureType.HOUSE),
			(House.default_width, House.default_height)))
		
class GroceryStoreFactory(ILocationFactory):
	def create(self, x, y, size, textures):
		width = int(GroceryStore.default_width * size)
		height = int(GroceryStore.default_height * size)

		return GroceryStore(x, y, width, height,
			pygame.transform.scale(textures.get(TextureType.STORE),
			(width, height)))

class IMapElementFactory:
	def __init__(self):
		pass
	
	# Abstract create method - returns newly created map element object
	def create(self, x, y, width, height, textures):
		pass

class MapElementFactory:
	def __init__(self):
		# Maps map element type to factory
		# <MapElementType, IMapElementFactory>
		self.factories = {}

		self.factories[MapElementType.AISLE] = AisleFactory()

	# Returns newly created map element from corresponding factory
	def create(self, type, x, y, width, height, textures):
		return self.factories.get(type).create(x, y, width, height, textures)
	
class AisleFactory(IMapElementFactory):
	def create(self, x, y, width, height, textures):
		return Aisle(x, y, width, height,
			pygame.transform.scale(textures.get(TextureType.AISLE),
			(width, height)))

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
		return Supply(x, y, Supply.default_width, Supply.default_height,
			pygame.transform.scale(textures.get(TextureType.FOOD), 
			(Supply.default_width, Supply.default_height)), 
			SupplyType.FOOD, "Food")

class SoapFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Supply(x, y, Supply.default_width, Supply.default_height,
			pygame.transform.scale(textures.get(TextureType.SOAP),
			(Supply.default_width, Supply.default_height)), 
			SupplyType.SOAP, "Soap")

class HandSanitizerFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Supply(x, y, Supply.default_width, Supply.default_height,
			pygame.transform.scale(textures.get(TextureType.HAND_SANITIZER),
			(Supply.default_width, Supply.default_height)), 
			SupplyType.HAND_SANITIZER, "Hand Sanitizer")

class ToiletPaperFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Supply(x, y, Supply.default_width, Supply.default_height,
			pygame.transform.scale(textures.get(TextureType.TOILET_PAPER),
			(Supply.default_width, Supply.default_height)), 
			SupplyType.TOILET_PAPER, "Toilet Paper")

class MaskFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Supply(x, y, Supply.default_width, Supply.default_height,
			pygame.transform.scale(textures.get(TextureType.MASK),
			(Supply.default_width, Supply.default_height)), SupplyType.MASK, "Mask")

class PetSuppliesFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Supply(x, y, Supply.default_width, Supply.default_height,
			pygame.transform.scale(textures.get(TextureType.PET_SUPPLIES),
			(Supply.default_width, Supply.default_height)),
			SupplyType.PET_SUPPLIES, "Pet Supplies")