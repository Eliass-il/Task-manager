from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status

from src.api.dependencies import CurrentUser, SessionDep
from src.services import tasks as task_service
from src.shemas.task_shemas import TaskCreate, TaskRead

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    data: TaskCreate,
    user: CurrentUser,
    db: SessionDep
):
    return await task_service.create_task(db, data, user_id= user.id)

@router.get("", response_model=list[TaskRead])
async def list_tasks(
    user: CurrentUser,
    db: SessionDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    return await task_service.list_tasks(
        db,
        user_id=user.id,
        limit=limit,
        offset=offset,
    )


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: Annotated[int, Path(ge=1)],
    user: CurrentUser,
    db: SessionDep,
):
    task = await task_service.get_task(
        db,
        task_id=task_id,
        user_id=user.id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task