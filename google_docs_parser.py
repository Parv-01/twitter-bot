import os
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/documents.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

class GoogleDocsParser:

    def __init__(self):
        try:
            creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")
            creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
            self.docs_service = build('docs', 'v1', credentials=creds)
        except Exception as e:
            raise Exception(
                f"❌ Failed to initialize Google Docs client. Make sure credentials.json exists and is valid. Error: {e}"
            )

    def get_document_content(self, document_id):
        """Retrieve plain text content from the given Google Doc ID."""
        try:
            document = self.docs_service.documents().get(documentId=document_id).execute()
            content = document.get('body', {}).get('content', [])
            full_text = ""

            for structural_element in content:
                if 'paragraph' in structural_element:
                    for element in structural_element['paragraph'].get('elements', []):
                        if 'textRun' in element:
                            full_text += element['textRun'].get('content', '')
            return full_text.strip()

        except Exception as e:
            raise Exception(f"❌ Failed to retrieve document content for ID '{document_id}': {e}")

    def parse_tweet_threads(self, text_content):
        """Parse threads from text with format:
        THREAD: My Thread Title
        Tweet 1: text...
        Tweet 2: text...
        END
        """
        threads = []

        # Capture blocks between THREAD: and END
        thread_blocks = re.findall(r'THREAD:\s*(.*?)\n(.*?)\bEND\b', text_content, re.DOTALL | re.IGNORECASE)

        for header, content in thread_blocks:
            thread_id = header.strip()
            tweet_texts = re.split(r'^\s*Tweet\s*\d+:', content, flags=re.MULTILINE)
            tweet_texts = [t.strip() for t in tweet_texts if t.strip()]

            if 0 < len(tweet_texts) <= 10:
                threads.append({'thread_id': thread_id, 'tweets': tweet_texts})
            else:
                print(f"⚠️ Skipping thread '{thread_id}' (invalid or too many tweets: {len(tweet_texts)})")

        return threads
