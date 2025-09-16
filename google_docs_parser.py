import os
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/documents.readonly', 'https://www.googleapis.com/auth/drive.readonly']

class GoogleDocsParser:

    def __init__(self):
        try:
            creds_path = os.path.join(os.getcwd(), 'credentials.json')
            creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
            self.docs_service = build('docs', 'v1', credentials=creds)
            self.drive_service = build('drive', 'v3', credentials=creds)

        except Exception as e:
            raise Exception(
                f"Failed to initialize Google Docs client. Make sure 'creds/credentials.json' exists and is valid. Error: {e}")

    def get_document_content(self, document_id):

        try:
            document = self.docs_service.documents().get(documentId=document_id).execute()
            content = document.get('body').get('content')
            full_text = ""
            for structural_element in content:
                if 'paragraph' in structural_element:
                    for element in structural_element.get('paragraph').get('elements'):
                        if 'textRun' in element:
                            full_text += element.get('textRun').get('content')
            return full_text

        except Exception as e:
            raise Exception(f"Failed to retrieve document content for ID '{document_id}': {e}")

    def parse_tweet_threads(self, text_content):

        threads = []
        thread_blocks = re.findall(
            r'THREAD:\s*([^\n]+)(.*?)^END', text_content, re.MULTILINE | re.DOTALL
        )

        for header, content in thread_blocks:
            thread_id = header.strip()

            tweet_texts = re.split(
                r'^\s*Tweet\s*\d:\s*',
                content,
                flags=re.MULTILINE
            )
            tweet_texts = [t.strip() for t in tweet_texts if t.strip()]

            if 0 < len(tweet_texts) <= 5:
                threads.append({
                    'thread_id': thread_id,
                    'tweets': tweet_texts
                })
            else:
                print(
                    f"Warning: Thread '{thread_id}' has {len(tweet_texts)} tweets. Skipping because it's empty or exceeds the limit of 5.")

        return threads
