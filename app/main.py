from fastapi import FastAPI, Depends
from .database import Base, engine, get_db
from .models import Pokemon
from sqlalchemy.orm import Session

app = FastAPI() 

#creates tables when app starts
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return{"status": "ok"} 

@app.post("/pokemon")
def create_pokemon(name: str, db: Session = Depends(get_db)): #give me a database connection for this request
    pokemon = Pokemon(name=name) #creates python object
    db.add(pokemon)
    db.commit()
    db.refresh(pokemon)
    return {
        "id": pokemon.id,
        "name": pokemon.name
    }

@app.get("/pokemon")
def get_pokemon(db: Session = Depends(get_db)):
    pokemon = db.query(Pokemon).all()
    return pokemon
