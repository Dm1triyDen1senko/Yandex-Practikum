(
    SCHOOL_21_NICKNAME,
    SBER_CHAT_NAME,
    TELEGRAM_NICKNAME,
    TEAM,
    TEAM_ROLE,
    USER_LEVEL,
    PROJECT,
    CONFIRMATION,
    CONFIRMATION_RESPONSE,
    CORRECTION,
    UPDATE_CORRECTED_FIELD,
    UPDATE_CORRECTED_LEVEL,
    FINAL_STATE,
    SEARCH_PEERS
) = range(14)

(
    CHOOSING_ROLE,
    REGISTRATION,
    CHOOSING_LEVEL,
    CHOOSING_TEAM,
    SHOWING_PEOPLE,
    CHOOSE_SELECTION_CRITERIA,
    INPUT_NICKNAME,
    CONFIRM_CHANGE
) = range(8)

FIELDS_FOR_CORRECTION = {
    'Ник в Школе 21': 'school21_nick',
    'Имя в Сберчате': 'sberchat_nick',
    'Ник в Telegram': 'telegram_nick',
    'Название команды': 'team',
    'Ваша роль': 'role',
    'Ваш уровень': 'level',
    'Над чем вы работаете': 'project',
}


class BotMessage:
    WELCOMING_REGISTRATION_MESSAGE = (
        'Привет! Пройди аутентификацию, чтобы присоединиться '
        'к сообществу Школы 21 внутри СБЕРа. После '
        'аутентификации ты получишь доступ к чату и '
        'информации о том, где работают пиры в СБЕРе.'
    )
    WELCOMING_SEARCH_PEERS_MESSAGE = (
        'Привет! Я бот по поиску пиров в Сбере. '
        'Для начала работы тебе нужно предоставить свои персональные данные '
        'для отображения в базе пиров и '
        'быть подписанным на канал комьюнити.'
    )
    SCHOOL_21_NICKNAME_MESSAGE = (
        'Укажи свой ник в Школе 21 (даже если ты уже '
        'не учишься). Это подтвердит, что ты наш '
        'студент и можешь присоединиться к '
        'сообществу.'
    )
    SBER_CHAT_NAME_MESSAGE = (
        'Укажи имя пользователя в СберЧате - это часть '
        'твоего адреса электронной почты до знака \'@\'. '
        'Например, для почты ivanov@sberbank.ru имя '
        'будет ivanov.'
    )
    TELEGRAM_NICKNAME_MESSAGE = (
        'Укажи свой ник в Telegram, чтобы другие '
        'пиры могли легко тебя найти. Это способ '
        'наладить полезные связи и быстрее '
        'решать вопросы вместе!'
    )
    TELEGRAM_NICKNAME_NOT_SET_MESSAGE = (
        'Похоже, у тебя не задан никнейм в Telegram. '
        'Пожалуйста, введи его вручную.'
    )
    TEAM_NAME_MESSAGE = (
        'Укажи команду. '
        'Например: Lab.SberPay.NFC или Lab.ПлатежныйСчет.Продукт.'
    )
    USER_ROLE_MESSAGE = (
        'Роль в команде. '
        'Пожалуйста, введи роль строго как в Пульсе, без указания уровня '
        'квалификации. Например: Senior golang разработчик или '
        'Владелец продукта.'
    )
    ROLE_LEVEL_MESSAGE = (
        'Выберите ваш уровень квалификации из предложенных вариантов.'
    )
    JOB_MESSAGE = (
        'Над чем ты работаешь? Коротко опиши свой вклад в '
        'продукт, чтобы участники сообщества знали какой ты '
        'крутой!'
    )
    AGREEMENT_MESSAGE = (
        'Нажимая на кнопку ниже, ты соглашаешься с передачей и хранением '
        'введенных данных.'
    )
    SELECT_VALUE_TO_EDIT_MESSAGE = (
        'Выберите значение, которое хотите изменить.'
    )
    USE_BUTTONS_TO_SELECT_MESSAGE = (
        'Пожалуйста, используйте кнопки для выбора.'
    )
    INVALID_VALUE_TO_EDIT_SELECTED_MESSAGE = (
        'Неизвестное значение для редактирования. '
        'Пожалуйста, выберите значение из приведенного списка.'
    )
    CONGRATS_MESSAGE = (
        'Добро пожаловать в наше сообщество!\n\n'
        'Заходи в чат по кнопке "Присоединиться к комьюнити". '
        'После этого тебе станет доступен поиск пиров.'
    )
    COMPLETE_AUTH_MESSAGE = (
        'Кажется, ты не состоишь в сообществе, пожалуйста, '
        'пройди аутентификацию.'
    )
    WHILE_UPDATE_ERROR_OCCURED_MESSAGE = (
        'Произошла ошибка. Пожалуйста, попробуйте снова.'
    )
    STATUS_CHECK_ERROR_MESSAGE = (
        'Произошла ошибка при проверке вашего статуса. '
        'Пожалуйста, попробуйте позже.'
    )
    SCHOOL_21_NICKNAME_USED_MESSAGE = (
        'Этот никнейм уже используется в Школе 21. '
        'Пожалуйста, введите другой никнейм.'
    )
    DATA_NOT_SAVED_MESSAGE = (
        'Произошла ошибка при сохранении данных. '
        'Пожалуйста, попробуйте подтвердить данные снова.'
    )
    DATA_WAS_SAVED_MESSAGE = (
        'Твои данные сохранены. УРА!'
    )
    CHOOSE_SEARCH_CRITERIA_MESSAGE = (
        'Выберите критерий поиска.'
    )
    CHOOSE_TEAM_MESSAGE = (
        'Выбери, пожалуйста, интересующую тебя команду в Школе 21.'
    )
    INCORRECT_CHOOSE_MESSAGE = (
        'Некорректный выбор. Попробуйте снова.'
    )
    NO_NICKNAME_SEARCH_RESULTS_MESSAGE = (
        'По заданным параметрам результатов нет. '
        'Проверь, что данные введены корректно и попробуй еще раз.'
    )
    NO_USER_INFO_MESSAGE = (
        'Информация о пользователе не найдена.'
    )
    CANT_BACK_TO_LIST_MESSAGE = (
        'Не удалось вернуться к списку. Начните сначала.'
    )
    CANT_BACK_TO_PREVIOUS_STEP_MESSAGE = (
        'Не удалось вернуться к предыдущему шагу. Начните сначала.'
    )
    ENTER_PEER_NICKNAME_MESSAGE = (
        'Введи ник пользователя в ТГ, Сберчате или в Школе 21.'
    )
    LOOKING_FOR_WHO_MESSAGE = 'Кого ищем?'
    current_value_of_field_message = (
        'Сейчас {field_name}: {current_value}. Введите новое значение.'
    )
    join_to_community_message = (
        'Пожалуйста, присоединись к <a href="{link}">Коммьюнити</a>.'
    )
    with_team_nobody_found_message = (
        'С командой {team_name} никого не нашлось:('
    )
    role_what_level_message = (
        'Роль: {selected_role}. А какой уровень?'
    )
    nobody_with_set_role_level_message = (
        'С ролью {selected_role} и '
        'уровнем {selected_level} никого не нашлось:('
    )
    peer_from_team_message = (
        'Пиры из команды {team_name}:'
    )
    peer_with_nickname_message = (
        'Пиры с никнеймом {nickname}:'
    )
    peers_with_role_level_message = (
        'Пиры с ролью {role} и уровнем {display_level}:'
    )


