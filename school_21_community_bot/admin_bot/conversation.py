from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from admin_bot.constants import (
    ADMIN_MENU,
    LEVEL_ADD,
    LEVEL_DELETE_CONFIRM,
    LEVEL_DETAIL,
    LEVEL_LIST,
    LEVEL_VIEW_USERS,
    MAIN_ADMIN_MENU,
    ROLE_ADD,
    ROLE_DELETE_CONFIRM,
    ROLE_DETAIL,
    ROLE_LIST,
    ROLE_VIEW_USERS,
    SEARCH_ALPHABET,
    SEARCH_MENU,
    SEARCH_NICKNAME,
    SEARCH_ROLE,
    SEARCH_TEAM,
    USER_ADD_FULL_NAME,
    USER_ADD_LEVEL_INPUT,
    USER_ADD_PROJECT,
    USER_ADD_ROLE_INPUT,
    USER_ADD_SBERCHAT_NICK,
    USER_ADD_SCHOOL21_NICK,
    USER_ADD_TEAM,
    USER_ADD_TELEGRAM_ID,
    USER_ADD_TELEGRAM_NICK,
    USER_DELETE_CONFIRM,
    USER_DETAIL,
    USER_EDIT_FIELD,
    USER_EDIT_LEVEL_INPUT,
    USER_EDIT_ROLE_INPUT,
    USER_EDIT_VALUE,
    USER_LIST,
    USER_MENU,
)
from admin_bot.level import (
    level_add_handler,
    level_delete_confirm_handler,
    level_detail_handler,
    level_list_handler,
    view_users_by_level,
)
from admin_bot.menu import (
    admin_menu_handler,
    start_admin,
    user_menu_handler,
)
from admin_bot.role import (
    role_add_handler,
    role_delete_confirm_handler,
    role_detail_handler,
    role_list_handler,
    view_users_by_role,
)
from admin_bot.search import (
    search_alphabet_handler,
    search_menu_handler,
    search_nickname_handler,
    search_role_handler,
    search_team_handler,
)
from admin_bot.user import (
    user_add_full_name,
    user_add_level_input,
    user_add_project,
    user_add_role_input,
    user_add_sberchat_nick,
    user_add_school21_nick,
    user_add_team,
    user_add_telegram_id,
    user_add_telegram_nick,
    user_delete_confirm_handler,
    user_detail_handler,
    user_edit_field_handler,
    user_edit_level_input,
    user_edit_role_input,
    user_edit_value_handler,
    user_list_handler,
)
from admin_bot.utils import unknown_command

admin_conversation_handler = ConversationHandler(
    entry_points=[
        CommandHandler("start", start_admin),
        MessageHandler(
            filters.TEXT & filters.Regex("^🍔 Меню$"),
            admin_menu_handler,
        ),
    ],
    states={
        ADMIN_MENU: [CallbackQueryHandler(admin_menu_handler)],
        MAIN_ADMIN_MENU: [CallbackQueryHandler(admin_menu_handler)],
        USER_MENU: [CallbackQueryHandler(user_menu_handler)],
        USER_LIST: [CallbackQueryHandler(user_list_handler)],
        USER_DETAIL: [CallbackQueryHandler(user_detail_handler)],
        USER_ADD_FULL_NAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, user_add_full_name
            )
        ],
        USER_ADD_TELEGRAM_ID: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, user_add_telegram_id
            )
        ],
        USER_ADD_TELEGRAM_NICK: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, user_add_telegram_nick
            )
        ],
        USER_ADD_SBERCHAT_NICK: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, user_add_sberchat_nick
            )
        ],
        USER_ADD_SCHOOL21_NICK: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, user_add_school21_nick
            )
        ],
        USER_ADD_TEAM: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, user_add_team)
        ],
        USER_ADD_ROLE_INPUT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, user_add_role_input
            )
        ],
        USER_ADD_LEVEL_INPUT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, user_add_level_input
            )
        ],
        USER_ADD_PROJECT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, user_add_project)
        ],

        USER_EDIT_FIELD: [
            CallbackQueryHandler(user_edit_field_handler)
        ],
        USER_EDIT_ROLE_INPUT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, user_edit_role_input
            )
        ],
        USER_EDIT_LEVEL_INPUT: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, user_edit_level_input
            )
        ],
        USER_EDIT_VALUE: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, user_edit_value_handler
            )
        ],
        USER_DELETE_CONFIRM: [
            CallbackQueryHandler(user_delete_confirm_handler)
        ],

        ROLE_LIST: [CallbackQueryHandler(role_list_handler)],
        ROLE_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                  role_add_handler)],
        ROLE_DETAIL: [CallbackQueryHandler(role_detail_handler)],
        ROLE_DELETE_CONFIRM: [
            CallbackQueryHandler(role_delete_confirm_handler)
        ],
        ROLE_VIEW_USERS: [
            CallbackQueryHandler(view_users_by_role)
        ],

        LEVEL_LIST: [CallbackQueryHandler(level_list_handler)],
        LEVEL_ADD: [MessageHandler(filters.TEXT & ~filters.COMMAND,
                                   level_add_handler)],
        LEVEL_DETAIL: [CallbackQueryHandler(level_detail_handler)],
        LEVEL_DELETE_CONFIRM: [
            CallbackQueryHandler(level_delete_confirm_handler)
        ],
        LEVEL_VIEW_USERS: [
            CallbackQueryHandler(view_users_by_level)
        ],

        SEARCH_MENU: [CallbackQueryHandler(search_menu_handler)],
        SEARCH_NICKNAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, search_nickname_handler
            )
        ],
        SEARCH_TEAM: [
            MessageHandler(filters.TEXT & ~filters.COMMAND,
                           search_team_handler)
        ],
        SEARCH_ROLE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND,
                           search_role_handler)
        ],
        SEARCH_ALPHABET: [
            CallbackQueryHandler(search_alphabet_handler)
        ],
    },
    fallbacks=[MessageHandler(filters.ALL, unknown_command)],
    allow_reentry=True,
)
