from fastapi import FastAPI
from router import routes as api_router

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
app.include_router(api_router)

seeder()
