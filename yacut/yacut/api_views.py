from datetime import datetime
from http import HTTPStatus

from flask import jsonify, request, abort

from . import app, db
from .error_handlers import InvalidAPIUsage
from .models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_short_link():
    data = request.get_json()

    if not data:
        raise InvalidAPIUsage('Отсутствует тело запроса')

    original_url = data.get('url', None)
    custom_id = data.get('custom_id', None)

    if not original_url:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    url_map = URLMap()

    if not custom_id:
        custom_id = url_map.get_unique_short_id()
        data.update({'custom_id': custom_id})

    if url_map.is_short_link_exists(custom_id):
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.'
        )

    if not url_map.is_valid_short_id(custom_id):
        raise InvalidAPIUsage(
            'Указано недопустимое имя для короткой ссылки'
        )

    url_map.original = original_url
    url_map.short = custom_id
    url_map.timestamp = datetime.utcnow()

    db.session.add(url_map)
    db.session.commit()

    short_link = request.host_url + url_map.short

    response_data = {
        'url': url_map.original,
        'short_link': short_link
    }

    return jsonify(response_data), HTTPStatus.CREATED


@app.route('/api/id/<short_id>/', methods=['GET'])
def get_short_link(short_id):
    url = URLMap.query.filter_by(short=short_id).first()

    if url is not None:
        return jsonify({'url': url.original}), HTTPStatus.OK
    return abort(HTTPStatus.NOT_FOUND, description="Указанный id не найден")
