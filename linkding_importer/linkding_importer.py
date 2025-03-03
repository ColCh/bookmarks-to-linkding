import json
import re
import requests
import time
import openai

class LinkdingImporter:
    def __init__(self, api_url, api_token, openai_token):
        self.api_url = api_url
        self.api_token = api_token
        self.openai_token = openai_token
        self.failed_bookmarks = []

    @staticmethod
    def normalize_folder_name(folder_name):
        folder_name = folder_name.strip().lower()  # Convert to lowercase
        folder_name = re.sub(r"[\s]+", "-", folder_name)  # Replace spaces with hyphens
        folder_name = re.sub(r"[^a-z0-9-]", "", folder_name)  # Remove special characters
        return folder_name

    def process_chrome_node(self, node, path=""):
        bookmarks = []
        current_path = f"{path}/{node['name']}" if path else node['name']
        if node.get("type") == "url":
            bookmarks.append({
                "url": node["url"],
                "title": node["name"],
                "tags": [self.normalize_folder_name(tag) for tag in path.split("/") if tag]
            })
        elif node.get("type") == "folder" and "children" in node:
            for child in node["children"]:
                bookmarks.extend(self.process_chrome_node(child, current_path))
        return bookmarks

    def process_firefox_node(self, node, path=""):
        bookmarks = []
        current_path = f"{path}/{node['title']}" if path else node['title']
        if node.get("type") == "text/x-moz-place":  # URL
            bookmarks.append({
                "url": node["uri"],
                "title": node["title"],
                "tags": [self.normalize_folder_name(tag) for tag in path.split("/") if tag]
            })
        elif node.get("type") == "text/x-moz-place-container" and "children" in node:  # Folder
            for child in node["children"]:
                bookmarks.extend(self.process_firefox_node(child, current_path))
        return bookmarks
        # DEBUG: return first
        # return bookmarks[0:1]

    def process_bookmarks(self, bookmarks_json, format="chrome"):
        if format == "chrome":
            roots = bookmarks_json.get("roots", {})
            all_bookmarks = []
            for root in roots.values():
                all_bookmarks.extend(self.process_chrome_node(root))
        elif format == "firefox":
            roots = bookmarks_json.get("children", [])
            all_bookmarks = []
            for root in roots:
                all_bookmarks.extend(self.process_firefox_node(root))
        else:
            raise ValueError("Unsupported format. Supported formats are 'chrome' and 'firefox'.")
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

    def add_openai_tags(self, bookmarks):
        openai.api_key = self.openai_token
        bookmarks_with_openai_tags = []
        for bookmark in bookmarks:
            print(f"process: {bookmark["title"]} START")
            # Format the list of existing tags as a comma-separated string
            existing_tags_str = ", ".join(bookmark["tags"])

            print(f"Already existing tags: {existing_tags_str}")

            # Define the prompt for the OpenAI model.
            # This prompt informs the model of its role and provides the necessary context.
            prompt = (
                f"You are an assistant that helps categorize bookmarks by suggesting relevant tags.\n"
                f"Bookmark Title: \"{bookmark["title"]}\"\n"
                f"Bookmark URL: \"{bookmark["url"]}\"\n"
                f"Already suggested tags: {existing_tags_str}\n\n"
                f"Please suggest additional tags that accurately describe the content of this bookmark. "
                f"Return a comma-separated list of tags. BUT NO MORE THAN 3 TAGS."
            )
            client = openai.OpenAI()
            response = client.chat.completions.create(
                model="gpt-4o",
                store=True,
                messages=[
                    {"role": "system", "content": prompt}
                ]
            )
            # Print the raw response message content.
            print(f"OpenAI response for bookmark '{bookmark['title']}': {response.choices[0].message.content}")

            # Extract tags from the response by splitting lines and trimming whitespace.
            tags = [tag.strip() for tag in response.choices[0].message.content.split(",") if tag.strip()]

            # Add the OpenAI suggested tags to the bookmark.
            bookmark["tags"].extend(tags)
            bookmarks_with_openai_tags.append(bookmark)
            print(f"process: {bookmark["title"]} DONE")
        return bookmarks_with_openai_tags