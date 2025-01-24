import json
import re
import requests
import os
import time
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LinkdingImporter:
    def __init__(self, api_url, api_token):
        self.api_url = api_url
        self.api_token = api_token
        self.failed_bookmarks = []

    @staticmethod
    def normalize_folder_name(folder_name):
        folder_name = folder_name.strip().lower()  # Convert to lowercase
        folder_name = re.sub(r"[\s]+", "-", folder_name)  # Replace spaces with hyphens
        folder_name = re.sub(r"[^a-z0-9-]", "", folder_name)  # Remove special characters
        return folder_name

    def process_node(self, node, path=""):
        bookmarks = []
        current_path = f"{path}/{node['name']}" if path else node['name']
        if node.get("type") == "url":
            bookmarks.append({
                "url": node["url"],
                "title": node["name"],
                "tags": [self.normalize_folder_name(tag) for tag in current_path.split("/") if tag]
            })
        elif node.get("type") == "folder" and "children" in node:
            for child in node["children"]:
                bookmarks.extend(self.process_node(child, current_path))
        return bookmarks

    def process_bookmarks(self, bookmarks_json):
        roots = bookmarks_json.get("roots", {})
        all_bookmarks = []
        for root in roots.values():
            all_bookmarks.extend(self.process_node(root))
        return all_bookmarks

    def import_to_linkding(self, bookmarks):
        headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }
        for bookmark in bookmarks:
            data = {
                "url": bookmark["url"],
                "title": bookmark["title"],
                "tag_names": bookmark["tags"]
            }
            try:
                response = requests.post(self.api_url, headers=headers, data=json.dumps(data))
                if response.status_code == 201:
                    print(f"Successfully imported: {bookmark['title']}")
                else:
                    print(f"Failed to import: {bookmark['title']} | Status: {response.status_code} | {response.text}")
                    self.failed_bookmarks.append(bookmark)
            except requests.RequestException as e:
                print(f"Exception occurred for: {bookmark['title']} | Error: {str(e)}")
                self.failed_bookmarks.append(bookmark)
            time.sleep(0.2)  # To avoid rate-limiting

    def save_failed_bookmarks(self, failed_import_file="failed_import.json"):
        if self.failed_bookmarks:
            with open(failed_import_file, "w", encoding="utf-8") as file:
                json.dump(self.failed_bookmarks, file, indent=2)
            print(f"Failed imports saved to {failed_import_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import bookmarks into Linkding.")
    parser.add_argument("--file", required=True, help="Path to the bookmarks JSON file.")

    args = parser.parse_args()

    # Read the input file
    try:
        with open(args.file, "r", encoding="utf-8") as file:
            bookmarks_json = json.load(file)
    except FileNotFoundError:
        print(f"Error: The file '{args.file}' does not exist.")
        exit(1)
    except json.JSONDecodeError:
        print(f"Error: The file '{args.file}' is not a valid JSON file.")
        exit(1)

    # Initialize LinkdingImporter
    importer = LinkdingImporter(
        api_url=os.getenv("LINKDING_API_URL", "http://your-linkding-instance/api/bookmarks/"),
        api_token=os.getenv("LINKDING_API_TOKEN", "your-api-token")
    )

    # Process bookmarks
    parsed_bookmarks = importer.process_bookmarks(bookmarks_json)

    # Import bookmarks
    importer.import_to_linkding(parsed_bookmarks)

    # Save failed imports
    importer.save_failed_bookmarks()
