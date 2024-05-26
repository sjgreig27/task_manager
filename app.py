from fastapi import FastAPI
from piccolo_admin.endpoints import create_admin
from piccolo.engine import engine_finder
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from tasks.endpoints import HomeEndpoint
from tasks.piccolo_app import APP_CONFIG
from tasks.routers import router as task_router
from piccolo_api.session_auth.endpoints import session_login, session_logout
from starlette.middleware.authentication import AuthenticationMiddleware
from piccolo_api.session_auth.middleware import SessionsAuthBackend


app = FastAPI(
    routes=[
        Route("/", HomeEndpoint),
        Mount(
            "/admin/",
            create_admin(
                tables=APP_CONFIG.table_classes,
                # Required when running under HTTPS:
                # allowed_hosts=['my_site.com']
            ),
        ),
        Mount("/static/", StaticFiles(directory="static")),
        Mount("/login/", session_login()),
        Mount("/logout/", session_logout()),
    ],
)


@app.on_event("startup")
async def open_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.start_connection_pool()
    except Exception:
        print("Unable to connect to the database")


@app.on_event("shutdown")
async def close_database_connection_pool():
    try:
        engine = engine_finder()
        await engine.close_connection_pool()
    except Exception:
        print("Unable to connect to the database")


app.include_router(task_router)
app = AuthenticationMiddleware(
    app,
    backend=SessionsAuthBackend(),
)
