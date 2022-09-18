from http import HTTPStatus

from django.core.cache import cache
from django.urls import reverse

from .fixtures import PostTests


class PostURLTests(PostTests):
    def test_revers_names_to_urls(self):
        url_and_names = [
            (reverse('posts:index'),
             '/'),
            (reverse('posts:group_list',
                     kwargs={'slug': self.group.slug}),
             f'/group/{self.group.slug}/'),
            (reverse('posts:profile',
                     kwargs={'username': self.author_user.username}),
             f'/profile/{self.author_user.username}/'),
            (reverse('posts:post_detail',
                     kwargs={'post_id': self.post.pk}),
             f'/posts/{self.post.pk}/'),
            (reverse('posts:post_create'),
             '/create/'),
            (reverse('posts:post_edit',
                     kwargs={'post_id': self.post.pk}),
             f'/posts/{self.post.pk}/edit/'),
        ]
        self.authorized_client.force_login(self.author_user)
        for reverse_name, url in url_and_names:
            with self.subTest():
                self.assertEqual(reverse_name, url)

    def test_urls_exist_at_desired_location(self):
        urls = [
            (reverse('posts:index'),
             HTTPStatus.OK,
             False),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
             HTTPStatus.OK,
             False),
            (reverse('posts:profile',
                     kwargs={'username': self.author_user.username}),
             HTTPStatus.OK,
             False),
            (reverse('posts:post_detail',
                     kwargs={'post_id': self.post.pk}),
             HTTPStatus.OK,
             False),
            (reverse('posts:post_create'),
             HTTPStatus.OK,
             True),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
             HTTPStatus.OK,
             True),
            ('/100/500/800/',
             HTTPStatus.NOT_FOUND,
             True)
        ]
        self.authorized_client.force_login(self.author_user)
        for name, status, author_needed in urls:
            with self.subTest():
                if author_needed:
                    response = self.authorized_client.get(name)
                else:
                    response = self.guest_client.get(name)
                self.assertEqual(response.status_code, status)

    def test_redirect(self):
        urls_redirect = [
            (reverse('posts:post_create'),
             '/auth/login/?next=/create/',
             False),
            (reverse('posts:post_edit',
                     kwargs={'post_id': self.post.pk}),
             f'/auth/login/?next=/posts/{self.post.pk}/edit/',
             False),
            (reverse('posts:post_edit',
                     kwargs={'post_id': self.post.pk}),
             (reverse('posts:post_detail',
                      kwargs={'post_id': self.post.pk})),
             True),
            (reverse('posts:add_comment',
                     kwargs={'post_id': self.post.pk}),
             f'/auth/login/?next=/posts/{self.post.pk}/comment/',
             False),
            (reverse('posts:add_comment',
                     kwargs={'post_id': self.post.pk}),
             (reverse('posts:post_detail',
                      kwargs={'post_id': self.post.pk})),
             True),
        ]
        for name, redirect, authorized in urls_redirect:
            with self.subTest():
                if authorized:
                    response = self.authorized_client.get(name)
                else:
                    response = self.guest_client.get(name)
                self.assertRedirects(
                    response, redirect
                )

    def test_urls_uses_correct_template(self):
        cache.clear()
        templates_url_names = [
            (reverse('posts:index'),
             'posts/index.html'),
            (reverse('posts:group_list', kwargs={'slug': self.group.slug}),
             'posts/group_list.html'),
            (reverse('posts:profile',
                     kwargs={'username': self.author_user.username}),
             'posts/profile.html'),
            (reverse('posts:post_detail',
                     kwargs={'post_id': self.post.pk}),
             'posts/post_detail.html'),
            (reverse('posts:post_create'),
             'posts/create_post.html'),
            (reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
             'posts/create_post.html'),
        ]
        self.authorized_client.force_login(self.author_user)
        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
