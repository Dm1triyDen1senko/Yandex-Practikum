import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select

from constants import ServiceConstant
from models.base import async_session
from models.role import Role
from models.user import User

logger = logging.getLogger(__name__)


async def get_role_by_name(session, role_name: str) -> Role:
    try:
        result = await session.execute(
            select(Role).where(Role.name == role_name)
        )
        role = result.scalar_one_or_none()
        return role
    except SQLAlchemyError:
        logger.error(f'Ошибка при получении роли "{role_name}"')
        return None


async def create_role(session, role_name: str) -> Role:
    try:
        new_role = Role(name=role_name)
        session.add(new_role)
        await session.flush()
        await session.refresh(new_role)
        return new_role
    except SQLAlchemyError:
        logger.error(f'Ошибка при создании роли "{role_name}"')
        return None


async def set_user_invitation_status(user):
    async with async_session() as session:
        setattr(user, 'invite_sent', True)
        session.add(user)
        await session.commit()


async def set_user_membership_status(user):
    async with async_session() as session:
        setattr(user, 'is_member', True)
        session.add(user)
        await session.commit()


async def create_or_update_user(user_data):
    try:
        async with async_session() as session:
            async with session.begin():
                role_name = user_data.get('role')
                if role_name:
                    role = await get_role_by_name(session, role_name)
                    if not role:
                        role = await create_role(session, role_name)
                        if not role:
                            logger.error(f'Не удалось создать роль: "{role}"')
                            return False
                    user_data['role'] = role.name
                result = await session.execute(
                    select(User).where(
                        (User.telegram_id == user_data['telegram_id']) |
                        (User.telegram_nick == user_data['telegram_nick'])
                    )
                )
                if user := result.scalar_one_or_none():
                    for key, value in user_data.items():
                        setattr(user, key, value)
                else:
                    user = User(**user_data)
                    session.add(user)
                await session.commit()
            return user
    except SQLAlchemyError:
        logger.error(f'Ошибка при создании пользователя "{user}"')
        return None


async def get_peers_by_role_and_level(
    role, level, offset=0, limit=ServiceConstant.PAGE_SIZE
):
    """Функция для получения людей по роли и уровню."""
    async with async_session() as session:
        query = select(User).filter(User.role == role)

        if level != 'Неважно':
            query = query.filter(User.level == level)
        result = await session.execute(query.offset(offset).limit(limit))
        people = result.scalars().all()

    return people


async def get_person_details(telegram_nick):
    """Функция для получения информации о работнике по никнейму в Телеграме."""
    async with async_session() as session:
        result = await session.execute(
            select(User).filter(User.telegram_nick == telegram_nick)
        )
        person = result.scalar_one_or_none()

    return person


async def get_user_by_telegram_id(user_telegram_id):
    """Получение user по его id."""
    async with async_session() as session:
        result = await session.execute(select(User).filter(
            User.telegram_id == user_telegram_id))
        user = result.scalars().first()
        return user


async def get_people_by_team_name(
        team, offset=0, limit=ServiceConstant.PAGE_SIZE
):
    """Функция для получения пиров по названию команды."""
    async with async_session() as session:
        query = select(User).filter(User.team == team)

        if team != 'Неважно':
            query = query.filter(User.team == team)
        result = await session.execute(query.offset(offset).limit(limit))
        people = result.scalars().all()

        return people


async def get_people_by_nickname(
    nickname, offset=0, limit=ServiceConstant.PAGE_SIZE
):
    """Функция для получения пиров по никнейму."""
    async with async_session() as session:
        try:
            query = select(User).filter(
                (User.telegram_nick.ilike(f'%{nickname}%')) |
                (User.sberchat_nick.ilike(f'%{nickname}%')) |
                (User.school21_nick.ilike(f'%{nickname}%'))
            )
            result = await session.execute(query.offset(offset).limit(limit))
            people = result.scalars().all()
            return people
        except SQLAlchemyError:
            return []


async def get_user_by_school21_nick(school21_nick: str):
    """Возвращает пользователя по никнейму в Школе 21, если он существует."""
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.school21_nick == school21_nick)
        )
        user = result.scalar_one_or_none()
        return user
