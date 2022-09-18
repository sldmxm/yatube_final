from django.contrib.auth import get_user_model
from django.urls import reverse

from ..models import Post, Comment
from .fixtures import PostTests


User = get_user_model()


class PostFormsTests(PostTests):
    def test_create_post(self):
        old_posts_pk = [pk for pk in
                        Post.objects
                        .values_list('pk', flat=True)]
        form_data = {
            'text': 'Новый тестовый текст',
            'group': self.group.pk,
            'image': self.uploaded_gif.open(),
        }
        self.authorized_client.force_login(self.author_user)
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile',
                    kwargs={'username': self.author_user.username}))
        self.assertEqual(Post.objects.count(), len(old_posts_pk) + 1)
        new_post = Post.objects.exclude(pk__in=old_posts_pk).last()
        new_post_data = [
            (new_post.text, form_data['text']),
            (new_post.group, self.group),
            (new_post.author, self.author_user),
        ]
        for field, volume in new_post_data:
            with self.subTest():
                self.assertEqual(field, volume)
        self.assertIsNot(new_post.image, '')

    def test_edit_post(self):
        form_data = {
            'text': 'Новая редакция',
            'group': self.another_group.pk,
        }
        self.authorized_client.force_login(self.author_user)
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.pk}))
        edited_post = Post.objects.get(pk=self.post.pk)
        edited_post_data = [
            (edited_post.text, form_data['text']),
            (edited_post.group, self.another_group),
            (edited_post.author, self.post.author),
        ]
        for field, volume in edited_post_data:
            with self.subTest():
                self.assertEqual(field, volume)

    def test_comment_add(self):
        old_comments_pk = [pk for pk in
                           Comment.objects
                           .filter(post=self.post.pk)
                           .values_list('pk', flat=True)]
        form_data = {
            'text': 'Тестовый комментарий',
        }
        self.authorized_client.post(
            reverse('posts:add_comment',
                    kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects
                         .filter(post=self.post.pk)
                         .count(),
                         len(old_comments_pk) + 1)
        new_comment = Comment.objects.exclude(pk__in=old_comments_pk).last()
        self.assertEqual(new_comment.text, form_data.get('text'))
