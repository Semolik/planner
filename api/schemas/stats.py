from pydantic import BaseModel

from schemas.users import UserReadShort


class StatsUser(BaseModel):
    user: UserReadShort
    stats: dict[int, int]  # month: count
