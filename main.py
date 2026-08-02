from fastapi import FastAPI
import redis

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
