import math

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import GROUP_ID
from crud.level import get_levels
from constants import ButtonText, ServiceConstant


async def get_level_keyboard():
    """Выводит клавиатуру с уровнями квалификации из базы данных."""
    levels = await get_levels()
    keyboard = [
        [InlineKeyboardButton(level.capitalize(), callback_data=level)]
        for level in levels]
    return InlineKeyboardMarkup(keyboard)


def get_skip_keyboard():
    """Выводит клавиатуру с кнопкой 'Пропустить'."""
    keyboard = [
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_SKIP, callback_data='skip_job')
        ]]
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard():
    """Выводит клавиатуру с кнопками 'Подтвердить' и 'Изменить'."""
    keyboard = [
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_CONFIRM, callback_data='confirm'),
            InlineKeyboardButton(
                ButtonText.BUTTON_EDIT, callback_data='edit'),
        ]]
    return InlineKeyboardMarkup(keyboard)


def get_fields_keyboard():
    """Выводит клавиатуру с данными пользователя из его карточки."""
    keyboard = [
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_NICKNAME_21, callback_data='Ник в Школе 21')
        ],
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_NAME_SBERCHAT,
                callback_data='Имя в Сберчате',)
        ],
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_NICKNAME_TELEGRAM,
                callback_data='Ник в Telegram',)
        ],
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_TEAM_NAME, callback_data='Название команды')
        ],
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_YOUR_ROLE, callback_data='Ваша роль')
        ],
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_YOUR_LEVEL, callback_data='Ваш уровень')
        ],
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_WORKING_ON,
                callback_data='Над чем вы работаете',)
        ]]
    return InlineKeyboardMarkup(keyboard)


def get_user_agreement_keyboard():
    """Выводит клавиатуру с кнопкой 'Продолжить'."""
    keyboard = [
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_CONTINUE, callback_data='continue')
        ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_continue_search_peers_keyboard():
    """Выводит клавиатуру с кнопкой 'Продолжить' для перехода к поиску пиров."""
    keyboard = [
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_CONTINUE, callback_data='continue_search')
        ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_join_channel_keyboard():
    """Выводит клавиатуру с кнопкой 'Я присоединился'."""
    keyboard = [
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_CONFIRM_JOIN, callback_data='continue')
        ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_final_keyboard(context):
    """Выводит клавиатуру с кнопками 'Присоединиться к коммьюинити' и 'Поиск пиров'."""
    link = await context.bot.create_chat_invite_link(
        chat_id=GROUP_ID, creates_join_request=True
    )
    keyboard = [
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_JOIN_COMMUNITY, url=link.invite_link)
        ],
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_SEARCH_PEERS, callback_data='search_peers')
        ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_complete_auth_keyboard():
    """Выводит клавиатуру с кнопкой 'Пройти аутентификацию'."""
    keyboard = [
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_AUTHENTICATE, callback_data='authenticate')
        ]]
    return InlineKeyboardMarkup(keyboard)


def get_change_level_search_filters():
    """Выводит клавиатуру с кнопкой 'Назад к выбору роли'."""
    keyboard = [
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_BACK_TO_ROLE_SELECTION,
                callback_data='retry_role')
        ]]
    return InlineKeyboardMarkup(keyboard)


def get_people_paginated_list():
    """Выводит клавиатуру с кнопкой 'Назад к списку'."""
    keyboard = [
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_BACK_TO_LIST,
                callback_data='back_to_people_list')
        ]]
    return InlineKeyboardMarkup(keyboard)


def get_show_telegram_nickname_keyboard():
    """Выводит клавиатуру с кнопкой 'Показать ник в ТГ участникам сообщества'."""
    keyboard = [[
        InlineKeyboardButton(
            ButtonText.BUTTON_SHOW_TG_NICKNAME,
            callback_data='show_my_tg_nickname')
    ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_search_criteria_keyboard():
    """Выводит клавиатуру с выбором критериев поиска пиров."""
    keyboard = [
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_SEARCH_BY_ROLE,
                callback_data='search_by_role')
        ],
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_SEARCH_BY_TEAM_NAME,
                callback_data='search_by_team_name')
        ],
        [
            InlineKeyboardButton(
                ButtonText.BUTTON_SEARCH_BY_NICKNAME,
                callback_data='search_by_nickname')
        ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_back_to_filter_and_to_criteria_keyboard(
        search_filter=None, keyboard=None, keyboard_return=False
):
    """Выводит клавиатуру с кнопками для возврата к фильтрам или критериям поиска."""
    if not keyboard:
        keyboard = [
            [InlineKeyboardButton(
                'Назад к критериям поиска',
                callback_data='back_to_criteria_selection')]]

    if search_filter:
        keyboard.insert(0, [InlineKeyboardButton(
            '← Назад к выбору',
            callback_data=f'back_to_{search_filter}_selection')])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    if keyboard_return is False:
        keyboard.append([InlineKeyboardButton(
            '← Назад к критериям поиска',
            callback_data='back_to_criteria_selection')])

    if keyboard_return is True:
        return keyboard

    if keyboard_return is False:

        return InlineKeyboardMarkup(inline_keyboard=keyboard)


async def get_create_paginated_keyboard(
    items,
    page,
    callback_prefix,
    item_per_page=ServiceConstant.PAGE_SIZE,
    back_callback=None,
    page_prefix=''
):
    """Выводит клавиатуру с кнопками для элементов списка и навигацией."""
    total_pages = math.ceil(len(items) / item_per_page)
    page = max(0, min(page, total_pages - 1))
    items_page = items[page * item_per_page: (page + 1) * item_per_page]

    keyboard = [
        [InlineKeyboardButton(item, callback_data=f'{callback_prefix}_{item}')]
        for item in items_page]

    navigation_buttons = []
    if page > 0:
        navigation_buttons.append(
            InlineKeyboardButton(
                '← Назад', callback_data=f'{page_prefix}page_{page - 1}'
            ))
    if page < total_pages - 1:
        navigation_buttons.append(
            InlineKeyboardButton(
                'Далее →', callback_data=f'{page_prefix}page_{page + 1}'
            ))
    if navigation_buttons:
        keyboard.append(navigation_buttons)

    if back_callback:
        keyboard.append(
            [
                InlineKeyboardButton(
                    '← Назад к критериям поиска', callback_data=back_callback)
            ])

    return InlineKeyboardMarkup(keyboard)


def get_peer_keyboard(people_page):
    """Выводит клавиатуру с пирами, удовлетворяющими критериям поиска."""
    keyboard = [
        [
            InlineKeyboardButton(
                f'{person.sberchat_nick or person.telegram_nick or person.school21_nick} — {person.team}',
                callback_data=f'person_{person.telegram_nick}')
        ] for person in people_page]

    return keyboard


def get_back_to_nickname_and_to_criteria_keyboard():
    """Выводит клавиатуру с кнопками для элементов списка и навигацией."""
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    '← Назад к поиску по никнейму',
                    callback_data='back_to_nickname_search'
                )],
            [
                InlineKeyboardButton(
                    '← Назад к критериям поиска',
                    callback_data='back_to_criteria_selection')
            ]])
