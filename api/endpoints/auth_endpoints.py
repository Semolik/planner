from users_controller import auth_backend, fastapi_users
from schemas.users import UserCreate, UserReadShortWithEmail, UserRead
from users_controller import current_superuser, create_user, optional_current_user
from fastapi import APIRouter, Depends, HTTPException
from cruds.users_crud import UsersCRUD
from cruds.institutes_crud import InstitutesCRUD
from db.session import get_async_session


api_router = APIRouter(prefix="/auth", tags=["auth"])

api_router.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/jwt"
)

api_router.include_router(
    fastapi_users.get_reset_password_router(),
)
api_router.include_router(
    fastapi_users.get_verify_router(UserReadShortWithEmail),
)


@api_router.post("/register", response_model=UserRead, status_code=201)
async def register_user(user: UserCreate, db=Depends(get_async_session), current_user=Depends(optional_current_user)):
    users_crud = UsersCRUD(db)
    has_admin = await users_crud.has_admin()
    if has_admin and (current_user is None or not current_user.is_superuser):
        raise HTTPException(
            status_code=403, detail="Регистрация пользователей доступна только администратору")
    if await users_crud.get_user_by_email(user.email):
        raise HTTPException(
            status_code=400, detail="Пользователь с таким email уже существует")
    institute_crud = InstitutesCRUD(db)
    if not await institute_crud.get_institute_by_id(user.institute_id):
        raise HTTPException(
            status_code=400, detail="Институт не найден")

    user = await create_user(
        email=user.email,
        password=user.password,
        first_name=user.first_name,
        last_name=user.last_name,
        patronymic=user.patronymic,
        roles=user.roles,
        # если администратора нет, то создаем его
        is_superuser=user.is_superuser if has_admin else True,
        institute_id=user.institute_id,
        group=user.group,
        is_verified=True
    )
    if not has_admin:
        print("\033[93mАдминистратор создан\033[0m")
    return await users_crud.get_user_by_id(user.id)
