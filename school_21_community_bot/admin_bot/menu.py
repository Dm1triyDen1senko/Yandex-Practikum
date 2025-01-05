import logging

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Update,
)
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
)

from admin_bot.conversation import (
    ADMIN_MENU,
    MAIN_ADMIN_MENU,
    USER_ADD_FULL_NAME,
    USER_MENU,
)
from admin_bot.decorators import admin_only
from admin_bot.level import show_levels
from admin_bot.metrics import export_metrics
from admin_bot.role import show_roles
from admin_bot.user import show_users
from admin_bot.utils import main_admin_menu, send_message

logger = logging.getLogger(__name__)


@admin_only
async def start_admin(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обработчик команды /start для администраторов.
    """
    try:
        menu_button = KeyboardButton("🍔 Меню")
        custom_keyboard = ReplyKeyboardMarkup(
            [[menu_button]],
            resize_keyboard=True,
            one_time_keyboard=False,
        )

        await send_message(
            update,
            context,
            "Добро пожаловать! Нажмите на кнопку 🍔 Меню, "
            "чтобы открыть админ-панель.",
            reply_markup=custom_keyboard,
        )
        return ADMIN_MENU
    except Exception as e:
        logger.error(f"Ошибка в start_admin: {e}")
        await send_message(
            update, context, "Произошла ошибка при запуске админ-панели."
        )
        return ConversationHandler.END


@admin_only
async def admin_menu_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обработчик действий в главном меню администратора.
    """
    query = update.callback_query
    if query:
        await query.answer()
        data = query.data
    else:
        data = update.message.text

    if data == "🍔 Меню":
        return await main_admin_menu(update, context)
    elif data == "users":
        return await user_menu(update, context)
    elif data == "roles":
        return await show_roles(update, context, page=0)
    elif data == "levels":
        return await show_levels(update, context, page=0)
    elif data == "metrics":
        return await export_metrics(update, context)
    elif data == "close_menu":
        await send_message(
            update,
            context,
            "Меню закрыто.",
        )
        return ConversationHandler.END
    else:
        if query:
            await query.edit_message_text("Неизвестная команда.")
        else:
            await send_message(update, context, "Неизвестная команда.")
        return MAIN_ADMIN_MENU


@admin_only
async def user_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Отображает меню управления пользователями.
    """
    try:
        keyboard = [
            [
                InlineKeyboardButton(
                    "Получить список пользователей",
                    callback_data="list_users"
                )
            ],
            [
                InlineKeyboardButton(
                    "Добавить пользователя", callback_data="add_user"
                )
            ],
            [
                InlineKeyboardButton(
                    "Удалить пользователя", callback_data="delete_user"
                )
            ],
            [
                InlineKeyboardButton(
                    "Редактировать данные", callback_data="edit_user"
                )
            ],
            [
                InlineKeyboardButton(
                    "Поиск пользователей", callback_data="search_users"
                )
            ],
            [
                InlineKeyboardButton(
                    "Назад в меню", callback_data="back_to_admin_menu"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if update.callback_query:
            await update.callback_query.edit_message_text(
                "Меню пользователей:", reply_markup=reply_markup
            )
        else:
            await update.message.reply_text(
                "Меню пользователей:", reply_markup=reply_markup
            )
        return USER_MENU
    except Exception as e:
        logger.error(f"Ошибка в user_menu: {e}")
        await send_message(
            update,
            context,
            "Произошла ошибка при отображении меню пользователей.",
        )
        return ConversationHandler.END


@admin_only
async def user_menu_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обработчик действий в меню пользователей.
    """
    query = update.callback_query
    if query:
        await query.answer()
        data = query.data
    else:
        data = update.message.text

    if data == "list_users":
        return await show_users(update, context, page=0)
    elif data == "add_user":
        await send_message(update, context, "Введите полное имя пользователя:")
        return USER_ADD_FULL_NAME
    elif data == "delete_user":
        return await show_users(update, context, page=0, action="delete")
    elif data == "edit_user":
        return await show_users(update, context, page=0, action="edit")
    elif data == "search_users":
        from admin_bot.search import search_menu
        return await search_menu(update, context)
    elif data == "back_to_admin_menu":
        return await main_admin_menu(update, context)
    elif data == "🍔 Меню":
        return await main_admin_menu(update, context)
    elif data == "close_menu":
        await send_message(
            update,
            context,
            "Меню закрыто.",
        )
        return ConversationHandler.END
    else:
        if query:
            await query.edit_message_text("Неизвестная команда.")
        else:
            await send_message(update, context, "Неизвестная команда.")
        return USER_MENU
