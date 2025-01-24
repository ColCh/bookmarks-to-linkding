from .linkding_importer import LinkdingImporter
import json
from unittest import TestCase
from unittest.mock import patch, mock_open, MagicMock

class TestLinkdingImporter(TestCase):
    def setUp(self):
        self.api_url = "http://example.com/api/bookmarks/"
        self.api_token = "test-token"
        self.importer = LinkdingImporter(api_url=self.api_url, api_token=self.api_token)

    def test_normalize_folder_name(self):
        self.assertEqual(self.importer.normalize_folder_name("Test Folder"), "test-folder")
        self.assertEqual(self.importer.normalize_folder_name("Folder With Spaces"), "folder-with-spaces")
        self.assertEqual(self.importer.normalize_folder_name(" Folder With Spaces at the start and end "), "folder-with-spaces-at-the-start-and-end")
        self.assertEqual(self.importer.normalize_folder_name("Special@Chars!"), "specialchars")
        self.assertEqual(self.importer.normalize_folder_name("Special@ Chars!"), "special-chars")

    @patch("requests.post")
    def test_import_to_linkding_success(self, mock_post):
        mock_post.return_value.status_code = 201
        bookmarks = [{"url": "http://example.com", "title": "Example", "tags": ["test"]}]
        self.importer.import_to_linkding(bookmarks)
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_import_to_linkding_failure(self, mock_post):
        mock_post.return_value.status_code = 400
        bookmarks = [{"url": "http://example.com", "title": "Example", "tags": ["test"]}]
        self.importer.import_to_linkding(bookmarks)
        self.assertEqual(len(self.importer.failed_bookmarks), 1)

    @patch("builtins.open", new_callable=mock_open, read_data='{"roots": {}}')
    def test_process_bookmarks_chrome(self, mock_file):
        with open("dummy.json", "r") as file:
            bookmarks_json = json.load(file)
        result = self.importer.process_bookmarks(bookmarks_json, format="chrome")
        self.assertEqual(result, [])

    @patch("builtins.open", new_callable=mock_open, read_data='{"children": []}')
    def test_process_bookmarks_firefox(self, mock_file):
        with open("dummy.json", "r") as file:
            bookmarks_json = json.load(file)
        result = self.importer.process_bookmarks(bookmarks_json, format="firefox")
        self.assertEqual(result, [])

    def test_process_bookmarks_invalid_format(self):
        with self.assertRaises(ValueError):
            self.importer.process_bookmarks({}, format="invalid")