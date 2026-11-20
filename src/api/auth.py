from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
    status,
)

from config import get_settings
from src.api.dependencies import (
    CurrentUser,
    SessionDep,
    check_request_origin,
)
from src.services import auth as auth_service
from src.shemas.user_shemas import (
    UserCreate,
    UserRead,
    UserSignIn,
)

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(check_request_origin)],)

def set_session_cookie(response: Response, token: str) -> None:
    settings = get_settings()

    response.set_cookie(
        key=settings.session_cookie_name,
        value=token,
        max_age=settings.session_ttl_seconds,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(data: UserCreate, response: Response, db: SessionDep):
    try:
        user, token = await auth_service.signup(db, data)
    except auth_service.EmailAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        ) from None

    set_session_cookie(response, token)
    return user

@router.post("/signin", response_model=UserRead)
async def signin(
    data: UserSignIn,
    response: Response,
    db: SessionDep,
):
    try:
        user, token = await auth_service.signin(db, data)
    except auth_service.InvalidCredentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email or password are incorrect",
        ) from None

    set_session_cookie(response, token)

    return user

@router.get("/me", response_model=UserRead)
async def me(user: CurrentUser, response: Response):
    response.headers["Cache-Control"] = "no-store"
    return user

@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(request: Request, db: SessionDep) -> Response:
    settings = get_settings()

    token = request.cookies.get(settings.session_cookie_name)

    if token:
        await auth_service.signout(db, token)

    response = Response(status_code=status.HTTP_204_NO_CONTENT)

    response.delete_cookie(
        key=settings.session_cookie_name,
        path="/",
        secure=settings.session_cookie_secure,
        httponly=True,
        samesite="lax",
    )

    return response