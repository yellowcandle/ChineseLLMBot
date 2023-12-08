import os
import re
import feedparser
from litellm import completion
import random
import tweepy

# Helper function to split text into tweet-sized segments
def split_into_tweets(text, max_length=280):
    tweets = []
    while len(text) > max_length:
        # Find the last space within the max_length
        space_index = text.rfind(' ', 0, max_length)
        # If no space is found, hard break at max_length
        if space_index == -1:
            space_index = max_length
        # Split at space_index
        tweets.append(text[:space_index])
        text = text[space_index:].lstrip()  # Remove leading whitespace for the new tweet
    tweets.append(text)  # Add the last chunk of text
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
        try:
            if in_reply_to_tweet_id is None:
                response = self.client.create_tweet(text=text)
            else:
                response = self.client.create_tweet(text=text, in_reply_to_tweet_id=in_reply_to_tweet_id)
            print("Tweet successfully posted!")
            return response
        except tweepy.TweepyException as e:
            print(f"An error occurred: {e}")

def extract_text_without_html(summary):
    # Using regular expression to remove HTML tags
    return re.sub('<[^<]+?>', '', summary)

def generate_response(prompt, entry_text):
    # Calling the OpenAI API to generate a response based on the text format provided by a random prompt
    response = completion(model="perplexity/pplx-70b-online",
                          messages=[{
                              "role": "system",
                              "content": prompt
                          }, {
                              "role": "user",
                              "content": entry_text
                          }])
    return response['choices'][0]['message']['content']

def select_prompt_in_sequence(index):
    prompts = [
        "你是香港人，使用作家瓊瑤的寫作風格重寫輸入的字句為一首詩",
        "你是香港人，使用作家金庸的寫作風格重寫輸入的字句為一首詩",
        "你是香港人，使用古典文言重寫輸入的字句為一首詩"
    ]
    return prompts[index % len(prompts)]

def main():
    twitter_api_key = os.environ.get('TWITTER_API_KEY')
    twitter_api_secret = os.environ.get('TWITTER_API_SECRET')
    twitter_access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
    twitter_access_secret = os.environ.get('TWITTER_ACCESS_SECRET')

    twitter_client = TwitterClient(twitter_api_key, twitter_api_secret, twitter_access_token, twitter_access_secret)
    index = 0
    selected_prompt = select_prompt_in_sequence(index)

    rss_feed_url = 'https://www.info.gov.hk/gia/rss/general_zh.xml'
    feed = feedparser.parse(rss_feed_url)

    response_text = ''
    if feed.entries:
        first_entry_title = extract_text_without_html(feed.entries[0].title)

        openai_api_key = os.environ.get('OPENAI_API_KEY')  # Ensure that the api key is used when calling the API
        perplexity_api_key = os.environ.get('PERPLEXITYAI_API_KEY')
              # Calling the OpenAI API to generate a response based on the text format provided by a random prompt
        response_text = generate_response(selected_prompt, first_entry_title)

    if response_text:
        suffix = "#中文 #文學"
        tweet_text = f"{first_entry_title}\n\n{response_text}"
        tweets = split_into_tweets(tweet_text, max_length=140 - len(suffix) - 1)

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