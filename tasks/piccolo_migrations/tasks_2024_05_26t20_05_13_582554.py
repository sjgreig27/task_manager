from enum import Enum
from piccolo.columns import OnDelete, Secret, Boolean, Timestamp, Integer, Serial
from piccolo.apps.migrations.auto.migration_manager import MigrationManager
from piccolo.table import Table
from piccolo.columns import Varchar, ForeignKey, Date, M2M, LazyTableReference


ID = "2024-05-26T20:05:13:582554"
VERSION = "1.5.1"
DESCRIPTION = "Prepopulate schema with example data"


class BaseUser(Table, tablename="piccolo_user"):
    id = Serial(index=False, primary_key=True, db_column_name="id")
    username = Varchar(length=100, unique=True)
    password = Secret(length=255)
    first_name = Varchar(null=True)
    last_name = Varchar(null=True)
    email = Varchar(length=255, unique=True)
    active = Boolean(default=False)
    admin = Boolean(
        default=False, help_text="An admin can log into the Piccolo admin GUI."
    )
    superuser = Boolean(
        default=False,
        help_text=(
            "If True, this user can manage other users's passwords in the "
            "Piccolo admin GUI."
        ),
    )
    last_login = Timestamp(
        null=True,
        default=None,
        required=False,
        help_text="When this user last logged in.",
    )


class Task(Table):
    class Status(str, Enum):
        pending = "Pending"
        doing = "Doing"
        blocked = "Blocked"
        done = "Done"

    id = Serial(index=False, primary_key=True, db_column_name="id")
    name = Varchar()
    description = Varchar(null=True)
    assignee_id = ForeignKey(
        references=BaseUser, on_delete=OnDelete.restrict, null=False
    )
    status = Varchar(length=50, choices=Status, null=False, default=Status.pending)
    parent_task = ForeignKey(references="self", on_delete=OnDelete.cascade, null=True)


class Label(Table):
    id = Serial(index=False, primary_key=True, db_column_name="id")
    term = Varchar()
    description = Varchar(null=True)


class TaskLabel(Table):
    task = ForeignKey(Task)
    label = ForeignKey(Label)


async def forwards():
    manager = MigrationManager(
        migration_id=ID, app_name="tasks", description=DESCRIPTION
    )

    async def run():
        smclean = await BaseUser.objects().create(
            username="smclean",
            password="pbkdf2_sha256$600000$96d80f64a2caf96913561676cbf5bda7$3375dd4e67ce9c29de10a0b2ae03bb85a3c907474e1f394d00eab23b0689af6b",
            first_name="Steve",
            last_name="Mclean",
            email="stevenmclean@gmail.com",
            active=True,
            admin=False,
            superuser=False,
        )

        lmclean = await BaseUser.objects().create(
            username="lmclean",
            password="pbkdf2_sha256$600000$96d80f64a2caf96913561676cbf5bda7$3375dd4e67ce9c29de10a0b2ae03bb85a3c907474e1f394d00eab23b0689af6b",
            first_name="Lisa",
            last_name="Mclean",
            email="lisamclean@gmail.com",
            active=True,
            admin=False,
            superuser=False,
        )

        jmclean = await BaseUser.objects().create(
            username="jmclean",
            password="pbkdf2_sha256$600000$96d80f64a2caf96913561676cbf5bda7$3375dd4e67ce9c29de10a0b2ae03bb85a3c907474e1f394d00eab23b0689af6b",
            first_name="John",
            last_name="Mclean",
            email="johnmclean@gmail.com",
            active=True,
            admin=False,
            superuser=False,
        )

        parent_task = await Task.objects().create(
            name="Prepare instrument",
            description="Prepare instrument for not batch of reactions",
            assignee_id=jmclean.id,
            status="Doing",
        )

        await Task.insert(
            Task(
                name="Weigh",
                description="Weigh out reactants for chemical reaction",
                assignee_id=smclean.id,
                status="Pending",
            ),
            Task(
                name="Replenish instrument",
                description="Restock consumables for instrument",
                assignee_id=lmclean.id,
                status="Done",
            ),
            Task(
                name="Discard waste",
                description="Empty waste for instrument",
                assignee_id=jmclean.id,
                parent_task=parent_task.id,
                status="Doing",
            ),
            Task(
                name="Clean instrument",
                description="Instrument requires cleaning",
                assignee_id=jmclean.id,
                parent_task=parent_task.id,
                status="Pending",
            ),
        )

        high_priority = await Label.objects().create(
            term="High priority", description="Task to be prioritised"
        )
        parked = await Label.objects().create(
            term="Parked", description="Task is being paused"
        )

        await TaskLabel.insert(
            TaskLabel(task=parent_task.id, label=high_priority.id),
            TaskLabel(task=parent_task.id, label=parked.id),
        )

    manager.add_raw(run)

    return manager
