import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from config import get_settings
from src.core.security import (
    dummy_hash,
    get_password_hash,
    verify_password,
)
from src.models import User, UserSession
from src.shemas.user_shemas import UserCreate, UserSignIn


class EmailAlreadyExists(Exception):
    pass


class InvalidCredentials(Exception):
    pass

def hash_session_token(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()

def create_session(db: AsyncSession, user_id: int) -> str:
    token = secrets.token_urlsafe(32)

    db.add(
        UserSession(
            token_hash=hash_session_token(token),
            user_id=user_id,
            expires_at=datetime.now(UTC) + timedelta(
                seconds=get_settings().session_ttl_seconds
            ),
        )
    )
    return token

async def signup(db: AsyncSession, data: UserCreate) -> tuple[User, str]:
    email = str(data.email).lower()

    password_hash= await run_in_threadpool(
        get_password_hash,
        data.password.get_secret_value(),
    )

    user = User(
        email=email,
        password_hash=password_hash,
    )

    try:
        db.add(user)
        await db.flush()

        token = create_session(db, user.id)

        await db.commit()
    except IntegrityError as exc:
        await db.rollback()

        original = exc.orig
        constraint = getattr(
            getattr(original, "diag", None),
            "constraint_name",
            None,
        )

        if (
            getattr(original, "sqlstate", None) == "23505"
            and constraint == "users_email_key"
        ):
            raise EmailAlreadyExists from exc

        raise

    await db.refresh(user)

    return user, token

async def signin(db: AsyncSession, data: UserSignIn) -> tuple[User, str]:
    email = str(data.email).lower()

    user = await db.scalar(
        select(User).where(User.email == email)
    )

    stored_hash = user.password_hash if user is not None else dummy_hash

    password_is_valid = await run_in_threadpool(
        verify_password,
        data.password.get_secret_value(),
        stored_hash,
    )

    if user is None or not password_is_valid:
        raise InvalidCredentials

    token = create_session(db, user.id)
    await db.commit()

    return user, token

async def signout(db: AsyncSession, token: str) -> None:
    await db.execute(
        delete(UserSession).where(UserSession.token_hash == hash_session_token(token)
        )
    )
    await db.commit()