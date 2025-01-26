from fastapi import APIRouter


from users.routes.userRouter import router as users_router
routes = APIRouter()

# user routes
routes.include_router(users_router, prefix="/users", tags=["users"])

