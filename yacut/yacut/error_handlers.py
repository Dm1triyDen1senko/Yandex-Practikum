from http import HTTPStatus

from flask import jsonify, render_template, request

from . import app, db


class InvalidAPIUsage(Exception):
    def __init__(self, message, status_code=HTTPStatus.BAD_REQUEST):
        super().__init__(message)
        self.status_code = status_code

    def to_dict(self):
        return dict(message=str(self))


@app.errorhandler(InvalidAPIUsage)
def invalid_api_usage(error):
    return jsonify(error.to_dict()), error.status_code


@app.errorhandler(HTTPStatus.BAD_REQUEST)
def bad_request(error):
    response = jsonify({
        "message": "Отсутствует тело запроса"
    })
    return response, HTTPStatus.BAD_REQUEST


@app.errorhandler(HTTPStatus.NOT_FOUND)
def page_not_found(error):
    if request.path.startswith('/api/'):
        response = jsonify({'message': 'Указанный id не найден'})
        return response, HTTPStatus.NOT_FOUND
    return render_template('404.html'), HTTPStatus.NOT_FOUND


@app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), HTTPStatus.INTERNAL_SERVER_ERROR