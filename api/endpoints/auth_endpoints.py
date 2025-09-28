import requests
from core.users_controller import auth_backend, fastapi_users, get_jwt_strategy
from schemas.users import UserCreate, UserRead, VKAuthParams
from core.users_controller import create_user, optional_current_user
from fastapi import APIRouter, Depends, HTTPException, status
from cruds.users_crud import UsersCRUD
from cruds.institutes_crud import InstitutesCRUD
from db.session import get_async_session
from core.config import settings

from fastapi.logger import logger


api_router = APIRouter(prefix="/auth", tags=["auth"])

api_router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/jwt")


@api_router.post("/register", response_model=UserRead, status_code=201)
async def register_user(
    user: UserCreate,
    db=Depends(get_async_session),
    current_user=Depends(optional_current_user),
):
    users_crud = UsersCRUD(db)
    has_admin = await users_crud.has_admin()
    if has_admin and (current_user is None or not current_user.is_superuser):
        raise HTTPException(
            status_code=403,
            detail="Регистрация пользователей доступна только администратору",
        )
    if await users_crud.get_user_by_username(user.username):
        raise HTTPException(
            status_code=400, detail="Пользователь с таким username уже существует"
        )
    institute_crud = InstitutesCRUD(db)
    if not await institute_crud.get_institute_by_id(user.institute_id):
        raise HTTPException(status_code=400, detail="Институт не найден")

    user = await create_user(
        username=user.username,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        patronymic=user.patronymic,
        roles=user.roles,
        is_superuser=user.is_superuser if has_admin else True,
        institute_id=user.institute_id,
        birth_date=user.birth_date,
        group=user.group,
        vk_id=user.vk_id,
        is_verified=True,
    )
    if not has_admin:
        print("\033[93mАдминистратор создан\033[0m")
    print(user)
    return await users_crud.get_user_by_id(user.id)


@api_router.post("/vk/callback")
async def vk_callback(body: VKAuthParams, db=Depends(get_async_session)):
    response = requests.post(
        "https://id.vk.com/oauth2/auth",
        data={
            "grant_type": "authorization_code",
            "code_verifier": body.code_verifier,
            "code": body.code,
            "client_id": settings.VK_APP,
            "device_id": body.device_id,
            "state": body.state,
            "redirect_uri": settings.HOST,
        },
    )
    if response.json().get("error"):
        logger.error(f"VK auth error: {response.json()}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Ошибка авторизации"
        )
    user_request = requests.post(
        "https://id.vk.com/oauth2/user_info",
        data={
            "client_id": settings.VK_APP,
            "access_token": response.json()["access_token"],
        },
    )
    user = user_request.json()["user"]
    vk_user_id = int(user["user_id"])
    db_user = await UsersCRUD(db).get_user_by_vk_id(vk_user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден"
        )
    response = await auth_backend.login(strategy=get_jwt_strategy(), user=db_user)
    return response
