import logging
from logging.handlers import TimedRotatingFileHandler

from telegram.ext import ApplicationBuilder, ChatJoinRequestHandler

from config import TOKEN
from handlers.approve_request_handler import approve_request
from handlers.registration_handler import registration_handler
from handlers.search_peers_handler import search_peers_handler

logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        TimedRotatingFileHandler(
            "app.log",
            when="midnight",
            interval=1,
            backupCount=10
        ),
    ]
)

logger = logging.getLogger(__name__)

application = ApplicationBuilder().token(TOKEN).build()

application.add_handler(search_peers_handler)
application.add_handler(registration_handler)
application.add_handler(ChatJoinRequestHandler(approve_request))

application.run_polling(
    allowed_updates=['chat_join_request', 'message', 'callback_query']
)
