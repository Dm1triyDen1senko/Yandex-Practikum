import os

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
DATABASE_URL = os.getenv('DATABASE_URL')
INVITE_LINK = os.getenv('INVITE_LINK')
GROUP_ID = os.getenv('GROUP_ID')
ADMIN_USER_IDS = os.getenv('ADMIN_USER_IDS', '').split(',')
ADMIN_USER_IDS = [int(
    user_id.strip()
) for user_id in ADMIN_USER_IDS if user_id.strip().isdigit()]
TOKEN_ADMIN = os.getenv('TOKEN_ADMIN')
