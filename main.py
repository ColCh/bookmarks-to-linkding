import json
import os
import argparse
from dotenv import load_dotenv
from linkding_importer import LinkdingImporter

# Load environment variables from .env file
load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import bookmarks into Linkding.")
    parser.add_argument("--file", required=True, help="Path to the bookmarks JSON file.")
    parser.add_argument("--format", required=True, choices=["chrome", "firefox"], help="Bookmarks format: 'chrome' or 'firefox'.")

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
    parsed_bookmarks = importer.process_bookmarks(bookmarks_json, format=args.format)

    # Import bookmarks
    importer.import_to_linkding(parsed_bookmarks)

    # Save failed imports
    importer.save_failed_bookmarks()
