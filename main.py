from fastapi import FastAPI , Request , Response
from router import routes as api_router
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from shared.functions.shareConfFile import getConfigFile
from fastapi.middleware.cors import CORSMiddleware
from middleware.responseFormatter import  IPFilterMiddleware
from seeder.seeder import seeder
ipfilter = IPFilterMiddleware
app = FastAPI()
origins = [
    "https://www.example.com",
    "https://example.com",
		"https://api.example.com"
]

app.add_middleware(
    CORSMiddleware,
    # allow_origins=getConfigFile("acl" , "ALLOWEDHOSTS").split(","),
    allow_origins = origins,
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
