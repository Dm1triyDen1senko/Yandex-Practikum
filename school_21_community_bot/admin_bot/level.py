import logging

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes

from admin_bot.constants import PAGINATION_SIZE
from admin_bot.conversation import (
    LEVEL_ADD,
    LEVEL_DELETE_CONFIRM,
    LEVEL_DETAIL,
    LEVEL_LIST,
)
from admin_bot.decorators import admin_only
from admin_bot.utils import main_admin_menu, send_message
from models.base import async_session
from models.level import Level
from models.user import User

logger = logging.getLogger(__name__)


@admin_only
async def show_levels(
    update: Update, context: ContextTypes.DEFAULT_TYPE, page: int = 0
):
    """
    Отображает список уровней с пагинацией.
    """
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Level)
                .order_by(Level.id)
                .offset(page * PAGINATION_SIZE)
                .limit(PAGINATION_SIZE)
            )
            levels = result.scalars().all()
        keyboard = [
            [
                InlineKeyboardButton(
                    level.name, callback_data=f"level_{level.id}"
                )
            ]
            for level in levels
        ]
        navigation_buttons = []
        if page > 0:
            navigation_buttons.append(
                InlineKeyboardButton(
                    "← Назад", callback_data=f"levels_page_{page - 1}"
                )
            )
        if len(levels) == PAGINATION_SIZE:
            navigation_buttons.append(
                InlineKeyboardButton(
                    "Далее →", callback_data=f"levels_page_{page + 1}"
                )
            )
        if navigation_buttons:
            keyboard.append(navigation_buttons)

        keyboard.append(
            [InlineKeyboardButton("Добавить уровень",
                                  callback_data="add_level")]
        )
        keyboard.append(
            [InlineKeyboardButton("Назад в меню",
                                  callback_data="back_to_admin_menu")]
        )
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_message(update, context, "Список уровней:",
                           reply_markup=reply_markup)
        return LEVEL_LIST
    except Exception as e:
        logger.error(f"Ошибка в show_levels: {e}")
        await send_message(
            update, context, "Произошла ошибка при отображении списка уровней."
        )
        return ConversationHandler.END


@admin_only
async def level_list_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обработчик действий в списке уровней.
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    try:
        if data.startswith("level_"):
            level_id = int(data.split("_")[1])
            return await level_detail(update, context, level_id)
        elif data.startswith("levels_page_"):
            page = int(data.split("_")[2])
            return await show_levels(update, context, page=page)
        elif data == "add_level":
            await query.edit_message_text("Введите название нового уровня:")
            return LEVEL_ADD
        elif data == "back_to_admin_menu":
            return await main_admin_menu(update, context)
        else:
            await query.edit_message_text("Неизвестная команда.")
            return LEVEL_LIST
    except Exception as e:
        logger.error(f"Ошибка в level_list_handler: {e}")
        await query.edit_message_text(
            "Произошла ошибка при обработке команды."
        )
        return LEVEL_LIST


