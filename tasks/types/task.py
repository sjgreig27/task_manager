from piccolo_api.crud.serializers import create_pydantic_model
from tasks.tables import Task

TaskModelIn = create_pydantic_model(table=Task, model_name="TaskModelIn")
TaskModelOut = create_pydantic_model(
    table=Task, include_default_columns=True, model_name="TaskModelOut"
)
