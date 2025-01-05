import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from admin_bot.conversation import MAIN_ADMIN_MENU
from admin_bot.decorators import admin_only

logger = logging.getLogger(__name__)


async def unknown_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает неизвестные команды.
    """
    await update.message.reply_text("Неизвестная команда.")


async def send_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str,
    reply_markup=None
):
    """
    Вспомогательная функция для отправки сообщений.
    """
    try:
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text, reply_markup=reply_markup
            )
        elif update.message:
            await update.message.reply_text(text, reply_markup=reply_markup)
    except Exception as e:
        logger.exception(f"Ошибка при отправке сообщения: {e}")


@admin_only
async def main_admin_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Отображает главное меню администратора.
    """
    try:
        keyboard = [
            [InlineKeyboardButton("Пользователи", callback_data="users")],
            [InlineKeyboardButton("Роли", callback_data="roles")],
            [InlineKeyboardButton("Уровни", callback_data="levels")],
            [InlineKeyboardButton("Экспорт метрик", callback_data="metrics")],
            [InlineKeyboardButton("Закрыть меню", callback_data="close_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await send_message(
            update,
            context,
            "Добро пожаловать в админ-панель. Выберите действие:",
            reply_markup=reply_markup,
        )
        return MAIN_ADMIN_MENU
    except Exception as e:
        logger.error(f"Ошибка в main_admin_menu: {e}")
        await send_message(
            update,
            context,
            "Произошла ошибка при отображении админ-панели.",
        )
        return ConversationHandler.END
