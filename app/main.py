from fastapi import FastAPI, Depends, Query
from .database import Base, engine, get_db
from .models import Pokemon, Type
from sqlalchemy.orm import Session
from sqlalchemy import desc
from .pokeapi import fetch_pokemon
import time

app = FastAPI() 

#creates tables when app starts
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return{"status": "ok"} 


@app.get("/analytics/top")
def top_by_stat(
    stat: str = Query("attack", description="One of: hp, attack, defense, special_attack, special_defense, speed"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    stat_map = {
        "hp": Pokemon.hp,
        "attack": Pokemon.attack,
        "defense": Pokemon.defense,
        "special_attack": Pokemon.special_attack,
        "special_defense": Pokemon.special_defense,
        "speed": Pokemon.speed,
    }

    if stat not in stat_map:
        return {"error": f"Invalid stat '{stat}'. Choose from: {list(stat_map.keys())}"}

    results = (
        db.query(Pokemon)
        .order_by(desc(stat_map[stat]))
        .limit(limit)
        .all()
    )

    return [
        {
            "id": p.id,
            "name": p.name,
            stat: getattr(p, stat),
            "types": [t.name for t in p.types],
        }
        for p in results
    ]

@app.post("/pokemon")
def create_pokemon(name: str, db: Session = Depends(get_db)): #give me a database connection for this request
    data = fetch_pokemon(name)
    pokemon = Pokemon(name=name) #creates python object
    type_names = [t["type"]["name"] for t in data["types"]]

    for type_name in type_names:
        existing_type = db.query(Type).filter(Type.name == type_name).first()
        if not existing_type:
            existing_type = Type(name=type_name)
            db.add(existing_type)
            db.commit()
            db.refresh(existing_type)

        pokemon.types.append(existing_type)

        db.add(pokemon)
        db.commit()
        db.refresh(pokemon)

    return {
        "message": "synced",
        "id": pokemon.id,
        "name": pokemon.name,
        "types": [t.name for t in pokemon.types],
        "attack": pokemon.attack
    }

@app.get("/pokemon")
def get_pokemon(db: Session = Depends(get_db)):
    pokemon = db.query(Pokemon).all()
    return pokemon

@app.post("/sync/pokemon/batch")
def sync_pokemon_batch(
    start: int = 1,
    end: int = 151,
    db: Session = Depends(get_db),
):
    inserted = 0
    skipped = 0
    failed = 0
    errors = []

    for pokemon_id in range(start, end + 1):
        try:
            data = fetch_pokemon(pokemon_id)
            result = upsert_pokemon_from_api_data(data, db)
            # time.sleep(0.1) # respect the api don't want to overwhelm it

            if result == "inserted":
                inserted += 1
            else:
                skipped += 1

        except Exception as e:
            failed += 1
            errors.append({"id": pokemon_id, "error": str(e)})

    return {
        "range": {"start": start, "end": end},
        "inserted": inserted,
        "skipped": skipped,
        "failed": failed,
        "errors_sample": errors[:5],  # don't spam the response
    }

@app.post("/sync/pokemon/{pokemon_id}")
def sync_pokemon(pokemon_id: int, db: Session = Depends(get_db)):
    data = fetch_pokemon(pokemon_id)

    #Stats come as a list of entries. turn it into a simple dict.
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


#insert if missing, otherwise skip
def upsert_pokemon_from_api_data(data: dict, db: Session) -> str:
    pokemon_id = data["id"]

    existing = db.query(Pokemon).filter(Pokemon.id == pokemon_id).first()
    if existing:
        return "skipped"

    stats_map = {s["stat"]["name"]: s["base_stat"] for s in data["stats"]}
    type_names = [t["type"]["name"] for t in data["types"]]

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

    #create/find types and link them
    for type_name in type_names:
        existing_type = db.query(Type).filter(Type.name == type_name).first()
        if not existing_type:
            existing_type = Type(name=type_name)
            db.add(existing_type)
            db.commit()
            db.refresh(existing_type)

        pokemon.types.append(existing_type)

    db.add(pokemon)
    db.commit()
    return "inserted"


