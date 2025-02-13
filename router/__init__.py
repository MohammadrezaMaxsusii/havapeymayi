from fastapi import APIRouter

from auth.routes.auth_routes import router as auth_router
from users.routes.userRouter import router as users_router

routes = APIRouter()

# user routes
routes.include_router(users_router, prefix="/users", tags=["users"])
routes.include_router(auth_router, prefix="/auth", tags=["auth"])
