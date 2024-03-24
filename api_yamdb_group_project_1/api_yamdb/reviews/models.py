from django.contrib.auth.models import AbstractUser
from django.core.validators import (
    MaxValueValidator, MinValueValidator
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from .validators import validate_year, validate_username
from api_yamdb import settings


class CustomUser(AbstractUser):
    class UserRole(models.TextChoices):
        USER = 'user'
        MODERATOR = 'moderator'
        ADMIN = 'admin'

    username = models.CharField(
        max_length=settings.USER_MAX_LENGTH,
        unique=True,
        validators=[
            UnicodeUsernameValidator(),
            validate_username
        ],
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        unique=True, verbose_name='Эл. почта'
    )
    bio = models.TextField(blank=True, verbose_name='Биография')
    role = models.CharField(
        choices=UserRole.choices,
        default=UserRole.USER,
        max_length=settings.USER_MAX_LENGTH,
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['id']

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.UserRole.ADMIN

    @property
    def is_moderator(self):
        return self.is_staff or self.role == self.UserRole.MODERATOR

    def __str__(self):
        return self.username


class Category(models.Model):
    """Категории произведений."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        unique=True,
        max_length=settings.MAX_LENGTH_SLUG,
        verbose_name='Слаг категории'
    )

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self) -> str:
        return self.slug


class Genre(models.Model):
    """Жанры произведений."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name='Название категории'
    )
    slug = models.SlugField(
        max_length=settings.MAX_LENGTH_SLUG,
        unique=True,
        verbose_name='Слаг жанра'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['name']

    def __str__(self) -> str:
        return self.slug


class Title(models.Model):
    """Произведения."""

    name = models.CharField(
        max_length=settings.MAX_LENGTH_NAME,
        verbose_name='Название произведения'
    )
    year = models.SmallIntegerField(
        verbose_name='Год создания',
        validators=[validate_year]
    )
    description = models.TextField(
        verbose_name='Описание произведения',
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='genre',
        verbose_name='Жанр'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='category',
        verbose_name='Категория',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['year']

    def __str__(self) -> str:
        return self.name


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='reviews')
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                settings.REVIEW_SCORE_MIN_VALUE,
                message='Оценка имеет границы от 1 до 10'
            ),
            MaxValueValidator(
                settings.REVIEW_SCORE_MAX_VALUE,
                message='Оценка имеет границы от 1 до 10'
            ),
        ]
    )
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_pair'
            ),
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['pub_date']

    def __str__(self):
        return self.score


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments")
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True)
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['review']

    def __str__(self) -> str:
        return self.text


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE
    )
