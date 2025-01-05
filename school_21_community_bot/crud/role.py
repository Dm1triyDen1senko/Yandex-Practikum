from sqlalchemy.future import select

from models.base import async_session
from models.role import Role


async def get_roles_from_db():
    """Функция для получения списка ролей из базы данных."""
    async with async_session() as session:
        result = await session.execute(select(Role.name))
        roles = result.scalars().all()

    return roles
