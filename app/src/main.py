from fastapi import FastAPI, Depends, HTTPException
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
# from auth.users import auth_backend, current_active_user, fastapi_users
# from auth.schemas import UserCreate, UserRead #, UserUpdate
# from auth.db import User, create_db_and_tables
# from booking.router import router as booking_router
# from tasks.router import router as tasks_router
# from redis import asyncio as aioredis
from src.linker.router import router as linker_router
from src.linker.db import create_db_and_tables
from src.auth.users import auth_backend, current_active_user, fastapi_users
from src.auth.schemas import UserCreate, UserRead, UserUpdate
from src.auth.users import User
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from src.tasks.router import router as tasks_router
from src.config import REDIS_URL

import uvicorn

def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        redis = aioredis.from_url(REDIS_URL, decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
        await create_db_and_tables()
        yield


    app = FastAPI(lifespan=lifespan)

    app.include_router(linker_router)
    app.include_router(tasks_router)

    app.include_router(
        fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
    )
    app.include_router(
        fastapi_users.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_verify_router(UserRead),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users.get_users_router(UserRead, UserUpdate),
        prefix="/users",
        tags=["users"],
    )

    @app.get("/authenticated-route")
    async def authenticated_route(user: User = Depends(current_active_user)):
        return {"message": f"Hello {user.email}!"}

    return app

app = create_app()
# if __name__ == "__main__":
#     uvicorn.run("main:app", reload=True, host="0.0.0.0", log_level="debug") 