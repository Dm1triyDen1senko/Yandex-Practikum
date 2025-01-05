from telegram.ext import (ApplicationBuilder,
                          MessageHandler, filters)

from config import TOKEN_ADMIN
from admin_bot.conversation import admin_conversation_handler
from admin_bot.utils import unknown_command

application = ApplicationBuilder().token(TOKEN_ADMIN).build()

application.add_handler(admin_conversation_handler)
application.add_handler(MessageHandler(filters.COMMAND, unknown_command))

application.run_polling()
