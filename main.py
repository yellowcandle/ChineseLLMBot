import os
import re
import feedparser
from litellm import completion
import random
import tweepy
# schedule is imported but never used; you might want to remove it if it's not needed later on

# Helper function to split text into tweet-sized segments
def split_into_tweets(text, max_length=280):
    words = text.split()
    tweets = []
    current_tweet = ''
    for word in words:
        if len(current_tweet) + len(word) + 1 > max_length:
            tweets.append(current_tweet)
            current_tweet = word
        else:
            current_tweet += (' ' + word) if current_tweet else word
    if current_tweet:
        tweets.append(current_tweet)
    return tweets

class TwitterClient:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

    def tweet(self, text, in_reply_to_tweet_id=None):
        # Checking if 'in_reply_to_tweet_id' is not None to decide on first tweet or reply
        method = self.client.create_tweet if in_reply_to_tweet_id is None else self.client.reply
        try:
            response = method(text=text, in_reply_to_tweet_id=in_reply_to_tweet_id)
            print("Tweet successfully posted!")
            return response
        except tweepy.TweepyException as e:
            print(f"An error occurred: {e}")

def extract_text_without_html(summary):
    # Using regular expression to remove HTML tags
    return re.sub('<[^<]+?>', '', summary)

def generate_response(prompt, entry_text):
    # Calling the OpenAI API to generate a response based on the text format provided by a random prompt
    response = completion(model="gpt-3.5-turbo",
                          messages=[{
                              "role": "system",
                              "content": prompt
                          }, {
                              "role": "user",
                              "content": entry_text
                          }])
    return response['choices'][0]['message']['content']

def select_random_prompt():
    prompts = [
        "使用台灣作家瓊瑤的寫作風格重寫輸入的字句",
        "使用作家金庸的寫作風格重寫輸入的字句",
        "使用文言文重寫輸入的字句"
    ]
    return random.choice(prompts)

def main():
    twitter_api_key = os.environ.get('TWITTER_API_KEY')
    twitter_api_secret = os.environ.get('TWITTER_API_SECRET')
    twitter_access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    twitter_access_secret = os.environ.get('TWITTER_ACCESS_SECRET')

    twitter_client = TwitterClient(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret)

    selected_prompt = select_random_prompt()

    rss_feed_url = 'https://www.info.gov.hk/gia/rss/general_zh.xml'
    feed = feedparser.parse(rss_feed_url)

    response_text = ''
    if feed.entries:
        first_entry_title = extract_text_without_html(feed.entries[0].title)

        openai_api_key = os.environ.get('OPENAI_API_KEY')  # Ensure that the api key is used when calling the API
        response_text = generate_response(selected_prompt, first_entry_title)

    if response_text:
        suffix = "#中文 #文學"
        tweet_text = f"{first_entry_title}\n\n{response_text}"
        tweets = split_into_tweets(tweet_text, max_length=180 - len(suffix) - 1)

        conversation_id = None
        for tweet in tweets:
            full_tweet = f"{tweet}\n\n{suffix}" if tweet == tweets[-1] else tweet
            print(f"{len(full_tweet)} chars")

            if conversation_id is None:
                response = twitter_client.tweet(full_tweet)
                conversation_id = response.data['id'] if response else None
            else:
                twitter_client.tweet(full_tweet, in_reply_to_tweet_id=conversation_id)

            print(full_tweet)

if __name__ == "__main__":
    main()