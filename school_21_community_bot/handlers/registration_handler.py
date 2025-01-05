from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from constants import (
    CONFIRMATION_RESPONSE,
    CORRECTION,
    FIELDS_FOR_CORRECTION,
    FINAL_STATE,
    PROJECT,
    USER_LEVEL,
    SBER_CHAT_NAME,
    SCHOOL_21_NICKNAME,
    SEARCH_PEERS,
    TEAM,
    TEAM_ROLE,
    TELEGRAM_NICKNAME,
    UPDATE_CORRECTED_FIELD,
    UPDATE_CORRECTED_LEVEL,
    BotMessage,
    MetricMessage
)
from crud.level import get_levels
from crud.user import (
    create_or_update_user,
    get_user_by_school21_nick,
    set_user_invitation_status
)
from service.metric import log_metric
from utils.keyboards import (
    get_confirmation_keyboard,
    get_fields_keyboard,
    get_final_keyboard,
    get_level_keyboard,
    get_show_telegram_nickname_keyboard,
    get_skip_keyboard,
    get_user_agreement_keyboard,
    get_continue_search_peers_keyboard
)
from utils.user_card import create_user_card
from utils.validators import (
    validate_nickname_sber,
    validate_nickname_school21,
    validate_nickname_telegram,
    validate_project_description,
    validate_role_name,
    validate_team_name,
)


async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение и запрашивает никнейм в Школе 21."""
    context.user_data.clear()
    context.user_data['telegram_id'] = update.effective_user.id
    await update.effective_message.reply_text(
        text=BotMessage.WELCOMING_REGISTRATION_MESSAGE
    )
    await update.effective_message.reply_text(
        text=BotMessage.SCHOOL_21_NICKNAME_MESSAGE
    )
    await log_metric(
        update.effective_user.id,
        MetricMessage.REGISTRATION_STARTED
    )
    return SCHOOL_21_NICKNAME


async def school_21_nickname(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Проверяет переданный никнейм пользователя в Школе 21 на валидность и
    уникальность, затем запрашивает имя пользователя в СберЧате.
    """
    school21_nick = update.message.text.strip()
    is_valid, error_message = validate_nickname_school21(school21_nick)

    if not is_valid:
        await update.message.reply_text(error_message)
        await log_metric(
            update.effective_user.id,
            MetricMessage.SCHOOL_21_NICKNAME_INVALID,
            error_message
        )
        return SCHOOL_21_NICKNAME

    existing_user = await get_user_by_school21_nick(school21_nick)
    if existing_user:
        error_unique = BotMessage.SCHOOL_21_NICKNAME_USED_MESSAGE
        await update.message.reply_text(error_unique)
        await log_metric(
            update.effective_user.id,
            MetricMessage.SCHOOL_21_NICKNAME_NOT_UNIQUE,
            school21_nick
        )
        return SCHOOL_21_NICKNAME

    context.user_data['school21_nick'] = school21_nick
    await log_metric(
        update.effective_user.id,
        MetricMessage.SCHOOL_21_NICKNAME_ENTERED,
        school21_nick
    )
    await update.message.reply_text(text=BotMessage.SBER_CHAT_NAME_MESSAGE)
    return SBER_CHAT_NAME


