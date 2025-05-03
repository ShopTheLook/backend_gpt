from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

@app.post("/second")
async def second_system(data: dict):
    # Simulate some transformation
    data["verified"] = True
    return data
