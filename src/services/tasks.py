from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Task
from src.shemas.task_shemas import TaskCreate


async def create_task(db: AsyncSession, data: TaskCreate, *, user_id: int,) -> Task:
    task = Task(
        user_id=user_id,
        title=data.title,
        description=data.description,
        status=data.status,
        due_at=data.due_at,
    )

    db.add(task)

    await db.commit()
    await db.refresh(task)

    return task

async def list_tasks(db: AsyncSession, *, user_id: int, limit: int, offset: int,) -> list[Task]:
    statement = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.id.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await db.scalars(statement)

    return list(result.all())

async def get_task(db: AsyncSession, *, task_id: int, user_id: int,) -> Task | None:
    statement = (
        select(Task)
        .where(
            Task.id == task_id,
            Task.user_id == user_id,
        )
    )
    return await db.scalar(statement)
    