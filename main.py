import os
import re
import time
from google_docs_parser import GoogleDocsParser
from twitter_client import TwitterClient

def get_last_posted_thread_id():
    """Reads the ID of the last posted thread from a state file."""
    try:
        with open("last_posted_thread.txt", "r") as f:
            return f.read().strip()
    except FileNotFoundError:
        print("State file 'last_posted_thread.txt' not found. This is expected on the first run.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred while reading the state file: {e}")
        return None

def update_last_posted_thread_id(thread_id):
    """Updates the state file with the ID of the newly posted thread."""
    try:
        with open("last_posted_thread.txt", "w") as f:
            f.write(thread_id)
        print("Successfully updated the last posted thread ID.")
    except Exception as e:
        print(f"Failed to write to the state file: {e}")

def run_bot():
    """Main function to fetch content, select a thread, and post to Twitter."""
    try:
        doc_id = os.environ.get("DOC_ID")
        if not doc_id:
            raise ValueError("DOC_ID not found in environment variables. Please check your GitHub Secrets.")

        print("Connecting to Google Docs and parsing content...")
        docs_parser = GoogleDocsParser()
        text_content = docs_parser.get_document_content(doc_id)
        tweet_threads = docs_parser.parse_tweet_threads(text_content)

        if not tweet_threads:
            print("No valid tweet threads found in the document. Exiting.")
            return

        print(f"Found {len(tweet_threads)} valid tweet threads.")
        last_posted_thread_id = get_last_posted_thread_id()
        thread_to_post = None

        if last_posted_thread_id:
            print(f"Last posted thread ID: {last_posted_thread_id}")
            try:
                last_index = [t['thread_id'] for t in tweet_threads].index(last_posted_thread_id)
                next_index = (last_index + 1) % len(tweet_threads)
                thread_to_post = tweet_threads[next_index]
            except ValueError:
                print("Last posted thread not found in the document. Posting the first thread.")
                thread_to_post = tweet_threads[0]
        else:
            print("No previous post found. Posting the first thread.")
            thread_to_post = tweet_threads[0]

        if not thread_to_post:
            print("No new threads to post. Exiting.")
            return

        print(f"Selected thread to post: {thread_to_post['thread_id']}")
        x_client = TwitterClient()
        x_client.post_tweet_thread(thread_to_post['tweets'])

        update_last_posted_thread_id(thread_to_post['thread_id'])

        print("Bot run completed.")

    except Exception as e:
        print(f"An unexpected error occurred during bot execution: {e}")
        raise

if __name__ == "__main__":
    run_bot()
