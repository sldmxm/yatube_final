from django.contrib.auth import get_user_model

from .fixtures import PostTests
from ..models import Post

User = get_user_model()


class PostModelTest(PostTests):
    def test_models_have_correct_object_names(self):
        object_names = [
            (self.post, self.post.text[:Post.CHARS_IN_STR]),
            (self.group, self.group.title),
        ]
        for obj, name in object_names:
            with self.subTest():
                self.assertEqual(str(obj), name)

    def test_models_have_correct_verbose(self):
        post = PostModelTest.post
        field_verboses = [
            ('text', 'Текст поста'),
            ('pub_date', 'Дата публикации'),
            ('author', 'Автор'),
            ('group', 'Группа'),
        ]
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_models_have_correct_help(self):
        post = PostModelTest.post
        field_help = [
            ('text', 'Введите текст поста'),
            ('pub_date', 'Введите дату публикации'),
            ('author', 'Введите автора публикации'),
            ('group', 'Группа, к которой будет относиться пост'),
        ]
        for field, expected_value in field_help:
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value)
