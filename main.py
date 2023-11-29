import os
import re
import feedparser
from litellm import completion
import random
import tweepy
import schedule

# Assuming dotenv is needed, we can uncomment these lines
# from dotenv import load_dotenv
# load_dotenv()

class TwitterClient:
    def __init__(self, consumer_key, consumer_secret, access_token, access_token_secret):
        self.client = tweepy.Client(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )

    def tweet(self, text):
        try:
            self.client.create_tweet(text=text)
            print("Tweet successfully posted!")
        except tweepy.TweepyException as e:
            print(f"An error occurred: {e}")

def extract_text_without_html(summary):
    return re.sub('<[^<]+?>', '', summary)

def generate_response(prompt, entry_text):
    response = completion(model="gpt-3.5-turbo",
                          messages=[{
                              "content": prompt,
                              "role": "system"
                          }, {
                              "content": entry_text,
                              "role": "user"
                          }])
    return response['choices'][0]['message']['content']

def select_random_prompt():
    prompts = [
        "使用台灣作家瓊瑤的寫作風格重寫輸入的字句，必須在140字元以內!",
        "使用作家金庸的寫作風格重寫輸入的字句，必須在140字元以內!",
        "使用文言文重寫輸入的字句，必須在140字元以內!"
    ]
    return random.choice(prompts)

def main():
    twitter_api_key = os.environ['TWITTER_API_KEY']
    twitter_api_secret = os.environ['TWITTER_API_SECRET']
    twitter_access_token = os.environ['TWITTER_ACCESS_TOKEN']
    twitter_access_secret = os.environ['TWITTER_ACCESS_SECRET']

    twitter_client = TwitterClient(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret)

    selected_prompt = select_random_prompt()

    rss_feed_url = 'https://www.info.gov.hk/gia/rss/general_zh.xml'
    feed = feedparser.parse(rss_feed_url)

    if feed.entries:
        first_entry_title = extract_text_without_html(feed.entries[0].title)

        openai_api_key = os.environ['OPENAI_API_KEY']
        response_text = generate_response(selected_prompt, first_entry_title)

        if response_text:
            tweet_text = first_entry_title + "\n\n" + response_text + "\n\n" + "#中文 #文學"
            twitter_client.tweet(tweet_text)
            print(tweet_text)

if __name__ == "__main__":
  main()