import os
import re
import feedparser
import tweepy
from litellm import completion

# Move dotenv import here if needed
# from dotenv import load_dotenv
# load_dotenv()

def tweet_content(summary_text):
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler('CONSUMER_KEY', 'CONSUMER_SECRET')
    auth.set_access_token('ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET')

    # Create API object
    api = tweepy.API(auth)

    # Post a tweet
    try:
        api.update_status(summary_text)
        print("Tweet successfully posted!")
    except tweepy.TweepError as e:
        print(f"An error occurred: {e}")

def response_output(response):
    print(response['choices'][0]['message']['content'])

url = 'https://www.info.gov.hk/gia/rss/general_zh.xml'
feed = feedparser.parse(url)

if feed.entries:
    first_summary_text = re.sub('<[^<]+?>', '', feed.entries[0].title)  # Remove HTML tags

my_secret = os.environ['OPENAI_API_KEY']
response = completion(model="gpt-3.5-turbo",
                      messages=[{
                          "content": "使用台灣作家瓊瑤的寫作風格重寫及拓展輸入的字句，輸出必須限制在140字元以內",
                          "role": "system"
                      }, {
                          "content": first_summary_text,
                          "role": "user"
                      }])

# Output the AI-generated response
response_output(response)

# Tweet the original summary text
if 'first_summary_text' in locals():
    tweet_content(first_summary_text)