import json
import os
from datetime import datetime

import sqlalchemy as sa

from alembic import op


def load_data_to_table(file_name, table_name):
    file_path = os.path.join(os.path.dirname(__file__), file_name)
    with open(file_path, encoding='utf-8') as f:
        data = json.load(f)

    if table_name == 'user':
        data = data["user"]

        for item in data:
            if 'registration_date' in item:
                item['registration_date'] = datetime.fromisoformat(
                    item['registration_date'])

    metadata = sa.MetaData()
    table = sa.Table(table_name, metadata, autoload_with=op.get_bind())

    op.bulk_insert(table, data)


def load_levels():
    load_data_to_table('levels.json', 'level')


def load_users():
    load_data_to_table('user.json', 'user')


def load_roles():
    load_data_to_table('roles.json', 'role')
