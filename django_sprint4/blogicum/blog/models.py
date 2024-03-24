from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone

User = get_user_model()


class BaseCreationModel(models.Model):
    is_published = models.BooleanField(
        'Опубликовано',
        default=True,
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        abstract = True


class Location(BaseCreationModel):
    name = models.CharField(
        'Название места',
        max_length=256,
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Category(BaseCreationModel):
    title = models.CharField(
        'Заголовок',
        max_length=256,
    )
    description = models.TextField(
        'Описание',
    )
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        max_length=255,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        ),
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class PostQuerySet(models.QuerySet):
    def published(self, filter_post=True):
        queryset = self.prefetch_related(
            'comments'
        ).select_related(
            'location', 'author', 'category'
        ).annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')
        if filter_post:
            return queryset.filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=timezone.now()
            )
        return queryset


class Post(BaseCreationModel):
    objects = PostQuerySet.as_manager()

    title = models.CharField(
        'Заголовок',
        max_length=256,
    )
    text = models.TextField(
        'Текст',
    )
    pub_date = models.DateTimeField(
        'Дата и время',
        help_text=(
            'Если установить дату и время в будущем — можно делать '
            'отложенные публикации.'
        )

    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Местоположение',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField(
        'Изображение',
        blank=True,
        upload_to='posts_images/',
    )

    def comment_count(self):
        return Comment.objects.filter(post=self).count()

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('-pub_date',)

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail', args=[self.pk]
        )


class Comment(models.Model):
    text = models.TextField(
        'Текст',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Номер публикации',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    created_at = models.DateTimeField(
        'Добавлено',
        auto_now_add=True,
    )

    class Meta:
        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарий'
        ordering = ('created_at',)
