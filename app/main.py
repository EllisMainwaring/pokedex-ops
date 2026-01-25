from fastapi import FastAPI
from .database import Base, engine
from .models import Pokemon

app = FastAPI() 

#creates tables when app starts
Base.metadata.create_all(bind=engine)

@app.get("/health")
def health():
    return{"status": "ok"} 