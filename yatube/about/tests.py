from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client


User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exist_at_desired_location_guest(self):
        urls = [
            ('/about/author/'),
            ('/about/tech/'),
        ]
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        templates_url_names = [
            ('/about/author/', 'about/resume.html'),
            ('/about/tech/', 'about/tech.html'),
        ]
        for address, template in templates_url_names:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
