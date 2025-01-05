import math

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update
)
from telegram.ext import (CallbackQueryHandler, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

from config import GROUP_ID
from constants import (CONFIRM_CHANGE, CHOOSE_SELECTION_CRITERIA,
                       CHOOSING_LEVEL, CHOOSING_ROLE, CHOOSING_TEAM,
                       INPUT_NICKNAME, REGISTRATION, SEARCH_PEERS,
                       SHOWING_PEOPLE, BotMessage, ServiceConstant)
from crud.level import get_levels
from crud.role import get_roles_from_db
from crud.team import get_teams_from_db
from crud.user import (
    get_people_by_nickname,
    get_peers_by_role_and_level,
    get_people_by_team_name,
    get_person_details,
    get_user_by_telegram_id,
    set_user_invitation_status,
)
from handlers.registration_handler import registration_handler
from utils.keyboards import (
    get_back_to_filter_and_to_criteria_keyboard,
    get_back_to_nickname_and_to_criteria_keyboard,
    get_complete_auth_keyboard, get_confirmation_keyboard,
    get_create_paginated_keyboard, get_fields_keyboard,
    get_join_channel_keyboard, get_peer_keyboard,
    get_search_criteria_keyboard, get_user_agreement_keyboard)
from utils.user_card import create_user_card

PAGE_SIZE = ServiceConstant.PAGE_SIZE


async def change_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Предоставляет пользователю карточку с
    личными данными для внесения изменений.
    """
    user_telegram_id = update.effective_user.id

    if user := await get_user_by_telegram_id(user_telegram_id):
        context.user_data.clear()
        user = user.__dict__
        user.pop('_sa_instance_state', None)

        for key, value in user.items():
            context.user_data[key] = value
        context.user_data['profile_changes'] = True

        await update.effective_message.reply_text(
            text=create_user_card(context.user_data),
            reply_markup=get_confirmation_keyboard()
        )
        return CONFIRM_CHANGE


async def confirm_change(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    """
    Обрабатывает ответ пользователя на изменение
    личных данных при поиске пиров.
    """
    if update.callback_query:
        query = update.callback_query
        await query.answer()

        if query.data == 'confirm':
            return await choose_selection_criteria(update, context)

        elif query.data == 'edit':
            await update.effective_message.reply_text(
                BotMessage.SELECT_VALUE_TO_EDIT_MESSAGE,
                reply_markup=get_fields_keyboard()
            )
            return REGISTRATION
    else:
        await update.effective_message.reply_text(
            BotMessage.USE_BUTTONS_TO_SELECT_MESSAGE,
        )
        return CONFIRM_CHANGE


async def start_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветствует пользователя и предлагает продолжить."""
    await update.effective_message.reply_text(
        text=(BotMessage.WELCOMING_SEARCH_PEERS_MESSAGE),
        reply_markup=get_user_agreement_keyboard()
    )
    return CHOOSE_SELECTION_CRITERIA


async def choose_selection_criteria(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Проверяет членство в коммьюнити и предлагает выбрать критерии поиска."""
    query = update.callback_query
    await query.answer()

    user_telegram_id = update.effective_user.id
    user = await get_user_by_telegram_id(user_telegram_id)

    if not user:
        await query.edit_message_text(
            text=BotMessage.COMPLETE_AUTH_MESSAGE,
            reply_markup=get_complete_auth_keyboard()
        )
        return REGISTRATION

    try:
        member = await context.bot.get_chat_member(
            chat_id=GROUP_ID, user_id=user_telegram_id
        )
        if member.status not in ('member', 'administrator', 'creator'):
            link = await context.bot.create_chat_invite_link(
                chat_id=GROUP_ID,
                creates_join_request=True
            )
            await query.edit_message_text(
                text=(
                    BotMessage.join_to_community_message.format(
                        link=link.invite_link)
                ),
                reply_markup=get_join_channel_keyboard(),
                parse_mode='HTML'
            )
            await set_user_invitation_status(user)

            return CHOOSE_SELECTION_CRITERIA

    except Exception:
        await query.answer(
            text=(BotMessage.STATUS_CHECK_ERROR_MESSAGE),
            show_alert=True
        )
        return ConversationHandler.END

    await query.edit_message_text(
        text=(BotMessage.CHOOSE_SEARCH_CRITERIA_MESSAGE),
        reply_markup=get_search_criteria_keyboard()
    )
    return CHOOSE_SELECTION_CRITERIA


async def select_team(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    page=0
):
    """Демонстрирует список доступных команд с пагинацией."""
    teams = await get_teams_from_db()
    reply_markup = await get_create_paginated_keyboard(
        teams,
        page,
        'team',
        back_callback='back_to_criteria_selection'
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(
            BotMessage.CHOOSE_TEAM_MESSAGE, reply_markup=reply_markup
        )
    else:
        await update.effective_message.reply_text(
            BotMessage.CHOOSE_TEAM_MESSAGE,
            reply_markup=reply_markup
        )
    context.user_data['last_team_page'] = page

    return CHOOSING_TEAM


async def handle_team_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обрабатывает выбор пользователем нужной команды."""
    query = update.callback_query
    await query.answer()
    data = query.data

    team_name = data.split('_', 1)[1]
    context.user_data['last_team_name'] = team_name

    if people := await get_people_by_team_name(team_name):
        context.user_data['last_page'] = 0
        await show_peers_list(
            update, context, people, team_name=team_name, page=0
        )
        return SHOWING_PEOPLE

    reply_markup = get_back_to_filter_and_to_criteria_keyboard(
        'team'
    )
    await query.edit_message_text(
        text=(BotMessage.with_team_nobody_found_message.format(
            team_name=team_name)),
        reply_markup=reply_markup
    )
    return CHOOSING_TEAM


async def select_role(
    update: Update, context: ContextTypes.DEFAULT_TYPE, page=0
):
    """Демонстрирует список доступных ролей с пагинацией."""
    roles = await get_roles_from_db()

    reply_markup = await get_create_paginated_keyboard(
        roles,
        page,
        'role',
        back_callback='back_to_criteria_selection',
        page_prefix='role_'
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(
            BotMessage.LOOKING_FOR_WHO_MESSAGE, reply_markup=reply_markup
        )
    else:
        await update.effective_message.reply_text(
            BotMessage.LOOKING_FOR_WHO_MESSAGE, reply_markup=reply_markup
        )
    context.user_data['last_role_page'] = page

    return CHOOSING_ROLE


async def handle_role_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обрабатывает выбор пользователем нужной роли."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith('role_page_'):
        page = int(data.split('_')[-1])
        return await select_role(update, context, page=page)

    if data.startswith('role_'):
        selected_role = data.split('_', 1)[1]
        context.user_data['selected_role'] = selected_role
        return await select_level(update, context, selected_role=selected_role)

    await query.edit_message_text(BotMessage.INCORRECT_CHOOSE_MESSAGE)

    return CHOOSING_ROLE


async def select_level(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    selected_role,
    page=0
):
    """Демонстрирует список доступных уровней с пагинацией."""
    levels = await get_levels()
    levels.insert(0, 'Неважно')

    reply_markup = await get_create_paginated_keyboard(
        levels,
        page,
        callback_prefix=f'level_{selected_role}',
        back_callback='back_to_role_selection',
        page_prefix=f'level_{selected_role}_'
    )
    if update.callback_query:
        await update.callback_query.edit_message_text(
            BotMessage.role_what_level_message.format(
                selected_role=selected_role),
            reply_markup=reply_markup
        )
    else:
        await update.effective_message.reply_text(
            BotMessage.role_what_level_message.format(
                selected_role=selected_role),
            reply_markup=reply_markup
        )
    context.user_data['last_level_page'] = page

    return CHOOSING_LEVEL


async def handle_level_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith(
        f'level_{context.user_data.get("selected_role")}_page_'
    ):
        parts = data.split('_')
        page = int(parts[-1])
        selected_role = context.user_data.get("selected_role")

        return await select_level(
            update, context, selected_role=selected_role, page=page
        )
    if data.startswith('level_'):
        parts = data.split('_', 2)
        selected_level = parts[2]
        selected_role = parts[1]

        people = await get_peers_by_role_and_level(
            selected_role, selected_level
        )
        if people:
            context.user_data['selected_role'] = selected_role
            context.user_data['selected_level'] = selected_level
            await show_peers_list(
                update,
                context,
                people,
                role=selected_role,
                level=selected_level,
                page=0
            )
            return SHOWING_PEOPLE
        else:
            await query.edit_message_text(
                text=(
                    BotMessage.nobody_with_set_role_level_message.format(
                        selected_role=selected_role,
                        selected_level=selected_level)
                ),
                reply_markup=get_back_to_filter_and_to_criteria_keyboard(
                    'level'
                )
            )
            return CHOOSING_LEVEL
    else:
        await query.edit_message_text(BotMessage.INCORRECT_CHOOSE_MESSAGE)

        return CHOOSING_LEVEL


async def input_nickname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Предлагает пользователю ввести никнейм пира."""
    reply_markup = get_back_to_filter_and_to_criteria_keyboard()
    if update.callback_query:
        await update.callback_query.edit_message_text(
            BotMessage.ENTER_PEER_NICKNAME_MESSAGE, reply_markup=reply_markup
        )
    else:
        await update.effective_message.reply_text(
            BotMessage.ENTER_PEER_NICKNAME_MESSAGE, reply_markup=reply_markup
        )
    return INPUT_NICKNAME


async def handle_nickname_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обрабатывает введенный пользователем никнейм."""
    nickname = update.message.text.strip()
    context.user_data['last_nickname_input'] = nickname

    if people := await get_people_by_nickname(nickname):
        context.user_data['last_nickname'] = nickname
        context.user_data['last_page'] = 0

        await show_peers_list(
            update, context, people, nickname=nickname, page=0
        )
        return SHOWING_PEOPLE
    else:
        await update.message.reply_text(
            BotMessage.NO_NICKNAME_SEARCH_RESULTS_MESSAGE,
            reply_markup=get_back_to_nickname_and_to_criteria_keyboard()
        )
        return INPUT_NICKNAME


async def show_peers_list(
    update,
    context,
    people,
    role=None,
    level=None,
    team_name=None,
    nickname=None,
    page=0
):
    """Демонстриурет список подходящих пиров с пагинацией."""
    total_pages = math.ceil(len(people) / PAGE_SIZE)
    page = max(0, min(page, total_pages - 1))
    people_page = people[page * PAGE_SIZE: (page + 1) * PAGE_SIZE]
    keyboard = get_peer_keyboard(people_page)
    navigation_buttons = []

    if page > 0:
        if team_name:
            navigation_buttons.append(
                InlineKeyboardButton(
                    '← Назад',
                    callback_data=f'prev_team_{team_name}_{page - 1}'
                )
            )
        elif nickname:
            navigation_buttons.append(
                InlineKeyboardButton(
                    '← Назад',
                    callback_data=f'prev_nickname_{nickname}_{page - 1}'
                )
            )
        else:
            navigation_buttons.append(
                InlineKeyboardButton(
                    '← Назад',
                    callback_data=f'prev_{role}_{level}_{page - 1}'
                )
            )
    if page < total_pages - 1:
        if team_name:
            navigation_buttons.append(
                InlineKeyboardButton(
                    'Далее →',
                    callback_data=f'next_team_{team_name}_{page + 1}'
                )
            )
        elif nickname:
            navigation_buttons.append(
                InlineKeyboardButton(
                    'Далее →',
                    callback_data=f'next_nickname_{nickname}_{page + 1}'
                )
            )
        else:
            navigation_buttons.append(
                InlineKeyboardButton(
                    'Далее →',
                    callback_data=f'next_{role}_{level}_{page + 1}'
                )
            )
    if navigation_buttons:
        keyboard.append(navigation_buttons)
    if team_name:
        keyboard.append(
            [
                InlineKeyboardButton(
                    '← Назад к выбору команды',
                    callback_data='back_to_team_selection'
                )
            ]
        )
    elif nickname:
        keyboard.append(
            [
                InlineKeyboardButton(
                    '← Назад к поиску по никнейму',
                    callback_data='back_to_nickname_search'
                )
            ]
        )
    else:
        keyboard.append(
            [
                InlineKeyboardButton(
                    '← Назад к выбору уровня',
                    callback_data='back_to_level_selection'
                )
            ]
        )

    context.user_data['last_page'] = page
    context.user_data.pop('last_team_name', None)
    context.user_data.pop('last_role', None)
    context.user_data.pop('last_level', None)
    context.user_data.pop('last_nickname', None)

    if team_name:
        context.user_data['last_team_name'] = team_name
        message = BotMessage.peer_from_team_message.format(team_name=team_name)
    elif nickname:
        context.user_data['last_nickname'] = nickname
        message = BotMessage.peer_with_nickname_message.format(
            nickname=nickname)
    else:
        context.user_data['last_role'] = role
        context.user_data['last_level'] = level
        display_level = 'Любой' if level == 'Неважно' else level
        message = BotMessage.peers_with_role_level_message.format(
            role=role, display_level=display_level)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            message, reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.effective_message.reply_text(
            message, reply_markup=InlineKeyboardMarkup(keyboard)
        )


async def show_peer_detail(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обрабатывает нажатие на карточку пира и показывает ее."""
    query = update.callback_query
    await query.answer()

    parts = query.data.split('_', 1)
    telegram_nick = parts[1]

    keyboard = get_back_to_filter_and_to_criteria_keyboard(keyboard_return=True)

    if person := await get_person_details(telegram_nick):
        level = person.level if person.level else 'Не указано'
        role = person.role if person.role else 'Не указано'

        message_text = (
            f'Сберчат: {person.sberchat_nick or "Не указано"}\n'
            f'TG: @{person.telegram_nick or "Не указано"}\n'
            f'S21: {person.school21_nick or "Не указано"}\n'
            f'Роль: {level} {role}\n'
            f'Над чем работаю: {person.project or "Не указано"}'
        )
        keyboard.append(
            [
                InlineKeyboardButton(
                    '← Назад к списку',
                    callback_data='back_to_peers_list'
                )
            ]
        )
        await query.edit_message_text(
            text=message_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return SHOWING_PEOPLE
    else:
        await query.edit_message_text(BotMessage.NO_USER_INFO_MESSAGE)

        return SHOWING_PEOPLE


async def handle_pagination_buttons(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обрабатывает нажатия на кнопки пагинации."""
    query = update.callback_query
    await query.answer()

    data = query.data
    parts = data.split('_')

    if parts[1] == 'team':
        team_name = parts[2]
        page = int(parts[3])

        all_people = await get_people_by_team_name(team_name)

        await show_peers_list(
            update, context, all_people, team_name=team_name, page=page
        )
    elif parts[1] == 'nickname':
        nickname = parts[2]
        page = int(parts[3])

        all_people = await get_people_by_nickname(nickname)

        await show_peers_list(
            update, context, all_people, nickname=nickname, page=page
        )
    else:
        role = parts[1]
        level = parts[2]
        page = int(parts[3])

        all_people = await get_peers_by_role_and_level(role, level)

        await show_peers_list(
            update, context, all_people, role=role, level=level, page=page
        )
    return SHOWING_PEOPLE


async def back_to_peers_list(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обрабатывает возврат к списку всех найденных пиров из карточки."""
    query = update.callback_query
    await query.answer()

    page = context.user_data.get('last_page', 0)

    if 'last_team_name' in context.user_data:
        team_name = context.user_data.get('last_team_name')
        all_people = await get_people_by_team_name(team_name)

        await show_peers_list(
            update, context, all_people, team_name=team_name, page=page
        )
        return SHOWING_PEOPLE
    elif 'last_nickname' in context.user_data:
        nickname = context.user_data.get('last_nickname')
        all_people = await get_people_by_nickname(nickname)

        await show_peers_list(
            update, context, all_people, nickname=nickname, page=page
        )
        return SHOWING_PEOPLE
    elif 'last_role' in context.user_data and \
         'last_level' in context.user_data:

        role = context.user_data.get('last_role')
        level = context.user_data.get('last_level')

        all_people = await get_peers_by_role_and_level(role, level)

        await show_peers_list(
            update, context, all_people, role=role, level=level, page=page
        )
        return SHOWING_PEOPLE
    else:
        await query.edit_message_text(
            BotMessage.CANT_BACK_TO_LIST_MESSAGE
        )
        return ConversationHandler.END


async def back_to_search_filter_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Обрабатывает возврат к выбору поисковых фильтров."""
    query = update.callback_query
    await query.answer()

    data = query.data

    if 'role' in data:
        return await select_role(
            update,
            context,
            page=context.user_data.get('last_role_page', 0)
        )
    elif 'team' in data:
        return await select_team(
            update,
            context,
            page=context.user_data.get('last_team_page', 0)
        )
    elif 'level' in data:
        selected_role = context.user_data.get('selected_role')

        return await select_level(
            update,
            context,
            selected_role=selected_role,
            page=context.user_data.get('last_level_page', 0)
        )
    elif 'nickname' in data:
        return await input_nickname(update, context)
    elif 'criteria' in data:
        await choose_selection_criteria(update, context)

        return CHOOSE_SELECTION_CRITERIA
    else:
        await query.edit_message_text(
            BotMessage.CANT_BACK_TO_PREVIOUS_STEP_MESSAGE)

        return ConversationHandler.END


search_peers_handler = ConversationHandler(
    entry_points=[
        CommandHandler('start', start_message),
        CallbackQueryHandler(
            choose_selection_criteria, pattern='^continue_search$')
    ],
    states={
        CHOOSE_SELECTION_CRITERIA: [
            CallbackQueryHandler(
                choose_selection_criteria, pattern='^continue$'
            ),
            CallbackQueryHandler(
                select_team, pattern='^search_by_team_name$'
            ),
            CallbackQueryHandler(select_role, pattern='^search_by_role$'),
            CallbackQueryHandler(
                input_nickname, pattern='^search_by_nickname$'
            ),
        ],
        REGISTRATION: [registration_handler],
        CHOOSING_TEAM: [
            CallbackQueryHandler(
                handle_team_selection, pattern='^team_.*|^team_page_.*'
            ),
            CallbackQueryHandler(
                back_to_search_filter_selection,
                pattern='^back_to_team_selection$|^back_to_criteria_selection$'
            ),
        ],
        CHOOSING_ROLE: [
            CallbackQueryHandler(
                handle_role_selection, pattern='^role_.*|^role_page_.*'
            ),
            CallbackQueryHandler(
                back_to_search_filter_selection,
                pattern='^back_to_criteria_selection$'
            ),
        ],
        CHOOSING_LEVEL: [
            CallbackQueryHandler(
                handle_level_selection, pattern='^level_.*|^level_page_.*'
            ),
            CallbackQueryHandler(
                back_to_search_filter_selection,
                pattern='^back_to_role_selection$|^back_to_criteria_selection$'
            ),
            CallbackQueryHandler(
                back_to_search_filter_selection,
                pattern='^back_to_level_selection$'
            ),
        ],
        INPUT_NICKNAME: [
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_nickname_input
            ),
            CallbackQueryHandler(
                back_to_search_filter_selection,
                pattern='^back_to_criteria_selection$'
            ),
            CallbackQueryHandler(
                back_to_search_filter_selection,
                pattern='^back_to_nickname_search$'
            ),
        ],
        SHOWING_PEOPLE: [
            CallbackQueryHandler(
                show_peer_detail, pattern='^person_.*'
            ),
            CallbackQueryHandler(
                handle_pagination_buttons, pattern='^(prev|next)_.*'
            ),
            CallbackQueryHandler(
                back_to_peers_list,
                pattern='^back_to_peers_list$'
            ),
            CallbackQueryHandler(
                back_to_search_filter_selection, pattern='^back_to_.*$'
            ),
        ],
        SEARCH_PEERS: [CallbackQueryHandler(start_message, '^search_peers$')],
        CONFIRM_CHANGE: [
            CallbackQueryHandler(confirm_change, '^(confirm|edit)$'),
            MessageHandler(filters.TEXT & ~filters.COMMAND, confirm_change)
        ],
    },
    fallbacks=[CommandHandler('change_profile', change_profile)],
    allow_reentry=True
)
