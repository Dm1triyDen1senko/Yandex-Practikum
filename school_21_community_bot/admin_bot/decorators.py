import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import ADMIN_USER_IDS
from admin_bot.conversation import ConversationHandler

logger = logging.getLogger(__name__)


def admin_only(func):
    """
    Декоратор для проверки доступа к админ-боту.
    """

    async def wrapper(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs
    ):
        """
        Обертка функции для проверки прав доступа.
        """
        user = update.effective_user
        logger.debug(f"Проверка пользователя: {user}")
        if user is None:
            logger.warning("Получено обновление без пользователя.")
            return ConversationHandler.END
        user_id = user.id
        if user_id in ADMIN_USER_IDS:
            logger.info(f"Пользователь {user_id} имеет доступ к админ-боту.")
            return await func(update, context, *args, **kwargs)
        else:
            logger.warning(
                f"Пользователь {user_id} попытался "
                f"получить доступ к админ-боту без прав."
            )
            if update.message:
                await update.message.reply_text(
                    "У вас нет доступа к этому боту."
                )
            elif update.callback_query:
                await update.callback_query.answer(
                    "У вас нет доступа к этому боту.", show_alert=True
                )
            return ConversationHandler.END
    return wrapper
