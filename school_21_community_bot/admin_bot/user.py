from datetime import datetime
import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes

from admin_bot.constants import PAGINATION_SIZE
from admin_bot.conversation import (
    USER_ADD_FULL_NAME,
    USER_ADD_LEVEL_INPUT,
    USER_ADD_PROJECT,
    USER_ADD_ROLE_INPUT,
    USER_ADD_SBERCHAT_NICK,
    USER_ADD_SCHOOL21_NICK,
    USER_ADD_TEAM,
    USER_ADD_TELEGRAM_ID,
    USER_ADD_TELEGRAM_NICK,
    USER_DELETE_CONFIRM,
    USER_DETAIL,
    USER_EDIT_FIELD,
    USER_EDIT_LEVEL_INPUT,
    USER_EDIT_ROLE_INPUT,
    USER_EDIT_VALUE,
    USER_LIST,
)
from admin_bot.decorators import admin_only
from admin_bot.utils import main_admin_menu, send_message
from models.base import async_session
from models.level import Level
from models.role import Role
from models.user import User

logger = logging.getLogger(__name__)


@admin_only
async def user_add_full_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод полного имени пользователя.
    """
    full_name = update.message.text.strip()
    if not full_name:
        await update.message.reply_text(
            "Полное имя не может быть пустым. Пожалуйста, введите полное имя:"
        )
        return USER_ADD_FULL_NAME
    context.user_data["new_user_full_name"] = full_name
    await update.message.reply_text(
        "Введите Telegram ID пользователя (число):"
    )
    return USER_ADD_TELEGRAM_ID


@admin_only
async def user_add_telegram_id(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод Telegram ID пользователя.
    """
    telegram_id_str = update.message.text.strip()
    if not telegram_id_str.isdigit():
        await update.message.reply_text(
            "Telegram ID должен быть числом. Пожалуйста, "
            "введите корректный Telegram ID:"
        )
        return USER_ADD_TELEGRAM_ID
    telegram_id = int(telegram_id_str)
    context.user_data["new_user_telegram_id"] = telegram_id
    await update.message.reply_text("Введите ник в Telegram (без @):")
    return USER_ADD_TELEGRAM_NICK


