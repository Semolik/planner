import uuid
from datetime import date

from sqlalchemy import select

from api.cruds.base_crud import BaseCRUD
from api.models.user_models import RequiredPeriod, RolePeriodConfig
from sqlalchemy.orm import selectinload

from api.models.user_models import UserRole


class PeriodsCRUD(BaseCRUD):
    async def get_periods(self):
        query = (
            select(RequiredPeriod)
            .options(selectinload(RequiredPeriod.roles_config))
            .order_by(RequiredPeriod.period_end.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_period_from_range(self, date_from: date, date_to: date):
        query = (
            select(RequiredPeriod)
            .where(
                (RequiredPeriod.period_start <= date_to)
                & (RequiredPeriod.period_end >= date_from)
            )
            .options(selectinload(RequiredPeriod.roles_config))
            .order_by(RequiredPeriod.period_end.desc())
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_period_by_id(self, period_id: uuid.UUID):
        query = (
            select(RequiredPeriod)
            .where(RequiredPeriod.id == period_id)
            .options(selectinload(RequiredPeriod.roles_config))
        )
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_period(
        self,
        period_start: date,
        period_end: date,
        photographers_count: int,
        designers_count: int,
        copywriters_count: int,
    ):
        period = RequiredPeriod(period_start=period_start, period_end=period_end)
        period = await self.create(period)
        photographers_config = RolePeriodConfig(
            user_role=UserRole.PHOTOGRAPHER,
            count=photographers_count,
            required_period_id=period.id,
        )
        designers_config = RolePeriodConfig(
            user_role=UserRole.DESIGNER,
            count=designers_count,
            required_period_id=period.id,
        )
        copywriters_config = RolePeriodConfig(
            user_role=UserRole.COPYWRITER,
            count=copywriters_count,
            required_period_id=period.id,
        )
        await self.create(photographers_config)
        await self.create(designers_config)
        await self.create(copywriters_config)
        return period
