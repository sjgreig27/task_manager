from piccolo_conf import *  # noqa


DB = PostgresEngine(
    config={
        "database": "task_manager_test",
        "user": "task_manager",
        "password": "task_manager",
        "host": "localhost",
        "port": 5432,
    }
)
