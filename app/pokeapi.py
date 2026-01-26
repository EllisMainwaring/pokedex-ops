import requests

BASE_URL = "https://pokeapi.co/api/v2"

def fetch_pokemon(pokemon_id: int) -> dict:
    response = requests.get(f"{BASE_URL}/pokemon/{pokemon_id}", timeout=10)
    response.raise_for_status() #error if not found
    return response.json()