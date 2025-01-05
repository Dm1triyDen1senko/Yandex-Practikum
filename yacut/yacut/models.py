import string
from datetime import datetime, timezone
from random import choice

from . import db


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(), nullable=False)
    short = db.Column(db.String(16), nullable=True)
    timestamp = db.Column(
        db.DateTime, index=True, default=datetime.now(timezone.utc)
    )

    def get_unique_short_id(self):
        result_short_id = ''
        while len(result_short_id) != 6:
            result_short_id += choice(string.ascii_letters + string.digits)

        if not self.is_short_link_exists(result_short_id):
            return result_short_id
        return self.get_unique_short_id()

    def is_short_link_exists(self, custom_id):
        return self.query.filter_by(short=custom_id).first()

    def is_valid_short_id(self, short_id):
        if len(short_id) > 16:
            return False
        for value in short_id:
            if value not in string.ascii_letters + string.digits:
                return False
        return True
