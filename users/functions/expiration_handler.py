from redis_handler.redis import *

ALL_USERS_SESSIONS_LIST_REDIS_KEY = "SESSIONS_LIST"


def add_user_to_redis_sessions(value):
    if value not in redis_get_as_array(ALL_USERS_SESSIONS_LIST_REDIS_KEY):
        redis_set_as_array(ALL_USERS_SESSIONS_LIST_REDIS_KEY, value)


def remove_user_from_redis_sessions(value):
    if value in redis_get_as_array(ALL_USERS_SESSIONS_LIST_REDIS_KEY):
        redis_del_from_array(ALL_USERS_SESSIONS_LIST_REDIS_KEY, value)


def get_user_session_key(user_id):
    return "USER_EXP:" + user_id
