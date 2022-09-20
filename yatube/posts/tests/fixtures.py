import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.conf import settings

from ..models import Post, Group


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.POSTS_IN_GROUP = 13
        cls.POSTS_IN_ANOTHER_GROUP = 14
        cls.author_user = User.objects.create_user(username='author_user')
        cls.another_author_user = User.objects.create_user(username='author2')
        cls.auth_user = User.objects.create_user(username='just_looking')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='157_157',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Другая тестовая группа',
            slug='000_000',
            description='Тестовое описание другой тестовой группы',
        )
        cls.uploaded_gif = SimpleUploadedFile(
            name='small.gif',
            content=(
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            ),
            content_type='image/gif',
        )
        for post_num in range(cls.POSTS_IN_GROUP):
            Post.objects.create(
                author=cls.author_user,
                text=f'Пост #{post_num} первого автора',
                group=cls.group,
                image=cls.uploaded_gif,
            )
        for post_num in range(cls.POSTS_IN_ANOTHER_GROUP):
            Post.objects.create(
                author=cls.another_author_user,
                text=f'Пост #{post_num} другого автора',
                group=cls.another_group,
            )
        cls.post = Post.objects.order_by().first()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.auth_user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)
