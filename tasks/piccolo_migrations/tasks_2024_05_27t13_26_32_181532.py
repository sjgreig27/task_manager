from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.columns.column_types import Varchar


ID = "2024-05-27T13:26:32:181532"
VERSION = "1.5.1"
DESCRIPTION = ""


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="tasks", description=DESCRIPTION
    )

    manager.alter_column(
        table_class_name="Label",
        tablename="label",
        column_name="term",
        db_column_name="term",
        params={"unique": True},
        old_params={"unique": False},
        column_class=Varchar,
        old_column_class=Varchar,
        schema=None,
    )

    return manager