class MetricMessage:
    REGISTRATION_STARTED = 'Старт регистрации'
    SCHOOL_21_NICKNAME_ENTERED = 'Введен ник школы 21'
    SCHOOL_21_NICKNAME_INVALID = 'Ник школы 21 не прошел валидацию'
    SBERCHAT_NICKNAME_ENTERED = 'Введен ник Сберчата'
    SBERCHAT_NICKNAME_INVALID = 'Ник Сберчата не прошел валидацию'
    TELEGRAM_NICKNAME_ENTERED = 'Введен ник Телеграм'
    TELEGRAM_NICKNAME_INVALID = 'Ник Телеграм не прошел валидацию'
    TEAM_NAME_ENTERED = 'Введено название команды'
    TEAM_NAME_INVALID = 'Название команды не прошло валидацию'
    USER_ROLE_ENTERED = 'Введена роль в команде'
    USER_ROLE_INVALID = 'Роль в команде не прошла валидацию'
    ROLE_LEVEL_ENTERED = 'Выбран уровень квалификации'
    ROLE_LEVEL_INVALID = 'Пожалуйста, выберите уровень, нажав на кнопку.'
    PROJECT_ENTERED = 'Введено поле "Проект"'
    PROJECT_INVALID = 'Поле "Проект" не прошло валидацию'
    PROJECT_NOT_SPECIFIED = 'Пропущено поле "Проект"'
    LEVEL_UPDATED = 'Обновлено поле "Уровень квалификации"'
    field_updated = 'Обновлено поле {field_for_edit}'
    SCHOOL_21_NICKNAME_NOT_UNIQUE = 'Никнейм школы 21 уже существует'


