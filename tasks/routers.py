import json
from fastapi import APIRouter
from typing import List, Union
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from tasks.tables import Task, TaskHistory, TaskLabel
from tasks.types.task import TaskModelOut, TaskModelIn, TaskLabelOut, TaskRestoreIn
from fastapi import status

router = APIRouter()


@router.get("/tasks", response_model=List[TaskModelOut])
async def list_tasks(request: Request) -> List[TaskModelOut]:
    return (
        await Task.select()
        .where(Task.assignee_id == request.user.user_id)
        .order_by(Task.id)
    )


@router.post("/tasks/", response_model=TaskModelOut)
async def create_task(task_model: TaskModelIn) -> TaskModelOut:
    task = Task(**task_model.model_dump())
    await task.save()
    return task.to_dict()


@router.put("/tasks/{task_id}/", response_model=TaskModelIn)
async def update_task(
    task_id: int, task_model: TaskModelIn
) -> Union[TaskModelOut, JSONResponse]:
    task = await Task.objects().get(Task.id == task_id)
    if not task:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)

    for key, value in task_model.model_dump().items():
        setattr(task, key, value)

    await task.save()

    return task.to_dict()


@router.delete("/tasks/{task_id}/")
async def delete_task(request: Request, task_id: int) -> JSONResponse:
    task = await Task.objects().get(Task.id == task_id)
    if not task:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)
    history_representation = json.dumps(
        TaskModelOut(**task.to_dict()).model_dump(), default=str
    )
    await TaskHistory.objects().create(
        task_id=task.id,
        serialized_data=history_representation,
        deleted_by=request.user.user_id,
    )
    await task.remove()

    return JSONResponse({})


@router.get("/tasks/{task_id}/subtasks/", response_model=List[TaskModelOut])
async def list_subtasks(request: Request, task_id: int) -> List[TaskModelOut]:
    return (
        await Task.select()
        .where(
            (Task.assignee_id == request.user.user_id) & (Task.parent_task == task_id)
        )
        .order_by(Task.id)
    )


@router.get("/tasks/{task_id}/labels/", response_model=List[TaskLabelOut])
async def list_labels(request: Request, task_id: int) -> List[TaskLabelOut]:
    return (
        await TaskLabel.objects(TaskLabel.label)
        .where(TaskLabel.task.id == task_id)
        .order_by(TaskLabel.id)
    )


@router.get("/tasks/deleted/", response_model=List[TaskModelOut])
async def list_deleted() -> List[TaskModelOut]:
    historical_tasks = await TaskHistory.objects().order_by(TaskHistory.id)
    return [
        TaskModelOut(**json.loads(deleted.serialized_data))
        for deleted in historical_tasks
    ]


@router.post("/tasks/deleted/restore", response_model=List[TaskModelOut])
async def restore_deleted_tasks(restore_spec: TaskRestoreIn) -> List[TaskModelOut]:
    def historical_model_to_task(history: TaskHistory) -> Task:
        return Task(**TaskModelOut(**json.loads(history.serialized_data)).model_dump())

    tasks_to_restore = await TaskHistory.objects().where(
        TaskHistory.task_id.is_in(restore_spec.restore_ids)
    )

    restored_tasks = [historical_model_to_task(x) for x in tasks_to_restore]
    await TaskHistory.delete().where(
        TaskHistory.task_id.is_in(restore_spec.restore_ids)
    )

    return await Task.insert(*restored_tasks)
