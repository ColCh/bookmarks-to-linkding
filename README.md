# Bookmarks to Linkding

This will allow you to import your bookmarks into the linkding platform. 

p.s As LinkDing does not support folder structure, this script will convert the folder structure to tags so you can still group them together.

## How to use

**Step 1:** Get your bookmarks in JSON format

**Firefox**

Backup bookmarks from the Bookmarks manager. If unsure, see [this](https://support.mozilla.org/en-US/kb/restore-bookmarks-from-backup-or-move-them#w_manual-backup)

**Chrome**

By default, Chrome stores your bookmarks as JSON, for example:

For Windows users:

    C:\Users\user\AppData\Local\Google\Chrome\User Data\Default\Bookmarks

For Linux users:

    ~/.config/chrome/Default/Bookmarks

For Mac users:

    ~/Library/Application Support/Google/Chrome/Default/Bookmarks

Then, copy the file to an easy location.

**Step 2:** Clone the project folder, create a virtualenv, activate it and install the requirements.

```bash
git clone https://github.com/starx/bookmarks-to-linkding.git
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Step 3:** Copy the bookmarks file to the project folder.

**Step 4:** Add your linkding credentials 

Get your rest api key, from your settings page.

![linkding_rest_api_key](./repo_files/linkding_rest_api_key.jpeg)

```bash
export LINKDING_API_URL="http://your-linkding-instance/api/bookmarks/"
export LINKDING_API_TOKEN="your-api-token"
```

**Step 5:** Run the script

For chrome:

    python main.py --file bookmarks.json --format chrome

For firefox:

    python main.py --file bookmarks.json --format firefox

That's it. Failed import will be saved in `failed_import.json`, so review them after finish.