class ButtonText:
    BUTTON_SKIP = 'Пропустить'
    BUTTON_CONFIRM = 'Подтвердить'
    BUTTON_EDIT = 'Изменить'
    BUTTON_NICKNAME_21 = 'Ник в Школе 21'
    BUTTON_NAME_SBERCHAT = 'Имя в Сберчате'
    BUTTON_NICKNAME_TELEGRAM = 'Ник в Telegram'
    BUTTON_TEAM_NAME = 'Название команды'
    BUTTON_YOUR_ROLE = 'Ваша роль'
    BUTTON_YOUR_LEVEL = 'Ваш уровень'
    BUTTON_WORKING_ON = 'Над чем вы работаете'
    BUTTON_CONTINUE = 'Продолжить'
    BUTTON_CONFIRM_JOIN = 'Я присоединился'
    BUTTON_JOIN_COMMUNITY = 'Присоединиться к комьюнити'
    BUTTON_SEARCH_PEERS = 'Поиск пиров'
    BUTTON_AUTHENTICATE = 'Пройти аутентификацию'
    BUTTON_BACK_TO_ROLE_SELECTION = 'Назад к выбору роли'
    BUTTON_BACK_TO_LIST = '← Назад к списку'
    BUTTON_SHOW_TG_NICKNAME = 'Показать ник в ТГ участникам сообщества'
    BUTTON_SEARCH_BY_ROLE = 'По роли'
    BUTTON_SEARCH_BY_TEAM_NAME = 'По названию команды'
    BUTTON_SEARCH_BY_NICKNAME = 'По никнейму'
    BUTTON_BACK_TO_SEARCH_CRITERIA = 'Назад к критериям поиска'
    BUTTON_BACK_TO_SELECTION = '← Назад к выбору'


class ValidatorMessage:
    ERROR_SCHOOL21_NICK = (
        'Ник может содержать только латинские '
        'буквы и должен быть от 4 до 16 символов.')
    ERROR_SBER_NICK = (
        'Укажи имя пользователя в Сберчате — это часть твоего адреса '
        "электронной почты до знака '@'. Он может содержать только буквы "
        'и цифры.')
    ERROR_TELEGRAM_NICK_LENGTH = 'Ник может быть длиной не более 32 символов.'
    ERROR_TELEGRAM_NICK_FORMAT = (
        'Ник может содержать только буквы, цифры, '
        'символы подчеркивания и @.')
    ERROR_TEAM_NAME_LENGTH = (
        'Название команды не может превышать 256 символов.')
    ERROR_TEAM_NAME_FORMAT = (
        'Название команды может содержать только буквы, цифры и пробелы.')
    ERROR_ROLE_NAME_LENGTH = (
        'Название вашей роли не может превышать 128 символов.')
    ERROR_ROLE_NAME_FORMAT = (
        'Название вашей роли может содержать только буквы и пробелы.')
    ERROR_PROJECT_DESCRIPTION_LENGTH = (
        'Описание проекта не может превышать 1024 символа.')


class ServiceConstant:
    PAGE_SIZE = 10
