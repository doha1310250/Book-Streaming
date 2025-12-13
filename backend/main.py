from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI()


# Routes
@app.get("/")
def home():
    return {"message": "FastAPI is working!"}

