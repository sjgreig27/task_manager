from typing import List
from piccolo_api.crud.serializers import create_pydantic_model
from pydantic import BaseModel
from tasks.tables import Task, TaskLabel, Label

LabelModelIn = create_pydantic_model(table=Label, model_name="LabelModelIn")

LabelModelOut = create_pydantic_model(
    table=Label, model_name="LabelModelOut", include_default_columns=True
)

TaskModelIn = create_pydantic_model(table=Task, model_name="TaskModelIn")

TaskModelOut = create_pydantic_model(
    table=Task, include_default_columns=True, model_name="TaskModelOut"
)

TaskLabelIn = create_pydantic_model(
    TaskLabel,
    exclude_columns=(TaskLabel.task,),
    model_name="TaskLabelOut",
)

TaskLabelOut = create_pydantic_model(
    TaskLabel,
    include_default_columns=True,
    exclude_columns=(TaskLabel.task,),
    model_name="TaskLabelOut",
    nested=True,
)


class TaskRestoreIn(BaseModel):
    restore_ids: List[int]
