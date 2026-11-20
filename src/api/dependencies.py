from datetime import UTC, datetime
from typing import Annotated
from urllib.parse import urlsplit

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import get_settings
from src.db.session import get_async_session
from src.models import User, UserSession
from src.services.auth import hash_session_token

SessionDep = Annotated[
    AsyncSession,
    Depends(get_async_session),
]

async def check_request_origin(request: Request) -> None:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return
    origin = request.headers.get("origin")

    if origin is None:
        try:
            referer = urlsplit(request.headers.get("referer", ""))
            origin = f"{referer.scheme}://{referer.netloc}"
        except ValueError:
            origin = None

    if origin not in get_settings().trusted_origins:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden source of request",
        )

async def get_current_user(request: Request, db: SessionDep, _crsf: Annotated[None, Depends(check_request_origin)],) -> User:
    token = request.cookies.get(get_settings().session_cookie_name)

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You must sign in.",
        )
    
    user = await db.scalar(
        select(User)
        .join(UserSession, UserSession.user_id == User.id)
        .where(
            UserSession.token_hash == hash_session_token(token),
            UserSession.expires_at > datetime.now(UTC),
        )
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session is not valid or expired",
        )
    return user



CurrentUser = Annotated[
    User,
    Depends(get_current_user),
]
