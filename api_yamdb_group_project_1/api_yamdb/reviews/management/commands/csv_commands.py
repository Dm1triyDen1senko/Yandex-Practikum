from csv import DictReader

from django.conf import settings
from django.core.management import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, GenreTitle
from reviews.models import CustomUser

DATA_DB = {
    CustomUser: 'users.csv',
    Category: 'category.csv',
    Genre: 'genre.csv',
    Title: 'titles.csv',
    Review: 'review.csv',
    Comment: 'comments.csv',
    GenreTitle: 'genre_title.csv'
}


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        try:
            for model, name_csv in DATA_DB.items():
                with open(
                    f'{settings.BASE_DIR}/static/data/{name_csv}',
                    'r',
                    encoding='utf-8'
                ) as csv_file:
                    reader = DictReader(csv_file)
                    model.objects.bulk_create(
                        model(**data) for data in reader)
        except FileNotFoundError:
            self.stdout.write(
                self.style.ERROR_OUTPUT(
                    'Ошибка при импорте данных в БД. '
                    'Отсутствуют нужные файлы!'))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    'Данные успешно загружены в БД.'))
