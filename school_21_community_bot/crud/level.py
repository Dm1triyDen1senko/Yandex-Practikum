from sqlalchemy.future import select

from models.base import async_session
from models.level import Level


async def get_levels():
    """Получение ролей из БД."""
    async with async_session() as session:
        result = await session.execute(select(Level.name))
        levels = result.scalars().all()
        return levels
