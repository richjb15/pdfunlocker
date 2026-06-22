"""
Gmail Locked PDF Auto-Unlocker
-------------------------------
Searches Gmail for emails matching a query, downloads PDF attachments,
unlocks them with a known password, and saves the unlocked copies locally.

SETUP (one-time):
1. Go to https://console.cloud.google.com/
2. Create a project (or use an existing one)
3. Enable the "Gmail API"
4. Create OAuth 2.0 credentials (Desktop App type)
5. Download the JSON file and save it as 'credentials.json' in this folder
6. Run: pip install --upgrade google-auth google-auth-oauthlib google-api-python-client pikepdf
7. Edit the CONFIG section below
8. Run: python unlock_pdfs.py
   -> A browser window will open the first time to authorize access.
      After that, a token.json file is saved so you won't need to log in again.
"""

import os
import base64
import pikepdf
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# ───────────────────────────────────────────────────────────
# CONFIG — edit these values
# ───────────────────────────────────────────────────────────
SEARCH_QUERY = 'from:yourbank.co.za has:attachment filename:pdf'  # Gmail search syntax
PDF_PASSWORDS = [
    "YOUR_PDF_PASSWORD_HERE",
    # "ANOTHER_PASSWORD",
    # "YET_ANOTHER_PASSWORD",
]        # the passwords that unlock the PDFs
OUTPUT_FOLDER = "/home/claude/unlocked_pdfs"    # where unlocked PDFs are saved
MAX_EMAILS = 20                                 # how many matching emails to check
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
# ───────────────────────────────────────────────────────────


def get_gmail_service():
    """Authenticate and return a Gmail API service object."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def unlock_pdf_bytes(pdf_bytes, password, out_path):
    """Decrypt PDF bytes with the given password and save to out_path."""
    import io
    try:
        with pikepdf.open(io.BytesIO(pdf_bytes), password=password) as pdf:
            pdf.save(out_path)
        return True
    except pikepdf.PasswordError:
        print(f"  ✗ Wrong password for this PDF, skipping: {out_path}")
        return False
    except pikepdf._core.PdfError as e:
        # Not actually encrypted, or already unlocked — just save as-is
        with open(out_path, "wb") as f:
            f.write(pdf_bytes)
        return True


def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    service = get_gmail_service()

    print(f"Searching Gmail for: {SEARCH_QUERY}")
    results = service.users().messages().list(
        userId="me", q=SEARCH_QUERY, maxResults=MAX_EMAILS
    ).execute()
    messages = results.get("messages", [])

    if not messages:
        print("No matching emails found.")
        return

    print(f"Found {len(messages)} matching email(s). Processing...")
    saved_count = 0

    for msg_meta in messages:
        msg_id = msg_meta["id"]
        msg = service.users().messages().get(userId="me", id=msg_id).execute()

        # Get subject for naming/logging
        headers = msg["payload"].get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "no_subject")
        safe_subject = "".join(c if c.isalnum() or c in " _-" else "_" for c in subject)[:50]

        parts = msg["payload"].get("parts", [])
        for part in parts:
            filename = part.get("filename", "")
            if filename.lower().endswith(".pdf"):
                attachment_id = part["body"].get("attachmentId")
                if not attachment_id:
                    continue
                attachment = service.users().messages().attachments().get(
                    userId="me", messageId=msg_id, id=attachment_id
                ).execute()
                file_data = base64.urlsafe_b64decode(attachment["data"])

                out_name = f"{safe_subject}_{filename}"
                out_path = os.path.join(OUTPUT_FOLDER, out_name)

                print(f"  Unlocking: {filename}  (from: \"{subject}\")")
                if unlock_pdf_bytes(file_data, PDF_PASSWORD, out_path):
                    print(f"  ✓ Saved unlocked copy: {out_path}")
                    saved_count += 1

    print(f"\nDone. {saved_count} unlocked PDF(s) saved to {OUTPUT_FOLDER}")


if __name__ == "__main__":
    main()
