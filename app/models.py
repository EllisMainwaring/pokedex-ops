from sqlalchemy import Column, Integer, String
from .database import Base 

class Pokemon(Base):
    __tablename__ = "pokemon"

    id = Column(Integer, primary_key=True, index=True)  #PokéAPI ID
    name = Column(String, unique=True, index=True, nullable=False)