from enum import Enum
from piccolo.table import Table
from piccolo.columns import (
    Varchar,
    ForeignKey,
    Date,
    M2M,
    LazyTableReference,
    Integer,
    JSON,
    Timestamp,
)
from piccolo.apps.user.tables import BaseUser
from piccolo.columns import OnDelete


class Task(Table):
    """
    An example table.
    """

    class Status(str, Enum):
        pending = "Pending"
        doing = "Doing"
        blocked = "Blocked"
        done = "Done"

    name = Varchar()
    description = Varchar(null=True)
    assignee_id = ForeignKey(
        references=BaseUser, on_delete=OnDelete.restrict, null=False
    )
    status = Varchar(length=50, choices=Status, null=False, default=Status.pending)
    parent_task = ForeignKey(references="self", on_delete=OnDelete.cascade, null=True)
    date_due = Date(null=True)
    labels = M2M(LazyTableReference("TaskLabel", module_path=__name__))


class TaskHistory(Table):
    task_id = Integer(unique=True)
    serialized_data = JSON()
    deleted_on = Timestamp()
    deleted_by = ForeignKey(BaseUser, on_delete=OnDelete.restrict)


class Label(Table):
    term = Varchar(unique=True)
    description = Varchar(null=True)
    tasks = M2M(LazyTableReference("TaskLabel", module_path=__name__))


class TaskLabel(Table):
    task = ForeignKey(Task)
    label = ForeignKey(Label)
