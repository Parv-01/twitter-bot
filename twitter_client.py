import tweepy
import os
import time

class TwitterClient:

    def __init__(self):
        try:
            self.bearer_token = os.environ.get("X_BEARER_TOKEN")
            self.api_key = os.environ.get("X_API_KEY")
            self.api_secret = os.environ.get("X_API_SECRET")
            self.access_token = os.environ.get("X_ACCESS_TOKEN")
            self.access_secret = os.environ.get("X_ACCESS_SECRET")
            self.client_id = os.environ.get("X_CLIENT_ID")
            self.client_secret = os.environ.get("X_CLIENT_SECRET")

            if not all([self.bearer_token, self.api_key, self.api_secret, self.access_token, self.access_secret,
                        self.client_id, self.client_secret]):
                raise ValueError("Missing one or more Twitter API credentials.")

            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret
            )

        except ValueError as e:
            raise Exception(f"Failed to initialize Twitter client due to missing credentials: {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred during Twitter client initialization: {e}")

    def post_tweet_thread(self, tweets):
        if not tweets:
            print("No tweets to post.")
            return
        last_tweet_id = None
        for i, tweet_text in enumerate(tweets):
            try:
                if i == 0:
                    response = self.client.create_tweet(text=tweet_text)
                else:
                    response = self.client.create_tweet(text=tweet_text, in_reply_to_tweet_id=last_tweet_id)

                last_tweet_id = response.data['id']
                print(f"Posted tweet {i + 1} with ID: {last_tweet_id}")

                if i < len(tweets) - 1:
                    print("Waiting 5 seconds before posting the next tweet...")
                    time.sleep(5)

            except tweepy.TweepyException as e:
                print(f"Error posting tweet {i + 1}: {e.response.text}")
                raise
            except Exception as e:
                print(f"An unexpected error occurred while posting tweet {i + 1}: {e}")
                raise
