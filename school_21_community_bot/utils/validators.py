import re

from constants import ValidatorMessage


def validate_nickname_school21(nick):
    if re.match(r'^[A-Za-z]{4,16}$', nick):
        return True, None
    else:
        return False, ValidatorMessage.ERROR_SCHOOL21_NICK


def validate_nickname_sber(nick):
    if re.match(r'^[A-Za-zА-Яа-я0-9]{1,256}$', nick):
        return True, None
    else:
        return False, ValidatorMessage.ERROR_SBER_NICK


def validate_nickname_telegram(nick):
    if len(nick) > 32:
        return False, ValidatorMessage.ERROR_TELEGRAM_NICK_LENGTH

    if not nick.startswith('@'):
        nick = '@' + nick

    if re.match(r'^[A-Za-zА-Яа-я0-9_@]+$', nick):
        return True, None
    else:
        return False, ValidatorMessage.ERROR_TELEGRAM_NICK_FORMAT


def validate_team_name(team_name):
    if len(team_name) > 256:
        return False, ValidatorMessage.ERROR_TEAM_NAME_LENGTH

    if not re.match(r'^[A-Za-zА-Яа-я0-9 ]+$', team_name):
        return False, ValidatorMessage.ERROR_TEAM_NAME_FORMAT
    return True, None


def validate_role_name(role_name):
    if len(role_name) > 128:
        return False, ValidatorMessage.ERROR_ROLE_NAME_LENGTH

    if not re.match(r'^[A-Za-zА-Яа-я ]+$', role_name):
        return False, ValidatorMessage.ERROR_ROLE_NAME_FORMAT
    return True, None


def validate_project_description(description):
    if len(description) > 1024:
        return False, ValidatorMessage.ERROR_PROJECT_DESCRIPTION_LENGTH
    return True, None
