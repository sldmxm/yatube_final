from math import ceil

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from ..models import Post
from ..forms import PostForm
from .fixtures import PostTests


User = get_user_model()


class PostViewsTests(PostTests):
    def test_index_cache(self):
        Post.objects.create(
            author=self.author_user,
            text='Hello World!',
        )
        response_before_delete = self.guest_client.get(reverse('posts:index'))
        Post.objects.first().delete()
        response_after_delete = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(
            response_before_delete.context,
            response_after_delete.context
        )
        cache.clear()
        response_cache_clear = self.guest_client.get(reverse('posts:index'))
        self.assertNotEqual(
            response_before_delete.context,
            response_cache_clear.context
        )

    def test_follow_and_unfollow(self):
        # Проверяем, в лентах подписок нет постов
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
        self.authorized_client.force_login(self.author_user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
        # Подписываемся
        self.authorized_client.force_login(self.auth_user)
        self.authorized_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author_user.username}),
        )
        # Публикуем пост и проверяем появление
        # его и остальных постов в ленте подписчика,
        # и пустую ленту не подписчика
        Post.objects.create(
            author=self.author_user,
            text='Hello World!',
        )
        self.authorized_client.force_login(self.auth_user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertQuerysetEqual(
            response.context['page_obj'].object_list,
            self.author_user.posts.all()[:settings.POSTS_PER_PAGE],
            transform=lambda x: x
        )
        self.authorized_client.force_login(self.author_user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)
        # Отменяем подписку и проверяем
        # пустую ленту подписок бывшего подписчика
        self.authorized_client.force_login(self.auth_user)
        self.authorized_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author_user.username}),
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_context_for_list_pages(self):
        cache.clear()
        list_pages = [
            (reverse('posts:index'),
                Post.objects.all()),
            (reverse('posts:group_list',
                     kwargs={'slug': self.group.slug}),
                self.group.posts),
            (reverse('posts:profile',
                     kwargs={'username': self.author_user.username}),
                self.author_user.posts),
        ]
        for reverse_name, posts in list_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                # Проверяем все посты первых страниц:
                # - последние посты попали на главную,
                # - на странице группы и автора их последние посты,
                # - чужие опубликованы позже, но их нет
                #   на странице группы и автора
                self.assertQuerysetEqual(
                    response.context['page_obj'].object_list,
                    posts.all()[:settings.POSTS_PER_PAGE],
                    transform=lambda x: x
                )

    def test_paginator(self):
        list_pages = [
            (reverse('posts:index'),
             Post.objects.all(),
             self.POSTS_IN_GROUP + self.POSTS_IN_ANOTHER_GROUP),
            (reverse('posts:group_list',
                     kwargs={'slug': self.group.slug}),
             self.group.posts,
             self.POSTS_IN_GROUP),
            (reverse('posts:profile',
                     kwargs={'username': self.author_user.username}),
             self.author_user.posts,
             self.POSTS_IN_GROUP),
        ]
        for reverse_name, posts, posts_count in list_pages:
            cache.clear()
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                pages_num = ceil(posts_count / settings.POSTS_PER_PAGE)
                num_posts_last_page = (posts_count
                                       - (pages_num - 1)
                                       * settings.POSTS_PER_PAGE)
                self.assertEqual(
                    response.context['page_obj'].paginator.num_pages,
                    pages_num
                )
                response = self.client.get(reverse_name + f'?page={pages_num}')
                self.assertEqual(
                    len(response.context['page_obj']),
                    num_posts_last_page
                )

    def test_context_for_post_detail(self):
        post_with_gif = Post.objects.exclude(image='').first()
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_with_gif.pk})
        )
        self.assertEqual(response.context.get('post'), post_with_gif)

    def test_context_for_post_create_and_edit(self):
        form_pages = [
            (reverse('posts:post_create'), None),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
             self.post.pk),
        ]
        self.authorized_client.force_login(self.author_user)
        for reverse_name, instance in form_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIsInstance(
                    response.context['form'], PostForm)
                self.assertEqual(
                    response.context.get('form').instance.id, instance)
