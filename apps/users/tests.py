from django.contrib.auth.models import Group
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class AuthAndRBACAPITestCase(APITestCase):
    def setUp(self):
        Group.objects.get_or_create(name="admin")
        self.admin = User.objects.create_user(
            username="admin", password="adminpass"
        )
        self.admin.groups.add(Group.objects.get(name="admin"))

    def test_login_endpoint(self):
        url = reverse("login")
        response = self.client.post(
            url, {"username": "admin", "password": "adminpass"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_create_user_with_roles(self):
        self.client.login(username="admin", password="adminpass")
        url = reverse("user-list")
        Group.objects.get_or_create(name="editor")
        response = self.client.post(
            url,
            {
                "username": "newuser",
                "email": "new@example.com",
                "roles": ["editor"],
                "password": "testpass123",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
