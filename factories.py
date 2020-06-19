import sdl2

from enums import TextureType, LocationType, ItemType, SupplyType, PetType, CharacterType, MapElementType
from locations import Location, House, GroceryStore, GasStation, Aisle, Road
from player import Player
from items import Item, Vehicle, Sink, ShoppingCart, Supply, Door, SelfCheckout, Closet, FuelDispenser
from npcs import Character, Pet, Shopper

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
		self.factories[CharacterType.SHOPPER] = ShopperFactory()

	# Returns newly created character from corresponding factory
	def create(self, type, x, y, name, textures):
		return self.factories.get(type).create(x, y, name, textures)

class PetFactory(ICharacterFactory):
	def create(self, x, y, name, textures):
		return Pet(x, y, name, textures.get(TextureType.DOG))

class ShopperFactory(ICharacterFactory):
	def create(self, x, y, name, textures):
		return Shopper(x, y, name, textures.get(TextureType.CIVILIAN), None)

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
		self.factories[LocationType.GAS_STATION] = GasStationFactory()

	# Returns newly created location from corresponding factory
	def create(self, type, x, y, size, textures):
		return self.factories.get(type).create(x, y, size, textures)
	
class HouseFactory(ILocationFactory):
	def create(self, x, y, size, textures):
		return House(x, y, House.default_width, House.default_height,
			textures.get(TextureType.HOUSE_INTERIOR), textures.get(TextureType.HOUSE_EXTERIOR))
		
class GroceryStoreFactory(ILocationFactory):
	def create(self, x, y, size, textures):
		width = int(GroceryStore.default_width * size)
		height = int(GroceryStore.default_height * size)

		return GroceryStore(x, y, width, height,
			textures.get(TextureType.STORE_INTERIOR), textures.get(TextureType.STORE_EXTERIOR))
		
class GasStationFactory(ILocationFactory):
	def create(self, x, y, size, textures):
		width = int(GasStation.default_width * size)
		height = int(GasStation.default_height * size)

		return GasStation(x, y, width, height,
			textures.get(TextureType.STORE_INTERIOR), textures.get(TextureType.STORE_EXTERIOR))

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
		self.factories[MapElementType.ROAD] = RoadFactory()

	# Returns newly created map element from corresponding factory
	def create(self, type, x, y, width, height, textures):
		return self.factories.get(type).create(x, y, width, height, textures)
	
class AisleFactory(IMapElementFactory):
	def create(self, x, y, width, height, textures):
		return Aisle(x, y, width, height, textures.get(TextureType.AISLE))
	
class RoadFactory(IMapElementFactory):
	def create(self, x, y, width, height, textures):
		return Road(x, y, width, height, textures.get(TextureType.ROAD))

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
		self.factories[ItemType.DOOR] = DoorFactory()
		self.factories[ItemType.SELF_CHECKOUT] = SelfCheckoutFactory()
		self.factories[ItemType.CLOSET] = ClosetFactory()
		self.factories[ItemType.FUEL_DISPENSER] = FuelDispenserFactory()

	# Returns newly created item from corresponding factory
	def create(self, type, x, y, textures):
		return self.factories.get(type).create(x, y, textures)
	
class VehicleFactory(IItemFactory):
	def create(self, x, y, textures):
		return Vehicle(x, y, textures.get(TextureType.VEHICLE))

class SinkFactory(IItemFactory):
	def create(self, x, y, textures):
		return Sink(x, y, textures.get(TextureType.SINK))
	
class ShoppingCartFactory(IItemFactory):
	def create(self, x, y, textures):
		return ShoppingCart(x, y, textures.get(TextureType.SHOPPING_CART))
	
class DoorFactory(IItemFactory):
	def create(self, x, y, textures):
		return Door(x, y, textures.get(TextureType.DOOR))
	
class SelfCheckoutFactory(IItemFactory):
	def create(self, x, y, textures):
		return SelfCheckout(x, y, textures.get(TextureType.SELF_CHECKOUT))
	
class ClosetFactory(IItemFactory):
	def create(self, x, y, textures):
		return Closet(x, y, textures.get(TextureType.CLOSET))
	
class FuelDispenserFactory(IItemFactory):
	def create(self, x, y, textures):
		return FuelDispenser(x, y, textures.get(TextureType.FUEL_DISPENSER))

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
			textures.get(TextureType.FOOD), 
			SupplyType.FOOD, "Food")

class SoapFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Supply(x, y, Supply.default_width, Supply.default_height,
			textures.get(TextureType.SOAP), 
			SupplyType.SOAP, "Soap")

class HandSanitizerFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Supply(x, y, Supply.default_width, Supply.default_height,
			textures.get(TextureType.HAND_SANITIZER), 
			SupplyType.HAND_SANITIZER, "Hand Sanitizer")

class ToiletPaperFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Supply(x, y, Supply.default_width, Supply.default_height,
			textures.get(TextureType.TOILET_PAPER), 
			SupplyType.TOILET_PAPER, "Toilet Paper")

class MaskFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Supply(x, y, Supply.default_width, Supply.default_height,
			textures.get(TextureType.MASK), SupplyType.MASK, "Mask")

class PetSuppliesFactory(ILocationFactory):
	def create(self, x, y, textures):
		return Supply(x, y, Supply.default_width, Supply.default_height,
			textures.get(TextureType.PET_SUPPLIES),
			SupplyType.PET_SUPPLIES, "Pet Supplies")