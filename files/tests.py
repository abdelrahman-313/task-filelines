from django.test import TestCase

import json
import shutil
import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APIRequestFactory

from files.models import UploadedFile
from files.views import (
    FileUploadView,
    RandomLineView,
    RandomLineBackwardsView,
    Longest100LinesView,
    Longest20OfFileView,
)

# Create a temp MEDIA_ROOT so test files go to a throwaway folder
_TEMP_MEDIA_ROOT = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=_TEMP_MEDIA_ROOT)
class ViewTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        # Clean temp media after tests
        shutil.rmtree(_TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.factory = APIRequestFactory()

    # ------------------------
    # FileUploadView
    # ------------------------
    def test_file_upload_success(self):
        view = FileUploadView.as_view()
        content = b"line 1\nline 2\n"
        uploaded = SimpleUploadedFile("sample.txt", content, content_type="text/plain")

        request = self.factory.post(
            "/upload",
            data={"file": uploaded},
            format="multipart",
        )
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.data  # use .data for DRF Response
        self.assertIn("id", data)
        self.assertIn("filename", data)
        self.assertTrue(UploadedFile.objects.filter(id=data["id"]).exists())

    def test_file_upload_missing_file_returns_400(self):
        view = FileUploadView.as_view()
        request = self.factory.post("/upload", data={}, format="multipart")
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ------------------------
    # RandomLineView
    # ------------------------
    def _create_text_file(self, name="sample.txt", content=b"alpha\nbeta\ngamma\n"):
        uploaded = SimpleUploadedFile(name, content, content_type="text/plain")
        return UploadedFile.objects.create(file=uploaded)

    @patch("files.views.random_line", return_value={"line": "hello"})
    def test_random_line_defaults_to_json(self, mock_random_line):
        self._create_text_file()
        view = RandomLineView.as_view()

        request = self.factory.get("/random-line")
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        data = json.loads(response.content.decode())  # HttpResponse, safe to decode
        self.assertEqual(data["random_line"], "hello")

    @patch("files.views.random_line", return_value={"line": "hello"})
    def test_random_line_accept_text_plain(self, mock_random_line):
        self._create_text_file()
        view = RandomLineView.as_view()

        request = self.factory.get("/random-line", HTTP_ACCEPT="text/plain")
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn("random_line:hello", response.content.decode())

    @patch("files.views.random_line", return_value={"line": "hello"})
    def test_random_line_accept_xml(self, mock_random_line):
        self._create_text_file()
        view = RandomLineView.as_view()

        request = self.factory.get("/random-line", HTTP_ACCEPT="application/xml")
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("application/xml", response["Content-Type"])
        self.assertIn("hello", response.content.decode())

    @patch("files.views.random_line", return_value={"line": "hello"})
    def test_random_line_accept_query_param_overrides(self, mock_random_line):
        self._create_text_file()
        view = RandomLineView.as_view()

        request = self.factory.get(
            "/random-line?accept=text/plain", HTTP_ACCEPT="application/json"
        )
        response = view(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertIn("random_line:hello", response.content.decode())

    # ------------------------
    # RandomLineBackwardsView
    # ------------------------
    @patch("files.views.random_line", return_value={"line": "abc"})
    def test_random_line_backwards(self, mock_random_line):
        self._create_text_file()
        view = RandomLineBackwardsView.as_view()
        request = self.factory.get("/random-line-backwards")
        response = view(request)
        self.assertEqual(response.status_code, 200)
        data = response.data  # use .data for DRF Response
        self.assertEqual(data["line_backwards"], "cba")

    # ------------------------
    # Longest100LinesView
    # ------------------------
    @patch("files.views.read_lines")
    def test_longest_100_lines(self, mock_read_lines):
        self._create_text_file(name="a.txt")
        self._create_text_file(name="b.txt")

        mock_read_lines.side_effect = [
            ["short", "medium length", "x" * 120],
            ["tiny", "y" * 200, "z" * 5],
        ]

        view = Longest100LinesView.as_view()
        request = self.factory.get("/longest100")
        response = view(request)
        self.assertEqual(response.status_code, 200)
        data = response.data  # use .data for DRF Response
        self.assertLessEqual(len(data), 100)
        lengths = list(map(len, data))
        self.assertEqual(lengths, sorted(lengths, reverse=True))
        self.assertEqual(data[0], "y" * 200)

    # ------------------------
    # Longest20OfFileView
    # ------------------------
    @patch(
        "files.views.read_lines",
        return_value=["a", "bbb", "cc", "d" * 50, "ee", "f" * 25],
    )
    def test_longest_20_of_file(self, mock_read_lines):
        f = self._create_text_file(name="solo.txt")
        view = Longest20OfFileView.as_view()
        file_pk = getattr(f, "id", None) or getattr(f, "pk", None)
        request = self.factory.get(f"/longest20/{file_pk}")
        response = view(request, file_id=file_pk)
        self.assertEqual(response.status_code, 200)
        data = response.data  # use .data for DRF Response
        self.assertLessEqual(len(data), 20)
        self.assertEqual(data[0], "d" * 50)
        self.assertIn("bbb", data)
