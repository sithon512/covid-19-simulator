from sqlalchemy import (
	create_engine as ce,
	Column,
	Integer,
	String,
	Float,
	ForeignKey,
	# relationship
)
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import sessionmaker

# DEFINE DATABASE ENGINE
engine = ce('sqlite:///dat')
Base = declarative_base()
Session = sessionmaker()

# DEFINE MODELS

class GameData(Base):
	"""
	Database key for a given save game. This is what all game attributes are
	related to when the game is saved so that different save games can be
	separated from each other.

	:attr uid: the unique identifier for this save game instance.
	:attr name: the user defined name of this save game instance.
	:attr world_age: the cumulative playtime of this world in ticks as
	returned from `pygame.time.get_ticks`.
	"""

	__tablename__ = 'gamedata'

	uid = Column(Integer, primary_key=True)
	name = Column(String(128))
	world_age = Column(Integer)


class Entity(object):
	"""
	Defines `Entity` mixin to be used for inheritance.

	:attr pos_x: the X coordinate of the entity.
	:attr pos_y: the Y coordinate of the entity.
	:attr width: the width (in pixels) of the entity.
	:attr height: the height (in pixels) of the entity.
	:attr texture_name: the name of the texture file used for this entity.
	:attr angle: the rotation of this entity as on the game map.
	"""

	@declared_attr
	def pos_x(cls):
		return Column(Float)
	@declared_attr
	def pos_y(cls):
		return Column(Float)
	@declared_attr
	def width(cls):
		return Column(Integer)
	@declared_attr
	def height(cls):
		return Column(Integer)
	@declared_attr
	def texture_name(cls):
		return Column(String(64))
	@declared_attr
	def angle(cls):
		return Column(Float)


class Player(Base, Entity):
	"""
	Defines the model for player statistics.

	:attr uid: the unique identifier of this player instance.
	:attr name: the user defined anme of this player.
	:attr money: the money resource of the player.
	:attr health: the health resource of this player.
	:attr morale: the morale resource of this player.
	"""

	__tablename__ = 'player'

	uid = Column(Integer, primary_key=True)
	name = Column(String(64))
	money = Column(Float)
	health = Column(Integer)
	morale = Column(Integer)


class Character(Base, Entity):
	"""
	Defines the model for NPC.

	:attr uid: the unique identifier of this character instance.
	:attr type: the integer identifier referencing the enumerated type as
	found in `enums.py`.
	:attr name: the name of this character, may or may not be user defined.
	:attr interaction_message: the message displayed for this character when
	the player in close proximity.
	:attr last_interaction: the last time the player interacted with this
	character in ticks. NOTE: this should be absolute with respect to the save
	game age.
	"""

	__tablename__ = 'character'

	uid = Column(Integer, primary_key=True)
	type = Column(Integer)
	name = Column(String(64))
	interaction_message = Column(String(256))
	last_interaction = Column(Integer)


class Location(Base, Entity):
	"""
	Defines the model for Location.

	:attr uid: the unique identifier of this location instance.
	:attr type: the integer identifier referencing the enumerated type as
	found in `enums.py`.
	:attr name: the name of the location.
	"""

	__tablename__ = 'location'

	uid = Column(Integer, primary_key=True)
	type = Column(Integer)
	name = Column(String(64))


class Item(Base, Entity):
	"""
	Defines the model for item.

	:attr uid: the unique identifier of this item instance.
	:attr type: the integer identifier referencing the enumerated type as
	found in `enums.py`.
	:attr name: the name of the item.
	:attr interaction_message: the message displayed for this item when the
	player is in close proximity.
	:attr last_interaction: the last time the player interacted with this item
	in ticks. NOTE: this should be absolute with respect to the save game age.
	"""

	__tablename__ = 'item'
	uid = Column(Integer, primary_key=True)
	type = Column(Integer)
	name = Column(String(64))
	interaction_message = Column(String(256))
	last_interaction = Column(Integer)


# DEFINE DATABASE
Base.metadata.create_all(engine)
Session.configure(bind=engine)

# global reference to database
database_session = Session()
