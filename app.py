import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["ecse3038"]
devices = db["tutorial5"]

app = FastAPI()


class Device(BaseModel):
    name: str
    room: str
    temp: float
    online: bool


# Your handlers go below this line.
@app.get("/devices")
def get_devices():
    return list(devices.find({}, {"_id": 0}))

@app.get("/devices/{name}")
def get_device(name: str):
    device = devices.find_one({"name": name}, {"_id": 0})
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@app.post("/devices", status_code=201)
def create_device(device: Device):
    new_device = device.model_dump()
    devices.insert_one(new_device)
    new_device.pop("_id")  
    return new_device

@app.put("/devices/{name}")
def update_device(name: str, device: Device):
    existing_device = devices.find_one({"name": name})

    if existing_device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    updated_device = device.model_dump()

    updated_device["name"] = name

    devices.replace_one(
        {"name": name},
        updated_device
    )

    return updated_device

@app.delete("/devices/{name}")
def delete_device(name: str):
    result = devices.delete_one({"name": name})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Device not found")

    return {"message": "Device deleted"}