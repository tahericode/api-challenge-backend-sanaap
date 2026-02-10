from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class DocumentAPITestCase(APITestCase):
    def setUp(self):
        # create groups for RBAC
        for name in ["admin", "editor", "viewer"]:
            Group.objects.get_or_create(name=name)

        self.admin = User.objects.create_user(
            username="admin", password="adminpass"
        )
        self.admin.groups.add(Group.objects.get(name="admin"))

        self.editor = User.objects.create_user(
            username="editor", password="editorpass"
        )
        self.editor.groups.add(Group.objects.get(name="editor"))

        self.viewer = User.objects.create_user(
            username="viewer", password="viewerpass"
        )
        self.viewer.groups.add(Group.objects.get(name="viewer"))

    def test_editor_can_upload_document(self):
        self.client.login(username="editor", password="editorpass")
        url = reverse("document-list")
        file = SimpleUploadedFile(
            "test.txt", b"hello world", content_type="text/plain"
        )
        response = self.client.post(
            url,
            {"file": file},
            format="multipart",
            HTTP_IDEMPOTENCY_KEY="idem-1",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_viewer_cannot_upload_document(self):
        self.client.login(username="viewer", password="viewerpass")
        url = reverse("document-list")
        file = SimpleUploadedFile(
            "test.txt", b"hello world", content_type="text/plain"
        )
        response = self.client.post(
            url,
            {"file": file},
            format="multipart",
            HTTP_IDEMPOTENCY_KEY="idem-2",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
