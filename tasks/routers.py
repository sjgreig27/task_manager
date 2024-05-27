import json
from fastapi import APIRouter
from typing import List, Union
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from tasks.tables import Task, TaskHistory, TaskLabel, Label
from tasks.types.task import (
    TaskModelOut,
    TaskModelIn,
    TaskLabelOut,
    TaskRestoreIn,
    LabelModelOut,
    LabelModelIn,
    TaskLabelIn,
)
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
    DB = Task._meta.db
    task = Task(**task_model.model_dump())
    async with DB.transaction():
        await task.save()
    return task.to_dict()


@router.put("/tasks/{task_id}/", response_model=TaskModelIn)
async def update_task(
    task_id: int, task_model: TaskModelIn
) -> Union[TaskModelOut, JSONResponse]:
    DB = Task._meta.db

    task = await Task.objects().get(Task.id == task_id)
    if not task:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)

    for key, value in task_model.model_dump().items():
        setattr(task, key, value)

    async with DB.transaction():
        await task.save()

    return task.to_dict()


@router.delete("/tasks/{task_id}/")
async def delete_task(request: Request, task_id: int) -> JSONResponse:
    DB = Task._meta.db

    task = await Task.objects().get(Task.id == task_id)
    if not task:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)
    history_representation = json.dumps(
        TaskModelOut(**task.to_dict()).model_dump(), default=str
    )

    async with DB.transaction():
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


@router.get("/tasks/deleted/", response_model=List[TaskModelOut])
async def list_deleted() -> List[TaskModelOut]:
    historical_tasks = await TaskHistory.objects().order_by(TaskHistory.id)
    return [
        TaskModelOut(**json.loads(deleted.serialized_data))
        for deleted in historical_tasks
    ]


@router.post("/tasks/deleted/restore", response_model=List[TaskModelOut])
async def restore_deleted_tasks(restore_spec: TaskRestoreIn) -> List[TaskModelOut]:
    DB = Task._meta.db

    def historical_model_to_task(history: TaskHistory) -> Task:
        return Task(**TaskModelOut(**json.loads(history.serialized_data)).model_dump())

    tasks_to_restore = await TaskHistory.objects().where(
        TaskHistory.task_id.is_in(restore_spec.restore_ids)
    )

    restored_tasks = [historical_model_to_task(x) for x in tasks_to_restore]

    async with DB.transaction():
        await TaskHistory.delete().where(
            TaskHistory.task_id.is_in(restore_spec.restore_ids)
        )

        await Task.insert(*restored_tasks)
    return (
        await Task.objects()
        .where(Task.id.is_in(restore_spec.restore_ids))
        .order_by(Task.id)
    )


@router.get("/tasks/{task_id}/labels/", response_model=List[TaskLabelOut])
async def list_task_labels(task_id: int) -> List[TaskLabelOut]:
    return (
        await TaskLabel.objects(TaskLabel.label)
        .where(TaskLabel.task == task_id)
        .order_by(TaskLabel.id)
    )


@router.post("/tasks/{task_id}/labels/", response_model=List[TaskLabelOut])
async def set_task_labels(
    task_id: int, labels: List[TaskLabelIn]
) -> List[TaskLabelOut]:
    DB = TaskLabel._meta.db

    new_task_labels = {x.label for x in labels}
    existing_task_labels = (
        await TaskLabel.select(TaskLabel.label)
        .where(TaskLabel.task == task_id)
        .distinct()
    )
    existing_task_label_ids = {x["label"] for x in existing_task_labels}
    async with DB.transaction():
        await TaskLabel.delete().where(
            (TaskLabel.label.not_in(new_task_labels) & (TaskLabel.task == task_id))
        )
        await TaskLabel.insert(
            *[
                TaskLabel(task=task_id, label=x.label)
                for x in labels
                if x.label not in existing_task_label_ids
            ]
        )
    return (
        await TaskLabel.objects(TaskLabel.label)
        .where(TaskLabel.task == task_id)
        .order_by(TaskLabel.id)
    )


@router.get("/labels", response_model=List[LabelModelOut])
async def list_labels(request: Request) -> List[LabelModelOut]:
    return await Label.select().order_by(Label.id)


@router.post("/labels/", response_model=LabelModelOut)
async def create_label(task_model: LabelModelIn) -> LabelModelOut:
    DB = Label._meta.db
    label = Label(**task_model.model_dump())
    async with DB.transaction():
        await label.save()
    return label.to_dict()


@router.put("/labels/{label_id}/", response_model=LabelModelOut)
async def update_label(
    label_id: int, label_model: LabelModelIn
) -> Union[LabelModelOut, JSONResponse]:
    DB = Label._meta.db
    label = await Label.objects().get(Label.id == label_id)
    if not label:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)

    for key, value in label_model.model_dump().items():
        setattr(label, key, value)

    async with DB.transaction():
        await label.save()

    return label.to_dict()


@router.delete("/labels/{label_id}/")
async def delete_label(label_id: int) -> JSONResponse:
    DB = Label._meta.db
    label = await Label.objects().get(Label.id == label_id)
    if not label:
        return JSONResponse({}, status_code=status.HTTP_404_NOT_FOUND)

    async with DB.transaction():
        await label.remove()

    return JSONResponse({})
