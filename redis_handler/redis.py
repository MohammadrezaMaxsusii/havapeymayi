from fastapi import FastAPI
import redis
import json

app = FastAPI()

# Initialize Redis connection
redis_client = redis.Redis(host="192.168.17.139", port=6379, decode_responses=True)

# print(json.loads(redis_client.get("GET_USER_INFO_KEY:09034214054")))
def redis_set_value(key: str, value: str, ttl: int = 120):
    redis_client.set(key, str(value), ttl)
    return {"status": True}

def redis_get_value(key: str):
    value = redis_client.get(key)
    if(value == None):
        return {"status": False}
    return {"status": True, "value": value}

def redis_del_value(key: str):
    redis_client.delete(key)


