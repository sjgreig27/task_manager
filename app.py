import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI
from piccolo_admin.endpoints import create_admin
from piccolo.engine import engine_finder
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles
from tasks.endpoints import HomeEndpoint
from tasks.piccolo_app import APP_CONFIG
from tasks.routers import router as task_router
from piccolo_api.session_auth.endpoints import session_login, session_logout
from piccolo_api.session_auth.middleware import SessionsAuthBackend
from starlette.middleware import Middleware
from starlette.middleware.authentication import AuthenticationMiddleware


async def open_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.start_connection_pool()
    except Exception:
        print("Unable to connect to the database")


async def close_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.close_connection_pool()
    except Exception:
        print("Unable to connect to the database")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await open_database_connection_pool()
    yield
    await close_database_connection_pool()


app = FastAPI(
    routes=[
        Route("/", HomeEndpoint),
        Mount(
            "/admin/",
            create_admin(
                tables=APP_CONFIG.table_classes,
            ),
        ),
        Mount("/static/", StaticFiles(directory="static")),
        Mount("/login/", session_login(redirect_to="/task_manager/docs")),
        Mount("/logout/", session_logout(redirect_to="/login/")),
    ],
    lifespan=lifespan,
)

authenticated_app = FastAPI(
    middleware=[
        Middleware(
            AuthenticationMiddleware,
            backend=SessionsAuthBackend(
                increase_expiry=datetime.timedelta(minutes=30),
                admin_only=False,
                superuser_only=False,
            ),
        ),
    ],
)
authenticated_app.include_router(task_router)
app.mount("/task_manager/", authenticated_app)
