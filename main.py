from fastapi import FastAPI
import redis
from pydantic import BaseModel
import asyncio

app = FastAPI()

redis_client = redis.Redis(host='localhost',port=6379,db=0,socket_timeout=2)

@app.get("/items/{item_id}")
def get_item(item_id:int):

    cached_item= redis_client.get(f"item_{item_id}")

    if cached_item:

        return {"item_id": item_id, "cached": True, "data": cached_item}

    item_data = f"Item data for {item_id}"
    redis_client.setex(f"item_{item_id}",3600, item_data)

    return {"item_id": item_id, "cached": False, "data": item_data}


class BookingRequest(BaseModel):
    session:str

@app.post("/movies/{movie_id}/{seat_id}")
async def book_movie(movie_id:str,seat_id:str,request_data:BookingRequest):

    session = request_data.session

    key = f"lock:{movie_id}:{seat_id}"

    lock_acquaried = redis_client.set(key,session,nx=True,ex=120)

    if not lock_acquaried:
        return {"status": "Error"}

    try:
        await asyncio.sleep(7)

        return {"status": "success", "message": f"Seat {seat_id} successfully booked!"}

    finally:
        redis_client.delete(key)