async def sberchat_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получает имя пользователя в СберЧате и запрашивает
    никнейм пользователя в Телеграме.
    """
    sber_chat_name = update.message.text.strip()
    is_valid, error_message = validate_nickname_sber(sber_chat_name)

    if is_valid:
        context.user_data['sberchat_nick'] = sber_chat_name
        await log_metric(
            update.effective_user.id,
            MetricMessage.SBERCHAT_NICKNAME_ENTERED,
            sber_chat_name
        )
        await update.message.reply_text(
            BotMessage.TELEGRAM_NICKNAME_MESSAGE,
            reply_markup=get_show_telegram_nickname_keyboard(),
        )
        return TELEGRAM_NICKNAME

    await update.message.reply_text(error_message)
    await log_metric(
        update.effective_user.id,
        MetricMessage.SBERCHAT_NICKNAME_INVALID,
        error_message
    )
    return SBER_CHAT_NAME


async def telegram_nickname(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """
    Получает никнейм пользователя в Телеграме
    и запрашивает название команды.
    """
    if update.callback_query:
        await update.callback_query.answer()
        tg_nickname = update.effective_user.username
        if not tg_nickname:
            await update.effective_message.reply_text(
                text=BotMessage.TELEGRAM_NICKNAME_NOT_SET_MESSAGE
            )
            return TELEGRAM_NICKNAME
    else:
        tg_nickname = update.message.text.strip()
        is_valid, error_message = validate_nickname_telegram(tg_nickname)
        if not is_valid:
            await update.effective_message.reply_text(text=error_message)
            await log_metric(
                update.effective_user.id,
                MetricMessage.TELEGRAM_NICKNAME_INVALID,
                error_message
            )
            return TELEGRAM_NICKNAME

    context.user_data['telegram_nick'] = tg_nickname
    await log_metric(
        update.effective_user.id,
        MetricMessage.TELEGRAM_NICKNAME_ENTERED,
        tg_nickname
    )
    await update.effective_message.reply_text(
        text=BotMessage.TEAM_NAME_MESSAGE
    )

    return TEAM


async def team_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает название команды и запрашивает роль пользователя в команде."""
    team = update.message.text.strip()
    is_valid, error_message = validate_team_name(team)

    if is_valid:
        context.user_data['team'] = team

        await log_metric(
            update.effective_user.id,
            MetricMessage.TEAM_NAME_ENTERED,
            team
        )
        await update.message.reply_text(text=BotMessage.USER_ROLE_MESSAGE)
        return TEAM_ROLE

    await update.message.reply_text(error_message)
    await log_metric(
        update.effective_user.id,
        MetricMessage.TEAM_NAME_INVALID,
        error_message
    )
    return TEAM


async def user_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает роль пользователя в команде и запрашивает уровень роли."""
    team_role = update.message.text.strip()
    is_valid, error_message = validate_role_name(team_role)

    if is_valid:
        context.user_data['role'] = team_role

        await log_metric(
            update.effective_user.id,
            MetricMessage.USER_ROLE_ENTERED,
            team_role
        )
        await update.effective_message.reply_text(
            BotMessage.ROLE_LEVEL_MESSAGE,
            reply_markup=await get_level_keyboard()
        )
        return USER_LEVEL

    await update.message.reply_text(error_message)
    await log_metric(
        update.effective_user.id,
        MetricMessage.USER_ROLE_INVALID,
        error_message
    )
    return TEAM_ROLE


async def user_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получает уровень пользователя и запрашивает
    над чем работает пользователь.
    """
    if update.callback_query:
        await update.callback_query.answer()
        level_name = update.callback_query.data
        context.user_data['level'] = level_name
        await log_metric(
            update.effective_user.id,
            MetricMessage.ROLE_LEVEL_ENTERED,
            level_name
        )
        await update.effective_message.reply_text(
            BotMessage.JOB_MESSAGE,
            reply_markup=get_skip_keyboard(),
        )
        return PROJECT

    await update.effective_message.reply_text(
        MetricMessage.ROLE_LEVEL_INVALID
    )
    return USER_LEVEL


async def project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Получает информацию о том, над чем работает пользователь."""
    if update.callback_query:
        await update.callback_query.answer()
        context.user_data['project'] = 'Не указано'
        await log_metric(
            update.effective_user.id,
            MetricMessage.PROJECT_NOT_SPECIFIED
        )
        return await confirmation(update, context)

    user_project = update.message.text.strip()
    is_valid, error_message = validate_project_description(user_project)

    if is_valid:
        context.user_data['project'] = user_project
        await log_metric(
            update.effective_user.id,
            MetricMessage.PROJECT_ENTERED,
            user_project
        )
        return await confirmation(update, context)

    await update.message.reply_text(error_message)
    await log_metric(
        update.effective_user.id,
        MetricMessage.PROJECT_INVALID,
        error_message
    )
    return PROJECT


async def confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Запрашивает подтверждение введенных данных
    перед завершением регистрации.
    """
    await update.effective_message.reply_text(
        text=create_user_card(context.user_data),
        reply_markup=get_confirmation_keyboard()
    )
    return CONFIRMATION_RESPONSE


