
class TextureType:
	PLAYER = 0
	HOUSE_INTERIOR = 1
	GROCERY_STORE_INTERIOR = 2
	VEHICLE = 3
	SINK = 4
	SHOPPING_CART = 5
	DOG = 6
	FOOD = 7
	SOAP = 8
	HAND_SANITIZER = 9
	TOILET_PAPER = 10
	MASK = 11
	PET_SUPPLIES = 12
	AISLE = 13
	DOOR = 14
	HOUSE_EXTERIOR = 15
	STORE_EXTERIOR = 16
	SELF_CHECKOUT = 17
	CLOSET = 18
	CIVILIAN = 19
	FUEL_DISPENSER = 20
	ROAD = 21
	SIDEWALK = 22
	DRIVEWAY = 23
	PARKING_LOT = 24
	KITCHEN = 25
	COUNTER = 26
	BED = 27
	DESK = 28
	COMPUTER = 29
	STOCKER = 30
	GAS_STATION_INTERIOR = 31
	GAS_STATION_EXTERIOR = 32
	GROCERY_STORE_EXTERIOR = 33
	SPLASH_SCREEN = 34
	HOUSE_EXTERIOR_REAR = 35
	GRASS = 36
	MINI_MAP = 37
	MAIN_MENU = 38
	LOSE_SCREEN = 39

class LocationType:
	HOUSE = 0
	GROCERY_STORE = 1
	GAS_STATION = 2

	HOUSE_REAR = 3

class ItemType:
	VEHICLE = 0
	SINK = 1
	SHOPPING_CART = 2
	SUPPLY = 3
	DOOR = 4
	SELF_CHECKOUT = 5
	CLOSET = 6
	FUEL_DISPENSER = 7
	KITCHEN = 8
	BED = 9
	COMPUTER = 10

class SupplyType:
	FOOD = 0
	SOAP = 1
	HAND_SANITIZER = 2
	TOILET_PAPER = 3
	PET_SUPPLIES = 4
	MASK = 5

	supply_strs = [
		"food",
		"soap",
		"hand sanitizer",
		"toilet paper",
		"mask",
		"pet supplies" ]

class CharacterType:
	PET = 0
	SHOPPER = 1
	STOCKER = 2

class PetType:
	DOG = 0
	CAT = 1

class AisleType:
	GROCERIES = 0
	TOILETRIES = 1
	PET_SUPPLIES = 2

class InventoryType:
	BACKPACK = 0
	SHOPPING_CART = 1
	CLOSET = 2

class MapElementType:
	AISLE = 0
	ROAD = 1
	SIDEWALK = 2
	DRIVEWAY = 3
	PARKING_LOT = 4
	COUNTER = 5
	DESK = 6

class RoadType:
	SMALL = 0
	MEDIUM = 1
	LARGE = 2
