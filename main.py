from fastapi import FastAPI , Request , Response
from router import routes as api_router
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
# from db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

from seeder.seeder import seeder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    # allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Base.metadata.create_all(bind=engine)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["example.com", "*.myapi.com", "localhost"],
)
ALLOWED_IPS = {"192.168.1.1", "203.0.113.42"}

class IPFilterMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        forwarded = request.headers.get("X-Forwarded-For")
        client_ip = forwarded.split(",")[0] if forwarded else request.client.host

        print(f"🔍 Client IP: {client_ip}")  # نمایش IP کلاینت برای دیباگ

        if client_ip not in ALLOWED_IPS:
            return Response("🚫 Access denied", status_code=403)

        return await call_next(request)

app.add_middleware(IPFilterMiddleware)
app.include_router(api_router)

seeder()
