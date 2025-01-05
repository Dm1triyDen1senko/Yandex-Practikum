from sqlalchemy.future import select

from models.base import async_session
from models.user import User


async def get_teams_from_db():
    """Функция для получения списка команд из базы данных."""
    async with async_session() as session:
        result = await session.execute(select(User.team).distinct())
        teams = result.scalars().all()

    return teams
