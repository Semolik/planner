from pydantic import BaseModel, ConfigDict

from api.schemas.users import UserReadShort


class StatsMonth(BaseModel):
    model_config = ConfigDict(use_enum_values=False)

    photographer: int = 0
    copywriter: int = 0
    designer: int = 0


class StatsUser(BaseModel):
    user: UserReadShort
    stats: dict[int, StatsMonth]  # month: count