@admin_only
async def level_add_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод названия нового уровня и добавляет его в базу данных.
    """
    level_name = update.message.text.strip()
    if not level_name:
        await update.message.reply_text(
            "Название уровня не может быть пустым."
            "Пожалуйста, введите корректное название."
        )
        return LEVEL_ADD
    async with async_session() as session:
        try:
            existing_level = await session.execute(
                select(Level).filter(Level.name.ilike(level_name))
            )
            existing_level = existing_level.scalar_one_or_none()
            if existing_level:
                await update.message.reply_text(
                    "Уровень с таким названием уже существует."
                    "Пожалуйста, введите другое название."
                )
                return LEVEL_ADD
            new_level = Level(name=level_name)
            session.add(new_level)
            await session.commit()
            await update.message.reply_text(
                f"Уровень '{level_name}' добавлен."
            )
            logger.info(f"Добавлен новый уровень: {level_name}")
        except SQLAlchemyError as e:
            await session.rollback()
            logger.error(f"SQLAlchemy ошибка при добавлении уровня: {e}")
            await update.message.reply_text(
                "Произошла ошибка при добавлении уровня."
            )
        except Exception as e:
            logger.error(f"Неизвестная ошибка при добавлении уровня: {e}")
            await update.message.reply_text(
                "Произошла неизвестная ошибка при добавлении уровня."
            )
    return await show_levels(update, context, page=0)


@admin_only
async def level_detail(
    update: Update, context: ContextTypes.DEFAULT_TYPE, level_id: int
):
    """
    Отображает детали выбранного уровня.
    """
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Level).filter(Level.id == level_id)
            )
            level = result.scalar_one_or_none()
        if level:
            message = f"ID: {level.id}\nНазвание: {level.name}"
            keyboard = [
                [
                    InlineKeyboardButton(
                        "Удалить уровень",
                        callback_data=f"delete_level_{level.id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Просмотреть пользователей",
                        callback_data=f"view_users_level_{level.id}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Назад к списку", callback_data="back_to_level_list"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Назад в меню", callback_data="back_to_admin_menu"
                    )
                ],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(
                message, reply_markup=reply_markup
            )
            return LEVEL_DETAIL
        else:
            await update.callback_query.edit_message_text("Уровень не найден.")
            return LEVEL_LIST
    except Exception as e:
        logger.error(f"Ошибка в level_detail: {e}")
        await update.callback_query.edit_message_text(
            "Произошла ошибка при получении деталей уровня."
        )
        return LEVEL_LIST


@admin_only
async def level_detail_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обработчик действий в деталях уровня.
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    try:
        if data.startswith("delete_level_"):
            level_id = int(data.split("_")[2])
            context.user_data["delete_level_id"] = level_id
            await query.edit_message_text(
                "Вы уверены, что хотите удалить уровень? "
                "Это действие необратимо.",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "Да", callback_data="confirm_delete_level"
                            )
                        ],
                        [
                            InlineKeyboardButton(
                                "Нет", callback_data="cancel_delete_level"
                            )
                        ],
                    ]
                ),
            )
            return LEVEL_DELETE_CONFIRM
        elif data.startswith("view_users_level_"):
            level_id = int(data.split("_")[3])
            return await view_users_by_level(update, context, level_id)
        elif data == "back_to_level_list":
            return await show_levels(update, context, page=0)
        elif data == "back_to_admin_menu":
            return await main_admin_menu(update, context)
        else:
            await query.edit_message_text("Неизвестная команда.")
            return LEVEL_DETAIL
    except Exception as e:
        logger.error(f"Ошибка в level_detail_handler: {e}")
        await query.edit_message_text(
            "Произошла ошибка при обработке команды."
        )
        return LEVEL_DETAIL


@admin_only
async def level_delete_confirm_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает подтверждение или отмену удаления уровня.
    """
    query = update.callback_query
    await query.answer()
    level_id = context.user_data.get("delete_level_id")
    try:
        if query.data == "confirm_delete_level":
            async with async_session() as session:
                result = await session.execute(
                    select(Level).filter(Level.id == level_id)
                )
                level = result.scalar_one_or_none()
                if level:
                    users_with_level = await session.execute(
                        select(User).filter(User.level.ilike(level.name))
                    )
                    users_with_level = users_with_level.scalars().all()
                    if users_with_level:
                        await query.edit_message_text(
                            "Невозможно удалить уровень, так как "
                            "с ним связаны пользователи."
                        )
                        return LEVEL_DELETE_CONFIRM
                    await session.delete(level)
                    await session.commit()
                    await query.edit_message_text("Уровень удален.")
                    logger.info(f"Уровень {level_id} удален.")
                else:
                    await query.edit_message_text("Уровень не найден.")
            return await show_levels(update, context, page=0)
        elif query.data == "cancel_delete_level":
            await query.edit_message_text("Удаление отменено.")
            return await level_detail(update, context, level_id)
        else:
            await query.edit_message_text("Неизвестная команда.")
            return LEVEL_DELETE_CONFIRM
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"SQLAlchemy ошибка при удалении уровня: {e}")
        await query.edit_message_text(
            "Произошла ошибка при удалении уровня."
        )
        return LEVEL_DELETE_CONFIRM
    except Exception as e:
        logger.error(f"Неизвестная ошибка при удалении уровня: {e}")
        await query.edit_message_text(
            "Произошла неизвестная ошибка при удалении уровня."
        )
        return LEVEL_DELETE_CONFIRM


@admin_only
async def view_users_by_level(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    level_id: int,
):
    """
    Отображает список пользователей, связанных с определенным уровнем.
    """
    try:
        async with async_session() as session:
            result = await session.execute(
                select(Level).filter(Level.id == level_id)
            )
            level = result.scalar_one_or_none()
            if not level:
                await update.callback_query.edit_message_text(
                    "Уровень не найден."
                )
                return LEVEL_DETAIL
            users_result = await session.execute(
                select(User).filter(User.level.ilike(level.name))
            )
            users = users_result.scalars().all()
        if not users:
            message = f"Нет пользователей с уровнем '{level.name}'."
        else:
            message = f"Список пользователей с уровнем '{level.name}':\n\n"
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
                    "Назад к списку уровней",
                    callback_data="back_to_level_list"
                )
            ],
            [
                InlineKeyboardButton(
                    "Назад в меню", callback_data="back_to_admin_menu"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            message, reply_markup=reply_markup
        )
        return LEVEL_DETAIL
    except Exception as e:
        logger.error(f"Ошибка в view_users_by_level: {e}")
        await update.callback_query.edit_message_text(
            "Произошла ошибка при просмотре пользователей."
        )
        return LEVEL_DETAIL
