import datetime

import datetime as dt

from django.core.exceptions import ValidationError


def validate_year(value):
    year = dt.date.today().year
    if value > year:
        raise ValidationError('Этот год еще не наступил.')
    return value


def validate_username(value):
    if value == 'me':
        raise ValidationError(
            'Нельзя использовать "me" в качестве имени пользователя'
        )
