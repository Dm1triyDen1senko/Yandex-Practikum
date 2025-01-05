import logging

from telegram import Update
from telegram.ext import ContextTypes

from config import GROUP_ID
from crud.user import get_user_by_telegram_id, set_user_membership_status

logger = logging.getLogger(__name__)


async def approve_request(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Автоматически одобряет заявки на вступление в канал."""
    request = update.chat_join_request
    if request:
        try:
            user_telegram_id = update.effective_user.id
            user = await get_user_by_telegram_id(user_telegram_id)
            if user:
                await set_user_membership_status(user)
                await context.bot.approve_chat_join_request(
                    chat_id=GROUP_ID,
                    user_id=update.effective_user.id
                )
                logger.info(
                    f'Заявка от {update.effective_user.username} одобрена.')
            else:
                logger.info(
                    msg=(f'Пользователь {update.effective_user.username} '
                         'пытался вступить в сообщество, но получил отказ, '
                         'поскольку отсутствует в базе данных.'))
        except Exception as e:
            logger.info(
                msg=('Ошибка при одобрении заявки для '
                     f'пользователя {update.effective_user.username}: {e}'))
