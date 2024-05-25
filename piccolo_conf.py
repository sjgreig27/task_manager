import os
from piccolo.engine.postgres import PostgresEngine
from piccolo.conf.apps import AppRegistry


DB = PostgresEngine(
    config={
        "database": os.environ.get("POSTGRES_DB_NAME", "task_manager"),
        "user": os.environ.get("POSTGRES_DB_USER", "task_manager"),
        "password": os.environ.get("POSTGRES_DB_USER_PASSWORD", "task_manager"),
        "host": os.environ.get("POSTGRESQL_DB_HOST", "localhost"),
        "port": int(os.environ.get("POSTGRESQL_DB_PORT", "5432")),
    }
)

APP_REGISTRY = AppRegistry(apps=["tasks.piccolo_app", "piccolo_admin.piccolo_app"])