async def confirmation_response(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """Обрабатывает ответ пользователя на подтверждение данных."""
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == 'confirm':
            if context.user_data.get('profile_changes', None):
                await update.effective_message.reply_text(
                    BotMessage.DATA_WAS_SAVED_MESSAGE,
                    reply_markup=get_continue_search_peers_keyboard()
                )
                context.user_data.pop('profile_changes', None)
                await create_or_update_user(context.user_data)
                context.user_data.clear()
                return SEARCH_PEERS
            await update.effective_message.reply_text(
                BotMessage.AGREEMENT_MESSAGE,
                reply_markup=get_user_agreement_keyboard()
            )
            return FINAL_STATE

        elif query.data == 'edit':
            await update.effective_message.reply_text(
                BotMessage.SELECT_VALUE_TO_EDIT_MESSAGE,
                reply_markup=get_fields_keyboard()
            )
            return CORRECTION
    else:
        await update.effective_message.reply_text(
            BotMessage.USE_BUTTONS_TO_SELECT_MESSAGE,
        )
        return CONFIRMATION_RESPONSE


async def correction(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор поля для редактирования."""
    if query := update.callback_query:
        await query.answer()
        field_name = update.callback_query.data
    else:
        await update.effective_message.reply_text(
            BotMessage.USE_BUTTONS_TO_SELECT_MESSAGE)
        return CORRECTION

    field_value = FIELDS_FOR_CORRECTION.get(field_name)

    if not field_value:
        await update.effective_message.reply_text(
            BotMessage.INVALID_VALUE_TO_EDIT_SELECTED_MESSAGE,
            reply_markup=get_fields_keyboard()
        )
        return CORRECTION

    context.user_data['field_for_edit'] = field_value

    if field_value != 'level':
        current_value = context.user_data.get(field_value)
        await update.effective_message.reply_text(
            BotMessage.current_value_of_field_message.format(
                field_name=field_name, current_value=current_value)
        )
        return UPDATE_CORRECTED_FIELD
    await update.effective_message.reply_text(
        BotMessage.ROLE_LEVEL_MESSAGE,
        reply_markup=await get_level_keyboard()
    )
    return UPDATE_CORRECTED_LEVEL


async def update_corrected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обновляет исправленное значение и возвращается к подтверждению."""
    field_for_edit = context.user_data.get('field_for_edit')
    if not field_for_edit:
        await update.effective_message.reply_text(
            BotMessage.WHILE_UPDATE_ERROR_OCCURED_MESSAGE,
            reply_markup=get_fields_keyboard())
        return CORRECTION

    if field_for_edit == 'level':
        if update.callback_query:
            await update.callback_query.answer()
            level_name = update.callback_query.data
            level_names = await get_levels()
            if level_name in level_names:
                context.user_data['level'] = level_name
                await log_metric(
                    update.effective_user.id,
                    MetricMessage.LEVEL_UPDATED,
                    level_name
                )
                return await confirmation(update, context)
            else:
                await update.effective_message.reply_text(
                    BotMessage.ROLE_LEVEL_MESSAGE,
                    reply_markup=await get_level_keyboard()
                )
                return UPDATE_CORRECTED_LEVEL
        else:
            await update.effective_message.reply_text(
                BotMessage.USE_BUTTONS_TO_SELECT_MESSAGE,
                reply_markup=await get_level_keyboard()
            )
            return UPDATE_CORRECTED_LEVEL
    else:
        value_for_update = update.message.text.strip()
        validator = {
            'school21_nick': validate_nickname_school21,
            'sberchat_nick': validate_nickname_sber,
            'telegram_nick': validate_nickname_telegram,
            'team': validate_team_name,
            'role': validate_role_name,
            'project': validate_project_description,
        }.get(field_for_edit)
        if not validator:
            await update.effective_message.reply_text(
                BotMessage.INVALID_VALUE_TO_EDIT_SELECTED_MESSAGE,
                reply_markup=get_fields_keyboard()
            )
            return CORRECTION

        is_valid, error_message = validator(value_for_update)

        if is_valid:
            context.user_data[field_for_edit] = value_for_update
            await log_metric(
                update.effective_user.id,
                MetricMessage.field_updated.format(
                    field_for_edit=field_for_edit),
                value_for_update
            )
            return await confirmation(update, context)
        await update.effective_message.reply_text(error_message)
        return UPDATE_CORRECTED_FIELD


async def final_state(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Сохраняет в базу данных введенные пользователем данные и
    предлагает подписаться на канал или перейти к поиску пиров.
    """
    context.user_data.pop('field_for_edit', None)
    user = await create_or_update_user(context.user_data)
    if user:
        await update.effective_message.reply_text(
            text=BotMessage.CONGRATS_MESSAGE,
            reply_markup=await get_final_keyboard(context)
        )
        await set_user_invitation_status(user)
        return SEARCH_PEERS
    await update.effective_message.reply_text(
        text=BotMessage.DATA_NOT_SAVED_MESSAGE,
        reply_markup=get_confirmation_keyboard()
    )
    return CONFIRMATION_RESPONSE


registration_handler = ConversationHandler(
    entry_points=[
        CallbackQueryHandler(start_message, pattern='^authenticate$'),
        CallbackQueryHandler(
            correction,
            pattern=('^(Ник в Школе 21|Имя в Сберчате|Ник в Telegram|'
                     'Название команды|Ваша роль|Ваш уровень|'
                     'Над чем вы работаете)$'))
    ],
    states={
        SCHOOL_21_NICKNAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, school_21_nickname)
        ],
        SBER_CHAT_NAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, sberchat_name)
        ],
        TELEGRAM_NICKNAME: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, telegram_nickname),
            CallbackQueryHandler(
                telegram_nickname, pattern='^show_my_tg_nickname$')
        ],
        TEAM: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, team_name)
        ],
        TEAM_ROLE: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, user_role)
        ],
        USER_LEVEL: [
            CallbackQueryHandler(user_level, pattern='^.+$'),
            MessageHandler(filters.TEXT & ~filters.COMMAND, user_level),
        ],
        PROJECT: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, project),
            CallbackQueryHandler(project, pattern='^skip_job$')
        ],
        CONFIRMATION_RESPONSE: [
            CallbackQueryHandler(
                confirmation_response, pattern='^(confirm|edit)$'),
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, confirmation_response)
        ],
        CORRECTION: [
            CallbackQueryHandler(
                correction,
                pattern=('^(Ник в Школе 21|Имя в Сберчате|Ник в Telegram|'
                         'Название команды|Ваша роль|Ваш уровень|'
                         'Над чем вы работаете)$')),
            MessageHandler(filters.TEXT & ~filters.COMMAND, correction)
        ],
        UPDATE_CORRECTED_FIELD: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, update_corrected)
        ],
        UPDATE_CORRECTED_LEVEL: [
            CallbackQueryHandler(
                update_corrected, pattern='^.+$'),
            MessageHandler(filters.TEXT & ~filters.COMMAND, update_corrected)
        ],
        FINAL_STATE: [
            CallbackQueryHandler(final_state, pattern='^continue$')
        ],
    },
    fallbacks=[],
    map_to_parent={
        SEARCH_PEERS: SEARCH_PEERS
    },
    allow_reentry=True
)