@admin_only
async def user_add_telegram_nick(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод ника в Telegram.
    """
    telegram_nick = update.message.text.strip().lstrip("@")
    if not telegram_nick:
        await update.message.reply_text(
            "Ник в Telegram не может быть пустым. Пожалуйста, "
            "введите ник в Telegram:"
        )
        return USER_ADD_TELEGRAM_NICK
    context.user_data["new_user_telegram_nick"] = telegram_nick
    await update.message.reply_text("Введите ник в СберЧате:")
    return USER_ADD_SBERCHAT_NICK


@admin_only
async def user_add_sberchat_nick(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод ника в СберЧате.
    """
    sberchat_nick = update.message.text.strip()
    if not sberchat_nick:
        await update.message.reply_text(
            "Ник в СберЧате не может быть пустым. Пожалуйста, "
            "введите ник в СберЧате:"
        )
        return USER_ADD_SBERCHAT_NICK
    context.user_data["new_user_sberchat_nick"] = sberchat_nick
    await update.message.reply_text("Введите ник в Школе 21:")
    return USER_ADD_SCHOOL21_NICK


@admin_only
async def user_add_school21_nick(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод ника в Школе 21.
    """
    school21_nick = update.message.text.strip()
    if not school21_nick:
        await update.message.reply_text(
            "Ник в Школе 21 не может быть пустым. Пожалуйста, "
            "введите ник в Школе 21:"
        )
        return USER_ADD_SCHOOL21_NICK
    context.user_data["new_user_school21_nick"] = school21_nick
    await update.message.reply_text("Введите команду:")
    return USER_ADD_TEAM


@admin_only
async def user_add_team(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод команды пользователя.
    """
    team = update.message.text.strip()
    if not team:
        await update.message.reply_text(
            "Команда не может быть пустой. Пожалуйста, введите команду:"
        )
        return USER_ADD_TEAM
    context.user_data["new_user_team"] = team
    await update.message.reply_text("Введите роль пользователя:")
    return USER_ADD_ROLE_INPUT


@admin_only
async def user_add_role_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод роли пользователя.
    """
    role_input = update.message.text.strip()
    if not role_input:
        await update.message.reply_text(
            "Роль не может быть пустой. Пожалуйста, введите роль пользователя:"
        )
        return USER_ADD_ROLE_INPUT
    context.user_data["new_user_role_input"] = role_input
    await update.message.reply_text("Введите уровень пользователя:")
    return USER_ADD_LEVEL_INPUT


@admin_only
async def user_add_level_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод уровня пользователя.
    """
    level_input = update.message.text.strip()
    if not level_input:
        await update.message.reply_text(
            "Уровень не может быть пустым. Пожалуйста, введите "
            "уровень пользователя:"
        )
        return USER_ADD_LEVEL_INPUT
    context.user_data["new_user_level_input"] = level_input
    await update.message.reply_text("Введите проект:")
    return USER_ADD_PROJECT


@admin_only
async def user_add_project(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод проекта пользователя и сохраняет нового пользователя.
    """
    project = update.message.text.strip()
    if not project:
        await update.message.reply_text(
            "Проект не может быть пустым. Пожалуйста, введите проект:"
        )
        return USER_ADD_PROJECT
    context.user_data["new_user_project"] = project
    async with async_session() as session:
        try:
            existing_user = await session.execute(
                select(User).filter(
                    User.telegram_id == (
                        context.user_data["new_user_telegram_id"])
                )
            )
            existing_user = existing_user.scalar_one_or_none()
            if existing_user:
                await update.message.reply_text(
                    "Пользователь с таким Telegram ID уже существует."
                )
                from admin_bot.menu import user_menu
                return await user_menu(update, context)
            role_name = context.user_data.get("new_user_role_input")
            if not role_name:
                await update.message.reply_text(
                    "Роль не была введена. Пожалуйста, начните процесс "
                    "создания пользователя заново."
                )
                from admin_bot.menu import user_menu
                return await user_menu(update, context)
            role = await session.execute(
                select(Role).filter(Role.name.ilike(role_name))
            )
            role = role.scalar_one_or_none()
            if not role:
                role = Role(name=role_name)
                session.add(role)
                await session.commit()
                await session.refresh(role)
                logger.info(f"Создана новая роль: {role_name}")
            level_name = context.user_data.get("new_user_level_input")
            if not level_name:
                await update.message.reply_text(
                    "Уровень не был введен. Пожалуйста, начните процесс "
                    "создания пользователя заново."
                )
                return await user_menu(update, context)
            level = await session.execute(
                select(Level).filter(Level.name.ilike(level_name))
            )
            level = level.scalar_one_or_none()
            if not level:
                level = Level(name=level_name)
                session.add(level)
                await session.commit()
                await session.refresh(level)
                logger.info(f"Создан новый уровень: {level_name}")
            new_user = User(
                telegram_id=context.user_data["new_user_telegram_id"],
                full_name=context.user_data["new_user_full_name"],
                telegram_nick=context.user_data["new_user_telegram_nick"],
                sberchat_nick=context.user_data["new_user_sberchat_nick"],
                school21_nick=context.user_data["new_user_school21_nick"],
                team=context.user_data["new_user_team"],
                role=role.name,
                level=level.name,
                project=project,
                registration_date=datetime.utcnow(),
            )
            session.add(new_user)
            await session.commit()
            await update.message.reply_text(
                f"Пользователь '{new_user.full_name}' добавлен."
            )
            logger.info(f"Добавлен новый пользователь: {new_user.full_name}")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"SQLAlchemy ошибка при добавлении пользователя: {e}")
            await update.message.reply_text(
                "Произошла ошибка при добавлении пользователя."
            )
        except Exception as e:
            logger.error(
                f"Неизвестная ошибка при добавлении пользователя: {e}"
            )
            await update.message.reply_text(
                "Произошла неизвестная ошибка при добавлении пользователя."
            )
    from admin_bot.menu import user_menu
    return await user_menu(update, context)


@admin_only
async def show_users(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page: int = 0,
    action: str = None,
    filters: dict = None,
):
    """Отображает список пользователей с учетом фильтров и пагинации."""
    try:
        async with async_session() as session:
            query = select(User).order_by(User.school21_nick.asc())
            if filters:
                if "nickname" in filters:
                    query = query.filter(
                        User.school21_nick.ilike(f"%{filters['nickname']}%")
                    )
                if "team" in filters:
                    query = query.filter(User.team.ilike(
                        f"%{filters['team']}%"))
                if "role" in filters:
                    query = query.filter(User.role.ilike(
                        f"%{filters['role']}%"))
                if "alphabet" in filters:
                    query = query.filter(
                        User.school21_nick.ilike(f"{filters['alphabet']}%")
                    )
            query = query.offset(page * PAGINATION_SIZE).limit(PAGINATION_SIZE)
            result = await session.execute(query)
            users = result.scalars().all()
        keyboard = []
        for user in users:
            display_name = (
                user.school21_nick
                if user.school21_nick
                else f"@{user.telegram_nick}"
            )
            if action == "delete":
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"Удалить {display_name}",
                            callback_data=f"delete_user_{user.id}",
                        )
                    ]
                )
            elif action == "edit":
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"Редактировать {display_name}",
                            callback_data=f"edit_user_{user.id}",
                        )
                    ]
                )
            else:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"{display_name}", callback_data=f"user_{user.id}"
                        )
                    ]
                )
        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(
                InlineKeyboardButton(
                    "← Назад",
                    callback_data=(f"users_page_{page - 1}_{action or ''}_"
                                   f"{serialize_filters(filters)}"),
                )
            )
        if len(users) == PAGINATION_SIZE:
            navigation_buttons.append(
                InlineKeyboardButton(
                    "Далее →",
                    callback_data=(f"users_page_{page + 1}_{action or ''}_"
                                   f"{serialize_filters(filters)}"),
                )
            )
        if navigation_buttons:
            keyboard.append(navigation_buttons)
        search_button = InlineKeyboardButton("🔍 Поиск",
                                             callback_data="search_users")
        back_button = InlineKeyboardButton(
            "Назад в меню пользователей", callback_data="back_to_user_menu"
        )
        keyboard.append([search_button, back_button])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_message(update, context, "Список пользователей:",
                           reply_markup=reply_markup)
        return USER_LIST
    except Exception as e:
        logger.error(f"Ошибка в show_users: {e}")
        await send_message(
            update,
            context, "Произошла ошибка при отображении списка пользователей."
        )
        return ConversationHandler.END


def serialize_filters(filters: dict) -> str:
    """
    Сериализует словарь фильтров в строку для передачи в callback_data.
    Используется разделитель '|'.
    """
    if not filters:
        return "none"
    return "|".join([f"{key}:{value}" for key, value in filters.items()])


def deserialize_filters(filter_string: str) -> dict:
    """Десериализует строку фильтров обратно в словарь."""
    if filter_string == "none":
        return {}
    filters = {}
    for item in filter_string.split("|"):
        key, value = item.split(":", 1)
        filters[key] = value
    return filters


@admin_only
async def user_list_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обработчик действий в списке пользователей.
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    try:
        if data.startswith("user_"):
            user_id = int(data.split("_")[1])
            return await user_detail(update, context, user_id)
        elif data.startswith("edit_user_"):
            user_id = int(data.split("_")[2])
            context.user_data["edit_user_id"] = user_id
            return await edit_user_field(update, context)
        elif data.startswith("delete_user_"):
            user_id = int(data.split("_")[2])
            context.user_data["delete_user_id"] = user_id
            await query.edit_message_text(
                "Вы уверены, что хотите удалить пользователя? "
                "Это действие необратимо.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Да", callback_data="confirm_delete_user"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "Нет", callback_data="cancel_delete_user"
                            )
                        ],
                    ]
                ),
            )
            return USER_DELETE_CONFIRM
        elif data.startswith("users_page_"):
            parts = data.split("_")
            page = int(parts[2])
            action = parts[3] if len(parts) > 3 else None
            filter_string = parts[4] if len(parts) > 4 else "none"
            filters = deserialize_filters(filter_string)
            return await show_users(update, context, page=page,
                                    action=action, filters=filters)
        elif data == "back_to_user_menu":
            from admin_bot.menu import user_menu
            return await user_menu(update, context)
        elif data == "search_users":
            from admin_bot.search import search_menu
            return await search_menu(update, context)
        else:
            await query.edit_message_text("Неизвестная команда.")
            return USER_LIST
    except Exception as e:
        logger.error(f"Ошибка в user_list_handler: {e}")
        await query.edit_message_text(
            "Произошла ошибка при обработке команды."
        )
        return ConversationHandler.END


@admin_only
async def user_detail(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int
):
    """
    Отображает детали выбранного пользователя.
    """
    try:
        async with async_session() as session:
            result = await session.execute(
                select(User).filter(User.id == user_id)
            )
            user = result.scalar_one_or_none()

            if user:
                role = await session.execute(
                    select(Role).filter(Role.name.ilike(user.role))
                )
                role = role.scalar_one_or_none()

                level = await session.execute(
                    select(Level).filter(Level.name.ilike(user.level))
                )
                level = level.scalar_one_or_none()

                message = (
                    f"ID: {user.id}\n"
                    f"Telegram ID: {user.telegram_id}\n"
                    f"Полное имя: {user.full_name}\n"
                    f"Ник в Telegram: @{user.telegram_nick}\n"
                    f"Ник в СберЧате: {user.sberchat_nick}\n"
                    f"Ник в Школе 21: {user.school21_nick}\n"
                    f"Команда: {user.team}\n"
                    f"Роль: {user.role if user.role else 'Не установлена'}\n"
                    f"Уровень: {user.level if user.level else 'Не установлен'}\n"
                    f"Проект: {user.project}\n"
                    f"Дата регистрации: {user.registration_date}\n"
                )
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Редактировать",
                            callback_data=f"edit_user_{user.id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Удалить", callback_data=f"delete_user_{user.id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Назад к списку", callback_data="back_to_user_list"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Назад в меню", callback_data="back_to_admin_menu"
                        )
                    ],
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await send_message(update, context,
                                   message, reply_markup=reply_markup)
                return USER_DETAIL
            else:
                await send_message(update, context, "Пользователь не найден.")
                return USER_LIST
    except Exception as e:
        logger.error(f"Ошибка в user_detail: {e}")
        await send_message(
            update,
            context,
            "Произошла ошибка при получении деталей пользователя."
        )
        return USER_LIST


@admin_only
async def user_detail_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обработчик действий в деталях пользователя.
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    try:
        if data.startswith("edit_user_"):
            user_id = int(data.split("_")[2])
            context.user_data["edit_user_id"] = user_id
            return await edit_user_field(update, context)
        elif data.startswith("delete_user_"):
            user_id = int(data.split("_")[2])
            context.user_data["delete_user_id"] = user_id
            await query.edit_message_text(
                "Вы уверены, что хотите удалить пользователя? Это "
                "действие необратимо.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Да", callback_data="confirm_delete_user"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "Нет", callback_data="cancel_delete_user"
                            )
                        ],
                    ]
                ),
            )
            return USER_DELETE_CONFIRM
        elif data == "back_to_user_list":
            return await show_users(update, context, page=0)
        elif data == "back_to_admin_menu":
            return await main_admin_menu(update, context)
        else:
            await query.edit_message_text("Неизвестная команда.")
            return USER_DETAIL
    except Exception as e:
        logger.error(f"Ошибка в user_detail_handler: {e}")
        await query.edit_message_text(
            "Произошла ошибка при обработке команды."
        )
        return USER_DETAIL


@admin_only
async def user_delete_confirm_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает подтверждение или отмену удаления пользователя.
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = context.user_data.get("delete_user_id")
    try:
        if data == "confirm_delete_user":
            async with async_session() as session:
                result = await session.execute(
                    select(User).filter(User.id == user_id)
                )
                user = result.scalar_one_or_none()
                if user:
                    await session.delete(user)
                    await session.commit()
                    await query.edit_message_text("Пользователь удален.")
                    logger.info(f"Пользователь {user_id} удален.")
                else:
                    await query.edit_message_text("Пользователь не найден.")
            return await show_users(update, context, page=0)
        elif data == "cancel_delete_user":
            await query.edit_message_text("Удаление отменено.")
            return await user_detail(update, context, user_id)
        else:
            await query.edit_message_text("Неизвестная команда.")
            return USER_DELETE_CONFIRM
    except Exception as e:
        logger.error(f"Ошибка в user_delete_confirm_handler: {e}")
        await query.edit_message_text(
            "Произошла ошибка при подтверждении удаления."
        )
        return USER_DELETE_CONFIRM


@admin_only
async def edit_user_field(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Отображает меню выбора поля для редактирования пользователя.
    """
    try:
        user_id = context.user_data["edit_user_id"]
        keyboard = [
            [
                InlineKeyboardButton(
                    "Полное имя", callback_data="edit_full_name"
                )
            ],
            [
                InlineKeyboardButton(
                    "Ник в Telegram", callback_data="edit_telegram_nick"
                )
            ],
            [
                InlineKeyboardButton(
                    "Ник в СберЧате", callback_data="edit_sberchat_nick"
                )
            ],
            [
                InlineKeyboardButton(
                    "Ник в Школе 21", callback_data="edit_school21_nick"
                )
            ],
            [
                InlineKeyboardButton("Команда", callback_data="edit_team")
            ],
            [
                InlineKeyboardButton("Роль", callback_data="edit_role")
            ],
            [
                InlineKeyboardButton("Уровень", callback_data="edit_level")
            ],
            [
                InlineKeyboardButton("Проект", callback_data="edit_project")
            ],
            [
                InlineKeyboardButton(
                    "Назад", callback_data=f"user_{user_id}"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            "Выберите поле для редактирования:", reply_markup=reply_markup
        )
        return USER_EDIT_FIELD
    except Exception as e:
        logger.error(f"Ошибка в edit_user_field: {e}")
        await update.callback_query.edit_message_text(
            "Произошла ошибка при выборе поля для редактирования."
        )
        return ConversationHandler.END


@admin_only
async def user_edit_field_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает выбор поля для редактирования пользователя.
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    field_map = {
        "edit_full_name": "full_name",
        "edit_telegram_nick": "telegram_nick",
        "edit_sberchat_nick": "sberchat_nick",
        "edit_school21_nick": "school21_nick",
        "edit_team": "team",
        "edit_role": "role",
        "edit_level": "level",
        "edit_project": "project",
    }
    try:
        if data in field_map:
            field = field_map[data]
            context.user_data["edit_field"] = field
            if field == "role":
                await query.edit_message_text(
                    "Введите новую роль пользователя:"
                )
                return USER_EDIT_ROLE_INPUT
            elif field == "level":
                await query.edit_message_text(
                    "Введите новый уровень пользователя:"
                )
                return USER_EDIT_LEVEL_INPUT
            else:
                await query.edit_message_text("Введите новое значение:")
                return USER_EDIT_VALUE
        else:
            await query.edit_message_text("Неизвестная команда.")
            return USER_EDIT_FIELD
    except Exception as e:
        logger.error(f"Ошибка в user_edit_field_handler: {e}")
        await query.edit_message_text(
            "Произошла ошибка при обработке команды."
        )
        return USER_EDIT_FIELD


@admin_only
async def user_edit_role_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод новой роли пользователя и обновляет ее в базе данных.
    """
    role_input = update.message.text.strip()
    if not role_input:
        await update.message.reply_text(
            "Роль не может быть пустой. Пожалуйста, введите роль пользователя:"
        )
        return USER_EDIT_ROLE_INPUT
    context.user_data["edit_role_input"] = role_input
    await update.message.reply_text("Редактирование роли завершено.")
    user_id = context.user_data.get("edit_user_id")
    async with async_session() as session:
        try:
            role = await session.execute(
                select(Role).filter(Role.name.ilike(role_input))
            )
            role = role.scalar_one_or_none()
            if not role:
                role = Role(name=role_input)
                session.add(role)
                await session.commit()
                await session.refresh(role)
                logger.info(
                    f"Создана новая роль при редактировании: {role.name}"
                )
            user = await session.execute(
                select(User).filter(User.id == user_id)
            )
            user = user.scalar_one_or_none()
            if user:
                user.role = role.name
                await session.commit()
                logger.info(
                    f"Пользователь {user_id} обновил роль на '{role.name}'."
                )
                await send_message(update, context, "Роль успешно обновлена.")
                return await user_detail(update, context, user_id)
            else:
                await send_message(update, context, "Пользователь не найден.")
                return USER_LIST
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"SQLAlchemy ошибка при обновлении роли: {e}")
            await send_message(
                update,
                context,
                "Произошла ошибка при обновлении роли пользователя."
            )
            return USER_EDIT_FIELD
        except Exception as e:
            logger.error(f"Неизвестная ошибка при обновлении роли: {e}")
            await send_message(
                update,
                context,
                "Произошла неизвестная ошибка при "
                "обновлениироли пользователя."
            )
            return USER_EDIT_FIELD


@admin_only
async def user_edit_level_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод нового уровня пользователя и обновляет его в базе данных.
    """
    level_input = update.message.text.strip()
    if not level_input:
        await update.message.reply_text(
            "Уровень не может быть пустым. Пожалуйста, "
            "введите уровень пользователя:"
        )
        return USER_EDIT_LEVEL_INPUT
    context.user_data["edit_level_input"] = level_input
    await update.message.reply_text("Редактирование уровня завершено.")
    user_id = context.user_data.get("edit_user_id")
    async with async_session() as session:
        try:
            level = await session.execute(
                select(Level).filter(Level.name.ilike(level_input))
            )
            level = level.scalar_one_or_none()
            if not level:
                level = Level(name=level_input)
                session.add(level)
                await session.commit()
                await session.refresh(level)
                logger.info(
                    f"Создан новый уровень при редактировании: {level.name}"
                )
            user = await session.execute(
                select(User).filter(User.id == user_id)
            )
            user = user.scalar_one_or_none()
            if user:
                user.level = level.name
                await session.commit()
                logger.info(
                    f"Пользователь {user_id} обновил уровень "
                    f"на '{level.name}'."
                )
                await update.message.reply_text("Уровень успешно обновлен.")
                return await user_detail(update, context, user_id)
            else:
                await update.message.reply_text("Пользователь не найден.")
                return USER_LIST
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"SQLAlchemy ошибка при обновлении уровня: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обновлении уровня пользователя."
            )
            return USER_EDIT_FIELD
        except Exception as e:
            logger.error(f"Неизвестная ошибка при обновлении уровня: {e}")
            await update.message.reply_text(
                "Произошла неизвестная ошибка при обновлении "
                "уровня пользователя."
            )
            return USER_EDIT_FIELD


@admin_only
async def user_edit_value_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод нового значения для выбранного поля пользователя.
    """
    new_value = update.message.text.strip()
    user_id = context.user_data.get("edit_user_id")
    field = context.user_data.get("edit_field")
    if not user_id or not field:
        logger.error("Отсутствуют данные для редактирования пользователя.")
        await update.message.reply_text(
            "Произошла ошибка при получении данных для редактирования."
        )
        return ConversationHandler.END
    async with async_session() as session:
        try:
            result = await session.execute(
                select(User).filter(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            if user:
                if field == "telegram_id":
                    if not str(new_value).isdigit():
                        await update.message.reply_text(
                            "Telegram ID должен быть числом. Пожалуйста, "
                            "введите корректный Telegram ID:"
                        )
                        return USER_EDIT_VALUE
                    new_value = int(new_value)
                    existing_user = await session.execute(
                        select(User).filter(User.telegram_id == new_value)
                    )
                    existing_user = existing_user.scalar_one_or_none()
                    if existing_user and existing_user.id != user_id:
                        await update.message.reply_text(
                            "Пользователь с таким Telegram ID уже существует."
                        )
                        return USER_EDIT_VALUE
                setattr(user, field, new_value)
                await session.commit()
                await update.message.reply_text("Поле успешно обновлено.")
                logger.info(
                    f"Пользователь {user_id} обновил поле {field} "
                    f"на '{new_value}'."
                )
                return await user_detail(update, context, user_id)
            else:
                await update.message.reply_text("Пользователь не найден.")
                return USER_LIST
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"SQLAlchemy ошибка при редактировании "
                         f"пользователя: {e}")
            await update.message.reply_text(
                "Произошла ошибка при обновлении данных пользователя."
            )
            return USER_EDIT_VALUE
        except Exception as e:
            logger.error(f"Неизвестная ошибка при редактировании "
                         f"пользователя: {e}")
            await update.message.reply_text(
                "Произошла неизвестная ошибка при обновлении "
                "данных пользователя."
            )
            return USER_EDIT_VALUE
