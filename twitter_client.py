import tweepy
import os
import time

class TwitterClient:
    def __init__(self):
        try:
            self.bearer_token = os.environ["X_BEARER_TOKEN"]
            self.api_key = os.environ["X_API_KEY"]
            self.api_secret = os.environ["X_API_SECRET"]
            self.access_token = os.environ["X_ACCESS_TOKEN"]
            self.access_secret = os.environ["X_ACCESS_SECRET"]

            self.client = tweepy.Client(
                bearer_token=self.bearer_token,
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_secret
            )

        except KeyError as e:
            raise Exception(f"❌ Missing environment variable: {e}")
        except Exception as e:
            raise Exception(f"💥 Failed to initialize Twitter client: {e}")

    def post_tweet_thread(self, tweets):
        """Post a list of tweets as a thread."""
        if not tweets:
            print("⚠️ No tweets to post.")
            return

        last_tweet_id = None
        for i, tweet_text in enumerate(tweets):
            try:
                if i == 0:
                    response = self.client.create_tweet(text=tweet_text)
                else:
                    response = self.client.create_tweet(
                        text=tweet_text,
                        in_reply_to_tweet_id=last_tweet_id
                    )

                last_tweet_id = response.data["id"]
                print(f"✅ Posted tweet {i + 1}/{len(tweets)}: ID={last_tweet_id}")

                if i < len(tweets) - 1:
                    time.sleep(5)

            except tweepy.TweepyException as e:
                print(f"💥 Error posting tweet {i + 1}: {getattr(e, 'response', {}).text}")
                raise
            except Exception as e:
                print(f"💥 Unexpected error posting tweet {i + 1}: {e}")
                raise
