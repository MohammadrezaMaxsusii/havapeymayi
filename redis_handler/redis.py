import configparser
import redis

config = configparser.ConfigParser()

config.read("config.ini")
host = config.get("redis", "REDIS_HOST")
port = config.get("redis", "REDIS_PORT")
# Initialize Redis connection
redis_client = redis.Redis(host=host, port=int(port), decode_responses=True)


# print(json.loads(redis_client.get("GET_USER_INFO_KEY:09034214054")))
def redis_set_value(key: str, value: str, ttl: int = 120):
    redis_client.set(key, str(value), ttl)
    return {"status": True}


def redis_get_value(key: str):
    value = redis_client.get(key)
    if value == None:
        return {"status": False}
    return {"status": True, "value": value}


def redis_del_value(key: str):
    redis_client.delete(key)
