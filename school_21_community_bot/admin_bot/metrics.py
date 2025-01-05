import logging
import os

import pandas as pd
from sqlalchemy.future import select
from telegram import Update
from telegram.ext import ContextTypes

from admin_bot.conversation import MAIN_ADMIN_MENU
from admin_bot.utils import admin_only, send_message
from models.base import async_session
from models.metric import Metric

logger = logging.getLogger(__name__)


@admin_only
async def export_metrics(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Экспортирует метрики в файл Excel и отправляет его администратору.
    """
    try:
        async with async_session() as session:
            result = await session.execute(select(Metric))
            metrics = result.scalars().all()

        data = [
            {
                "ID": metric.id,
                "User ID": metric.user_id,
                "Action": metric.action,
                "Data": metric.data,
                "Timestamp": metric.timestamp,
            }
            for metric in metrics
        ]
        df = pd.DataFrame(data)
        excel_path = "metrics_export.xlsx"
        df.to_excel(excel_path, index=False)

        with open(excel_path, "rb") as document:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=document,
                filename="metrics_export.xlsx",
                caption="Экспорт метрик в формате Excel.",
            )
        os.remove(excel_path)
        logger.info("Метрики экспортированы и отправлены пользователю.")
        return MAIN_ADMIN_MENU
    except Exception as e:
        logger.error(f"Ошибка в export_metrics: {e}")
        await send_message(
            update, context, "Произошла ошибка при экспорте метрик."
        )
        return MAIN_ADMIN_MENU
