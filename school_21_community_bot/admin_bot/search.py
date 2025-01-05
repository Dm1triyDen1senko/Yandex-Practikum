import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ConversationHandler, ContextTypes
from admin_bot.conversation import (
    SEARCH_ALPHABET,
    SEARCH_MENU,
    SEARCH_NICKNAME,
    SEARCH_ROLE,
    SEARCH_TEAM,
)
from admin_bot.decorators import admin_only

logger = logging.getLogger(__name__)


@admin_only
async def search_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Отображает меню типов поиска пользователей.
    """
    try:
        keyboard = [
            [
                InlineKeyboardButton(
                    "Поиск по никнейму Школы 21",
                    callback_data="search_nickname",
                )
            ],
            [
                InlineKeyboardButton(
                    "Поиск по команде", callback_data="search_team"
                )
            ],
            [
                InlineKeyboardButton(
                    "Поиск по роли", callback_data="search_role"
                )
            ],
            [
                InlineKeyboardButton(
                    "Фильтрация по алфавиту (Латиница)",
                    callback_data="search_alphabet",
                )
            ],
            [
                InlineKeyboardButton(
                    "Назад в меню пользователей",
                    callback_data="back_to_user_menu"
                )
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(
            "Выберите тип поиска:", reply_markup=reply_markup
        )
        return SEARCH_MENU
    except Exception as e:
        logger.error(f"Ошибка в search_menu: {e}")
        await update.callback_query.edit_message_text(
            "Произошла ошибка при отображении меню поиска."
        )
        return ConversationHandler.END


@admin_only
async def search_menu_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает выбор типа поиска.
    """
    query = update.callback_query
    await query.answer()
    data = query.data

    try:
        if data == "search_nickname":
            await query.edit_message_text(
                "Введите никнейм Школы 21 для поиска:"
            )
            return SEARCH_NICKNAME
        elif data == "search_team":
            await query.edit_message_text(
                "Введите название команды для поиска:"
            )
            return SEARCH_TEAM
        elif data == "search_role":
            await query.edit_message_text(
                "Введите название роли для поиска:"
            )
            return SEARCH_ROLE
        elif data == "search_alphabet":
            return await search_alphabet_menu(update, context)
        elif data == "back_to_user_menu":
            from admin_bot.menu import user_menu
            return await user_menu(update, context)
        else:
            await query.edit_message_text("Неизвестная команда.")
            return SEARCH_MENU
    except Exception as e:
        logger.error(f"Ошибка в search_menu_handler: {e}")
        await query.edit_message_text(
            "Произошла ошибка при обработке команды поиска."
        )
        return SEARCH_MENU


@admin_only
async def search_alphabet_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Отображает меню алфавитной фильтрации.
    """
    try:
        latin_letters = [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F",
            "G",
            "H",
            "I",
            "J",
            "K",
            "L",
            "M",
            "N",
            "O",
            "P",
            "Q",
            "R",
            "S",
            "T",
            "U",
            "V",
            "W",
            "X",
            "Y",
            "Z",
        ]
        buttons = []
        for i in range(0, len(latin_letters), 5):
            row = [
                InlineKeyboardButton(
                    letter, callback_data=f"alphabet_{letter}"
                )
                for letter in latin_letters[i:i + 5]
            ]
            buttons.append(row)
        buttons.append(
            [InlineKeyboardButton("Назад", callback_data="search_menu")]
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await update.callback_query.edit_message_text(
            "Выберите первую букву никнейма Школы 21 для фильтрации:",
            reply_markup=reply_markup,
        )
        return SEARCH_ALPHABET
    except Exception as e:
        logger.error(f"Ошибка в search_alphabet_menu: {e}")
        await update.callback_query.edit_message_text(
            "Произошла ошибка при отображении алфавитного меню."
        )
        return ConversationHandler.END


@admin_only
async def search_alphabet_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает выбор буквы для алфавитной фильтрации.
    """
    query = update.callback_query
    await query.answer()
    data = query.data
    try:
        if data.startswith("alphabet_"):
            letter = data.split("_")[1]
            filters = {"alphabet": letter}
            from admin_bot.user import show_users
            return await show_users(update, context, page=0, filters=filters)
        elif data == "search_menu":
            return await search_menu(update, context)
        else:
            await query.edit_message_text("Неизвестная команда.")
            return SEARCH_ALPHABET
    except Exception as e:
        logger.error(f"Ошибка в search_alphabet_handler: {e}")
        await query.edit_message_text(
            "Произошла ошибка при обработке алфавитного фильтра."
        )
        return SEARCH_ALPHABET


@admin_only
async def search_nickname_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод никнейма для поиска.
    """
    nickname = update.message.text.strip()
    if not nickname:
        await update.message.reply_text(
            "Никнейм Школы 21 не может быть пустым. "
            "Пожалуйста, введите никнейм для поиска:"
        )
        return SEARCH_NICKNAME
    filters = {"nickname": nickname}
    from admin_bot.user import show_users
    return await show_users(update, context, page=0, filters=filters)


@admin_only
async def search_team_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод названия команды для поиска.
    """
    team = update.message.text.strip()
    if not team:
        await update.message.reply_text(
            "Название команды не может быть пустым. "
            "Пожалуйста, введите название команды для поиска:"
        )
        return SEARCH_TEAM
    filters = {"team": team}
    from admin_bot.user import show_users
    return await show_users(update, context, page=0, filters=filters)


@admin_only
async def search_role_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ввод названия роли для поиска.
    """
    role = update.message.text.strip()
    if not role:
        await update.message.reply_text(
            "Название роли не может быть пустым. Пожалуйста, "
            "введите название роли для поиска:"
        )
        return SEARCH_ROLE
    filters = {"role": role}
    from admin_bot.user import show_users
    return await show_users(update, context, page=0, filters=filters)
