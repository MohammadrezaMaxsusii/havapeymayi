from fastapi import FastAPI, Request, Response
from redis_handler.redis import *
from router import routes as api_router
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from shared.functions.shareConfFile import getConfigFile
from fastapi.middleware.cors import CORSMiddleware
from middleware.responseFormatter import IPFilterMiddleware
from seeder.seeder import seeder
from apscheduler.schedulers.background import BackgroundScheduler
from users.dto.createUser import deleteUserDto
from users.functions.expiration_handler import (
    ALL_USERS_SESSIONS_LIST_REDIS_KEY,
    remove_user_from_redis_sessions,
)
from users.routes.userRouter import EACH_USER_SESSION_EXP_KEY, deleteUser

ipfilter = IPFilterMiddleware
app = FastAPI()
origins = ["https://www.example.com", "https://example.com", "https://api.example.com"]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=getConfigFile("acl" , "ALLOWEDHOSTS").split(","),
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
    max_age=3600,
)

# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts = getConfigFile("acl" , "ALLOWEDHOSTS").split(","),
# )


app.add_middleware(ipfilter)
app.include_router(api_router)

seeder()


def remove_expired_sessions():
    print("Removing expired sessions...")

    user_sessions = redis_get_keys_regex(EACH_USER_SESSION_EXP_KEY)
    all_sessions = redis_get_as_array(ALL_USERS_SESSIONS_LIST_REDIS_KEY)

    for this_session in all_sessions:
        if this_session not in user_sessions:
            print(f"Removing session: {this_session}")

            user_id = this_session.split(":")[1]
            deleteUser(deleteUserDto(id=user_id))
            remove_user_from_redis_sessions(this_session)


duration = int(getConfigFile("interval_remove_session", "MINUTE"))
scheduler = BackgroundScheduler()
scheduler.add_job(remove_expired_sessions, "interval", minutes=duration)
scheduler.start()
