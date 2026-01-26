from fastapi import FastAPI, Depends
from .database import Base, engine, get_db
from .models import Pokemon
from sqlalchemy.orm import Session
from .pokeapi import fetch_pokemon

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

@app.post("/sync/pokemon/{pokemon_id}")
def sync_pokemon(pokemon_id: int, db: Session = Depends(get_db)):
    data = fetch_pokemon(pokemon_id)

    #Stats come as a list of entries. We'll turn it into a simple dict.
    stats_map = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}

    #Types come as a list too
    type_names = [t["type"]["name"] for t in data["types"]]

    existing = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if existing:
        return {"message": "already exists", "id": existing.id, "name": existing.name}

    pokemon = Pokemon(
        id=pokemon_id,
        name=data["name"],
        height=data.get("height"),
        weight=data.get("weight"),
        hp=stats_map.get("hp"),
        attack=stats_map.get("attack"),
        defense=stats_map.get("defense"),
        special_attack=stats_map.get("special-attack"),
        special_defense=stats_map.get("special-defense"),
        speed=stats_map.get("speed"),
    )

    db.add(pokemon)
    db.commit()
    db.refresh(pokemon)

    return {
        "message": "synced",
        "id": pokemon.id,
        "name": pokemon.name,
        "types": type_names,
        "attack": pokemon.attack
    }
