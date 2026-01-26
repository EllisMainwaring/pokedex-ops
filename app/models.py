from sqlalchemy import Column, Integer, String, Table, ForeignKey
from .database import Base
from sqlalchemy.orm import relationship

pokemon_types = Table(
    "pokemon_types",
    Base.metadata,
    Column("pokemon_id", Integer, ForeignKey("pokemon.id"), primary_key=True),
    Column("type_id", Integer, ForeignKey("types.id"), primary_key=True),
)

class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    height = Column(Integer, nullable=True)
    weight = Column(Integer, nullable=True)

    hp = Column(Integer, nullable=True)
    attack = Column(Integer, nullable=True)
    defense = Column(Integer, nullable=True)
    special_attack = Column(Integer, nullable=True)
    special_defense = Column(Integer, nullable=True)
    speed = Column(Integer, nullable=True)

    types = relationship("Type", secondary=pokemon_types, back_populates="pokemon")



class Type(Base):
    __tablename__ = "types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    pokemon = relationship("Pokemon", secondary=pokemon_types, back_populates="types")
