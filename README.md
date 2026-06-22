Gmail Locked PDF Auto-Unlocker
Automatically finds password-protected PDFs in your Gmail (e.g. bank statements),
downloads them, and saves unlocked copies locally.
One-time setup
1. Get Gmail API access

Go to https://console.cloud.google.com/
Create a new project (top left dropdown → New Project)
In the search bar, search "Gmail API" → click it → click Enable
Go to APIs & Services → Credentials
Click Create Credentials → OAuth client ID

If prompted, configure the consent screen first (choose "External", fill in
app name + your email, you can leave most fields default, add yourself as
a test user)
Application type: Desktop app


Download the JSON file it gives you, rename it to credentials.json,
and place it in this same folder as unlock_pdfs.py

2. Install dependencies
bashpip install --upgrade google-auth google-auth-oauthlib google-api-python-client pikepdf
3. Edit the config
Open unlock_pdfs.py and edit these lines near the top:
pythonSEARCH_QUERY = 'from:yourbank.co.za has:attachment filename:pdf'
PDF_PASSWORD = "YOUR_PDF_PASSWORD_HERE"
OUTPUT_FOLDER = "/home/claude/unlocked_pdfs"

SEARCH_QUERY uses normal Gmail search syntax — test it in Gmail's search bar first
PDF_PASSWORD — the password that opens your bank's PDFs (often an ID number)
OUTPUT_FOLDER — change to wherever you want files saved locally, e.g.
/Users/yourname/Documents/UnlockedStatements on Mac

4. Run it
bashpython unlock_pdfs.py
The first time, a browser window opens asking you to log into Google and approve
access. After that, it remembers you (via token.json) and won't ask again.
Notes

This only requests read-only Gmail access — it can't send, delete, or modify
anything in your inbox.
If your bank uses different passwords for different statements (e.g. ID number
changes aren't typical, but worth checking), you'll need to handle that case —
let me know if so and I can extend the script to try multiple passwords.
Re-running the script will re-process the same emails. Ask me if you'd like
it to skip files it's already unlocked.
