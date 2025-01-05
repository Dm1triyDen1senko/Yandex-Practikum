import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.ext import ConversationHandler, ContextTypes

from admin_bot.constants import PAGINATION_SIZE
from admin_bot.conversation import (
    ROLE_ADD,
    ROLE_DELETE_CONFIRM,
    ROLE_DETAIL,
    ROLE_LIST,
)
from admin_bot.decorators import admin_only
from admin_bot.utils import main_admin_menu, send_message
from models.base import async_session
from models.role import Role
from models.user import User

logger = logging.getLogger(__name__)


@admin_only
async def show_roles(
    update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0
):
    """
    Отображает список ролей с пагинацией.
    """
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Role)
                .order_by(Role.id)
                .offset(page * PAGINATION_SIZE)
                .limit(PAGINATION_SIZE)
            )
            roles = result.scalars().all()
        keyboard = [
            [
                InlineKeyboardButton(
                    role.name, callback_data=f"role_{role.id}"
                )
            ]
            for role in roles
        ]
        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(
                InlineKeyboardButton(
                    "← Назад", callback_data=f"roles_page_{page - 1}"
                )
            )
        if len(roles) == PAGINATION_SIZE:
            navigation_buttons.append(
                InlineKeyboardButton(
                    "Далее →", callback_data=f"roles_page_{page + 1}"
                )
            )
        if navigation_buttons:
            keyboard.append(navigation_buttons)
        keyboard.append(
            [InlineKeyboardButton("Добавить роль", callback_data="add_role")]
        )
        keyboard.append(
            [InlineKeyboardButton("Назад в меню",
                                  callback_data="back_to_admin_menu")]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_message(update, context, "Список ролей:",
                           reply_markup=reply_markup)
        return ROLE_LIST
    except Exception as e:
        logger.error(f"Ошибка в show_roles: {e}")
        await send_message(
            update, context, "Произошла ошибка при отображении списка ролей."
        )
        return ConversationHandler.END


@admin_only
async def role_list_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обработчик действий в списке ролей.
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    try:
        if data.startswith("role_"):
            role_id = int(data.split("_")[1])
            context.user_data["role_id"] = role_id
            return await role_detail_handler(update, context)
        elif data.startswith("roles_page_"):
            page = int(data.split("_")[2])
            return await show_roles(update, context, page=page)
        elif data == "add_role":
            await send_message(update, context, "Введите название новой роли:")
            return ROLE_ADD
        elif data == "back_to_admin_menu":
            return await main_admin_menu(update, context)
        else:
            await send_message(update, context, "Неизвестная команда.")
            return ROLE_LIST
    except Exception as e:
        logger.error(f"Ошибка в role_list_handler: {e}")
        await send_message(
            update, context, "Произошла ошибка при обработке команды."
        )
        return ROLE_LIST


@admin_only
async def role_add_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод названия новой роли и добавляет ее в базу данных.
    """
    role_name = update.message.text.strip()
    if not role_name:
        await update.message.reply_text(
            "Название роли не может быть пустым. "
            "Пожалуйста, введите корректное название."
        )
        return ROLE_ADD
    async with async_session() as session:
        try:
            existing_role = await session.execute(
                select(Role).filter(Role.name.ilike(role_name))
            )
            existing_role = existing_role.scalar_one_or_none()
            if existing_role:
                await update.message.reply_text(
                    "Роль с таким названием уже существует. "
                    "Пожалуйста, введите другое название."
                )
                return ROLE_ADD
            new_role = Role(name=role_name)
            session.add(new_role)
            await session.commit()
            await update.message.reply_text(f"Роль '{role_name}' добавлена.")
            logger.info(f"Добавлена новая роль: {role_name}")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"SQLAlchemy ошибка при добавлении роли: {e}")
            await update.message.reply_text(
                "Произошла ошибка при добавлении роли."
            )
        except Exception as e:
            logger.error(f"Неизвестная ошибка при добавлении роли: {e}")
            await update.message.reply_text(
                "Произошла неизвестная ошибка при добавлении роли."
            )
    return await show_roles(update, context, page=0)


@admin_only
async def role_detail_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обработчик действий в деталях роли.
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    role_id = context.user_data.get("role_id")
    try:
        if data.startswith("role_"):
            role_id = int(data.split("_")[1])
            context.user_data["role_id"] = role_id
            async with async_session() as session:
                result = await session.execute(
                    select(Role).filter(Role.id == role_id)
                )
                role = result.scalar_one_or_none()
            if role:
                message = f"ID: {role.id}\nНазвание: {role.name}"
                keyboard = [
                    [
                        InlineKeyboardButton(
                            "Удалить роль",
                            callback_data=f"delete_role_{role.id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Просмотреть пользователей",
                            callback_data=f"view_users_role_{role.id}",
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "Назад к списку ролей",
                            callback_data="back_to_role_list"
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
                return ROLE_DETAIL
            else:
                await send_message(update, context, "Роль не найдена.")
                return ROLE_LIST
        elif data.startswith("delete_role_"):
            role_id = int(data.split("_")[2])
            context.user_data["delete_role_id"] = role_id
            await send_message(
                update,
                context,
                "Вы уверены, что хотите удалить роль? "
                "Это действие необратимо.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Да", callback_data="confirm_delete_role"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "Нет", callback_data="cancel_delete_role"
                            )
                        ],
                    ]
                ),
            )
            return ROLE_DELETE_CONFIRM
        elif data.startswith("view_users_role_"):
            role_id = int(data.split("_")[3])
            context.user_data["role_id"] = role_id
            return await view_users_by_role(update, context)
        elif data == "back_to_role_list":
            return await show_roles(update, context, page=0)
        elif data == "back_to_admin_menu":
            return await main_admin_menu(update, context)
        else:
            await send_message(update, context, "Неизвестная команда.")
            return ROLE_DETAIL
    except Exception as e:
        logger.error(f"Ошибка в role_detail_handler: {e}")
        await send_message(
            update, context, "Произошла ошибка при обработке команды."
        )
        return ROLE_DETAIL


@admin_only
async def role_delete_confirm_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает подтверждение или отмену удаления роли.
    """
    query = update.callback_query
    await query.answer()
    role_id = context.user_data.get("delete_role_id")
    try:
        if query.data == "confirm_delete_role":
            async with async_session() as session:
                result = await session.execute(
                    select(Role).filter(Role.id == role_id)
                )
                role = result.scalar_one_or_none()
                if role:
                    users_with_role = await session.execute(
                        select(User).filter(User.role.ilike(role.name))
                    )
                    users_with_role = users_with_role.scalars().all()
                    if users_with_role:
                        await send_message(
                            update,
                            context,
                            "Невозможно удалить роль, так как с "
                            "ней связаны пользователи."
                        )
                        return ROLE_DELETE_CONFIRM
                    await session.delete(role)
                    await session.commit()
                    await send_message(update, context, "Роль удалена.")
                    logger.info(f"Роль {role_id} удалена.")
                else:
                    await send_message(update, context, "Роль не найдена.")
            return await show_roles(update, context, page=0)
        elif query.data == "cancel_delete_role":
            await send_message(update, context, "Удаление отменено.")
            return await role_detail_handler(update, context)
        else:
            await send_message(update, context, "Неизвестная команда.")
            return ROLE_DELETE_CONFIRM
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"SQLAlchemy ошибка при удалении роли: {e}")
        await send_message(
            update, context, "Произошла ошибка при удалении роли."
        )
        return ROLE_DELETE_CONFIRM
    except Exception as e:
        logger.error(f"Неизвестная ошибка при удалении роли: {e}")
        await send_message(
            update, context, "Произошла неизвестная ошибка при удалении роли."
        )
        return ROLE_DELETE_CONFIRM


