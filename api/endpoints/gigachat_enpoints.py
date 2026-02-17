from gigachat import GigaChat
from api.cruds.settings_crud import SettingsCRUD

from fastapi import APIRouter, Depends, Form
from fastapi.exceptions import HTTPException
from api.db.session import get_async_session
from api.core.users_controller import current_superuser
from pydantic import BaseModel

api_router = APIRouter(tags=["Gigachat"], prefix="/gigachat")


class BalanceResponse(BaseModel):
    total_tokens: float
    used_tokens: float
    remaining_tokens: float
    usage_percentage: float


class StatusResponse(BaseModel):
    gigachat_token_set: bool


@api_router.get("/status", dependencies=[Depends(current_superuser)])
async def get_status(db=Depends(get_async_session)) -> StatusResponse:
    """
    Получить статус наличия GigaChat токена
    """
    settings_crud = SettingsCRUD(db)
    gigachat_token = await settings_crud.get_setting("gigachat_token")

    return StatusResponse(gigachat_token_set=gigachat_token is not None)


@api_router.post("/token", status_code=204, dependencies=[Depends(current_superuser)])
async def set_token(
    token: str = Form(...),
    db=Depends(get_async_session),
):
    try:
        giga = GigaChat(credentials=token, verify_ssl_certs=False)
        response = giga.get_token()
        if not response:
            raise HTTPException(
                status_code=400,
                detail="Invalid token: Unable to get access token from GigaChat",
            )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid token: {str(e)}")

    settings_crud = SettingsCRUD(db)
    await settings_crud.set_setting(key="gigachat_token", value=token)


@api_router.delete("/token", status_code=204, dependencies=[Depends(current_superuser)])
async def delete_token(db=Depends(get_async_session)):
    settings_crud = SettingsCRUD(db)
    setting = await settings_crud.get_setting("gigachat_token")
    if setting:
        await settings_crud.delete(setting)


@api_router.get("/balance", dependencies=[Depends(current_superuser)])
async def get_balance(db=Depends(get_async_session)) -> BalanceResponse:
    settings_crud = SettingsCRUD(db)
    gigachat_token = await settings_crud.get_setting("gigachat_token")

    if not gigachat_token:
        raise HTTPException(status_code=400, detail="GigaChat token not configured")

    try:
        giga = GigaChat(
            credentials=gigachat_token.value,
            scope="GIGACHAT_API_PERS",
            model="GigaChat",
            verify_ssl_certs=False,
        )

        balance_response = giga.get_balance()
        gigachat_balance = None
        for balance_item in balance_response.balance:
            if balance_item.usage.lower() == "gigachat":
                gigachat_balance = balance_item.value
                break

        if gigachat_balance is None:
            raise HTTPException(
                status_code=400,
                detail="Could not retrieve GigaChat balance information",
            )

        total_tokens = 900000.0
        remaining_tokens = gigachat_balance
        used_tokens = total_tokens - remaining_tokens
        usage_percentage = (used_tokens / total_tokens) * 100

        return BalanceResponse(
            total_tokens=total_tokens,
            used_tokens=used_tokens,
            remaining_tokens=remaining_tokens,
            usage_percentage=usage_percentage,
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get balance: {str(e)}")
