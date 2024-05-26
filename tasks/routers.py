from fastapi import APIRouter
from typing import List, Union
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from tasks.tables import Task
from tasks.types.task import TaskModelOut, TaskModelIn

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
    task = Task(**task_model.dict())
    await task.save()
    return task.to_dict()


@router.put("tasks/{task_id}/", response_model=TaskModelOut)
async def update_task(
    task_id: int, task_model: TaskModelIn
) -> Union[TaskModelOut, JSONResponse]:
    task = await Task.objects().get(Task.id == task_id)
    if not task:
        return JSONResponse({}, status_code=404)

    for key, value in task_model.dict().items():
        setattr(task, key, value)

    await task.save()

    return task.to_dict()


@router.delete("tasks/{task_id}/")
async def delete_task(task_id: int) -> JSONResponse:
    task = await Task.objects().get(Task.id == task_id)
    if not task:
        return JSONResponse({}, status_code=404)
    await task.remove()

    return JSONResponse({})
