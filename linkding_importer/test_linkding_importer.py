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
    
    def test_process_invalid_chrome_bookmarks(self):
        # Read the sample Firefox bookmarks file
        with open("repo_files/firefox.json", "r", encoding="utf-8") as file:
            bookmarks_json = json.load(file)
        
        # Process bookmarks and mock the import
        parsed_bookmarks = self.importer.process_bookmarks(bookmarks_json, format="chrome")

        self.assertEqual(0, len(parsed_bookmarks))

    @patch("linkding_importer.linkding_importer.LinkdingImporter.import_to_linkding")
    def test_import_chrome_bookmarks(self, mock_import_to_linkding):
        # Read the sample Chrome bookmarks file
        with open("repo_files/chrome.json", "r", encoding="utf-8") as file:
            bookmarks_json = json.load(file)
        
        # Process bookmarks and mock the import
        parsed_bookmarks = self.importer.process_bookmarks(bookmarks_json, format="chrome")
        self.importer.import_to_linkding(parsed_bookmarks)

        # Verify the number of calls to import_to_linkding
        mock_import_to_linkding.assert_called_once()
        self.assertEqual(len(parsed_bookmarks), mock_import_to_linkding.call_args[0][0].__len__())


    @patch("builtins.open", new_callable=mock_open, read_data='{"children": []}')
    def test_process_bookmarks_firefox(self, mock_file):
        with open("dummy.json", "r") as file:
            bookmarks_json = json.load(file)
        result = self.importer.process_bookmarks(bookmarks_json, format="firefox")
        self.assertEqual(result, [])

    def test_process_invalid_firefox_bookmarks(self):
        # Read the sample Firefox bookmarks file
        with open("repo_files/chrome.json", "r", encoding="utf-8") as file:
            bookmarks_json = json.load(file)
        
        # Process bookmarks and mock the import
        parsed_bookmarks = self.importer.process_bookmarks(bookmarks_json, format="firefox")

        self.assertEqual(0, len(parsed_bookmarks))

    @patch("linkding_importer.linkding_importer.LinkdingImporter.import_to_linkding")
    def test_import_firefox_bookmarks(self, mock_import_to_linkding):
        # Read the sample Firefox bookmarks file
        with open("repo_files/firefox.json", "r", encoding="utf-8") as file:
            bookmarks_json = json.load(file)
        
        # Process bookmarks and mock the import
        parsed_bookmarks = self.importer.process_bookmarks(bookmarks_json, format="firefox")
        self.importer.import_to_linkding(parsed_bookmarks)

        # Verify the number of calls to import_to_linkding
        mock_import_to_linkding.assert_called_once()
        self.assertEqual(len(parsed_bookmarks), mock_import_to_linkding.call_args[0][0].__len__())

    def test_process_bookmarks_invalid_format(self):
        with self.assertRaises(ValueError):
            self.importer.process_bookmarks({}, format="invalid")

    def test_correct_tag_during_chrome_import(self):
        with open("repo_files/chrome_children.json", "r", encoding="utf-8") as file:
            bookmarks_json = json.load(file)
        
        # Process bookmarks and mock the import
        parsed_bookmarks = self.importer.process_bookmarks(bookmarks_json, format="chrome") # my breakpoint
        sut_bookmark = parsed_bookmarks.pop()
        expected_tags = ['bookmarks-bar', 'starx', 'personal', 'active-list', 'startingpages', 'home']
        assert set(expected_tags) == set(sut_bookmark['tags'])


    def test_correct_tag_during_firefox_import(self):
        with open("repo_files/firefox_children.json", "r", encoding="utf-8") as file:
            bookmarks_json = json.load(file)
        
        # Process bookmarks and mock the import
        parsed_bookmarks = self.importer.process_bookmarks(bookmarks_json, format="firefox") # my breakpoint
        sut_bookmark = parsed_bookmarks.pop()
        expected_tags = ['toolbar', 'starx', 'personal', 'active-list', 'startingpages', 'home']
        assert set(expected_tags) == set(sut_bookmark['tags'])
        
