from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Укажите название группы'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Краткое имя',
        help_text='Укажите сокращенное имя группы для адресной строки'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Укажите описание группы'
    )

    def __str__(self):  # Меняем отображение объекта Group
        return self.title


class Post(models.Model):
    CHARS_IN_STR = 15

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Введите дату публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Введите автора публикации'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
        blank=True, null=True
    )
    image = models.ImageField(
        upload_to='posts/',
        blank=True,
        verbose_name='Картинка',
        help_text='Картинка, удачно дополняющая пост',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:self.CHARS_IN_STR]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментируемый пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата комментария',
    )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_following',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='restrict_self_follow',
            ),
        ]