@admin_only
async def view_users_by_role(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Отображает список пользователей, связанных с определенной ролью.
    """
    role_id = context.user_data.get("role_id")
    if not role_id:
        logger.error("role_id отсутствует в context.user_data")
        await send_message(update,
                           context, "Произошла ошибка при извлечении role_id.")
        return ROLE_DETAIL
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Role).filter(Role.id == role_id)
            )
            role = result.scalar_one_or_none()
            if not role:
                await send_message(update, context, "Роль не найдена.")
                return ROLE_DETAIL
            users_result = await session.execute(
                select(User).filter(User.role.ilike(role.name))
            )
            users = users_result.scalars().all()
        if not users:
            message = f"Нет пользователей с ролью '{role.name}'."
        else:
            message = f"Список пользователей с ролью '{role.name}':\n\n"
            for user in users:
                display_name = (
                    user.school21_nick
                    if user.school21_nick
                    else f"@{user.telegram_nick}"
                )
                message += f"• {display_name} (ID: {user.id})\n"
        keyboard = [
            [
                InlineKeyboardButton(
                    "Назад к списку ролей", callback_data="back_to_role_list"
                )
            ],
            [
                InlineKeyboardButton(
                    "Назад в меню", callback_data="back_to_admin_menu"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_message(update, context, message, reply_markup=reply_markup)
        return ROLE_DETAIL
    except Exception as e:
        logger.error(f"Ошибка в view_users_by_role: {e}")
        await send_message(
            update, context, "Произошла ошибка при просмотре пользователей."
        )
        return ROLE_DETAIL
