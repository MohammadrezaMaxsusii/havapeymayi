from redis_handler.redis import *

KEY = "SESSIONS_LIST"


def add_user_to_redis_sessions(value):
    if value not in redis_get_as_array(KEY):
        redis_set_as_array(KEY, value)


def remove_user_from_redis_sessions(value):
    if value in redis_get_as_array(KEY):
        redis_del_from_array(KEY, value)
