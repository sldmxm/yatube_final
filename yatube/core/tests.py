from http import HTTPStatus

from django.test import TestCase, Client


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_404_uses_correct_template(self):
        response = self.guest_client.get('/nowhere_address/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
